from aiogram import Bot, Dispatcher, types, executor
import aiohttp
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from transliterate import translit
from utils.BI_extractor import create_bot_data_structure
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage


API_TOKEN = '6497022427:AAHZS8FfFz7stafFCNmoevoIyGGL2hU1YAA'
RASA_WEBHOOK_URL = 'http://rasa:5005/webhooks/rest/webhook'
MODEL_WEBHOOK_URL = 'http://ml_model:5000/predict'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)
ML_DATA = create_bot_data_structure('utils/BI_DATA.xlsx')


def transliterate_text(text):
    return translit(text, 'ru', reversed=True)


class StateGroup(StatesGroup):

    inlineChoice = State()
    register_answer = State()


async def generate_buttons(fg_name: str):
    """ Генерация кнопок на основе функциональной группы """
    group_data = ML_DATA.get(fg_name.lower(), None)
    markup = InlineKeyboardMarkup()
    if group_data:
        if all(map(lambda x: not isinstance(x, str), group_data['варианты_выбора'])):
            return None
        for option in group_data['варианты_выбора']:
            if isinstance(option, str):
                callback_data = '_' + transliterate_text(option if option != "Другое" else "other_action")
                markup.add(InlineKeyboardButton(text=option, callback_data=callback_data))
    else:
        # Возвращаем кнопку "Другое", если ФГ не найдена
        markup.add(InlineKeyboardButton(text="Другое", callback_data="other"))

    return markup


async def send_to_rasa(sender, message):
    async with aiohttp.ClientSession() as session:
        payload = {
            "sender": sender,
            "message": message
        }
        async with session.post(RASA_WEBHOOK_URL, json=payload) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None


async def send_to_model(message: str):
    async with aiohttp.ClientSession() as session:
        payload = {
            "text": message
        }
        async with session.post(MODEL_WEBHOOK_URL, json=payload) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None


async def handle_rasa_response(response, message):
    if len(response) == 0 or response[0]['text'] == 'NOT SURE' or not response:
        return await send_to_model(message)
    return response


def reverse_transliterate_text(text):
    return translit(text, 'ru', reversed=False)


@dp.message_handler(commands=['start', 'help'], state='*')
async def send_welcome(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("Привет! Я бот, который что-то делает")


@dp.callback_query_handler(lambda c: c.data.startswith('_'), state=StateGroup.inlineChoice)
async def callback_query_handler(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == '_other_action':
        await callback_query.message.answer("Специалист скоро свяжется с вами для уточнения деталей.",
                                            reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        return

    state_data = await state.get_data()
    fg_name = state_data.get('prediction')

    group_data = ML_DATA.get(fg_name, None)
    if group_data:
        options = group_data['варианты_выбора']
        responses = group_data['ответы']
        choice_index = list(map(lambda x: x.lower(), options)).index(reverse_transliterate_text(callback_query.data[1:]).lower())
        response_text = responses[choice_index]
        possible_link = group_data['доп_данные'][choice_index]

        if possible_link is not None and isinstance(possible_link, str) and possible_link != "nan":
            response_text += f"\n\n{possible_link}"

        await callback_query.message.delete()
        await callback_query.message.answer(response_text)
    else:
        await callback_query.message.answer("Выбранная опция не найдена.", parse_mode='markdown')

    await bot.answer_callback_query(callback_query.id)
    await state.finish()
    await StateGroup.register_answer.set()


@dp.message_handler(state=StateGroup.register_answer)
async def register_answer(message: types.Message, state: FSMContext):
    await message.answer("Благодарим вас за информацию!")
    await state.finish()

@dp.message_handler()
async def echo(message: types.Message, state: FSMContext):
    sender = f"{message.from_user.first_name}, {message.from_user.last_name}"
    response = await send_to_rasa(sender, message.text)
    print(message.text, message.from_user.first_name)
    if response or len(response) == 0:
        response = await handle_rasa_response(response, message.text)
        if isinstance(response, list):
            return await message.answer(response[0]['text'], parse_mode='markdown')
        if response is None:
            return await message.answer("Произошла ошибка при обработке сообщения.")
        prediction = response['prediction'].replace('ФГ ', '')
        response_message = f'*Отлично*, выберите, что вам подходит из списка ниже: {prediction}'
        await state.update_data(prediction=prediction.lower())
        buttons = await generate_buttons(prediction)
        if buttons is None:
            response_message = f'Специалист скоро свяжется с вами для уточнения деталей. {prediction}'
        await StateGroup.inlineChoice.set()
        await message.answer(response_message, parse_mode='markdown', reply_markup=buttons)
    else:
        await message.answer(f"Произошла ошибка при обработке сообщения. Повторите попытку позже. {response}")
        await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
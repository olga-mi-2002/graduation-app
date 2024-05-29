from datetime import datetime
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted
import random


class ActionGreet(Action):
    def name(self):
        return "action_greet"

    def run(self, dispatcher, tracker, domain):
        now = datetime.now()
        # +3 GMT CONSTANT (MOSCOW)
        current_hour = now.hour + 3

        morning_greetings = ["Доброе утро! Рад вас видеть.", "Здравствуйте, прекрасное утро для новых начинаний!"]
        afternoon_greetings = ["Добрый день! Чем могу помочь?", "Рад вас видеть, прекрасный день для продуктивной работы!"]
        evening_greetings = ["Добрый вечер! Как прошёл ваш день?", "Добрый вечер! Надеюсь, вы в хорошем настроении."]

        if current_hour < 12:
            greeting = random.choice(morning_greetings)
        elif current_hour < 18:
            greeting = random.choice(afternoon_greetings)
        else:
            greeting = random.choice(evening_greetings)

        dispatcher.utter_message(text=greeting)
        return []


class ActionExplainBusinessIncubator(Action):
    def name(self):
        return "utter_explain_business_incubator"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="Бизнес-инкубатор — это организация, помогающая начинающим компаниям развиваться.")
        return []


class ActionDefaultFallback(Action):
    def name(self):
        return "action_default_fallback"

    def run(self, dispatcher, tracker, domain):
        # Сообщение пользователю
        dispatcher.utter_message(text="NOT SURE")
        # Откат последнего сообщения пользователя
        return [UserUtteranceReverted()]

from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

model = joblib.load('random_forest_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

# Загрузка модели и векторизатора
# role_model = joblib.load('role_decision_tree_model.pkl')
# role_vectorizer = joblib.load('role_vectorizer.pkl')
#
#
# @app.route('/role-predict', methods=['POST'])
# def role_predict():
#     json_data = request.get_json(force=True)
#     text = json_data['text']
#     text_vectorized = vectorizer.transform([text])
#     prediction = model.predict(text_vectorized)
#
#     return jsonify({'prediction': prediction[0]})


@app.route('/predict', methods=['POST'])
def predict():
    json_data = request.get_json(force=True)
    text = json_data['text']
    text_vectorized = vectorizer.transform([text]).toarray()
    prediction = model.predict(text_vectorized)

    # Проверка поддержки predict_proba и правильный доступ к вероятностям
    if hasattr(model, "predict_proba"):
        prediction_proba = model.predict_proba(text_vectorized)
        # Проверяем, что prediction[0] - это индекс
        class_index = model.classes_.tolist().index(prediction[0])
        confidence = prediction_proba[0][class_index]
    else:
        confidence = "Model does not support probability estimation"

    return jsonify({'prediction': prediction[0], 'confidence': confidence})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


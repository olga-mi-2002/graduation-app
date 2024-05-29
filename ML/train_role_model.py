import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.tree import DecisionTreeClassifier
import joblib

# Загрузка данных
data = pd.read_excel('роли для кода.xlsx')

# Очистка данных
data.dropna(subset=['Обращение', 'Роль'], inplace=True)

# Векторизация текстовых данных
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(data['Обращение'])
y = data['Роль']

# Разделение данных на обучающий и тестовый наборы
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Создание и обучение модели
model = DecisionTreeClassifier(random_state=42)
model.fit(X_train, y_train)

# Сохранение модели и векторизатора
joblib.dump(model, 'roles_decision_tree_model.pkl')
joblib.dump(vectorizer, 'roles_vectorizer.pkl')

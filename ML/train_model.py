import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
import joblib

data = pd.read_excel('Данные БИ для кода.xlsx')

data.dropna(subset=['Обращение', 'ФГ'], inplace=True)

data = data[~data['Обращение'].str.contains("тест", case=False, na=False)]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(data['Обращение'])
y = data['ФГ']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

joblib.dump(model, 'random_forest_model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')

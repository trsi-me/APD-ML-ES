import joblib
import os
from ml.preprocessor import preprocess_text

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), 'vectorizer.pkl')

model = None
vectorizer = None


def load_model():
    global model, vectorizer
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)


def predict_email(text):
    if model is None:
        load_model()
    cleaned = preprocess_text(text)
    vector = vectorizer.transform([cleaned])
    prediction = model.predict(vector)[0]
    probability = model.predict_proba(vector)[0]
    confidence = round(float(max(probability)) * 100, 2)
    label = 'تصيد احتيالي' if prediction == 1 else 'بريد شرعي'
    is_phishing = bool(prediction == 1)
    return {
        'label': label,
        'is_phishing': is_phishing,
        'confidence': confidence,
        'raw_prediction': int(prediction)
    }

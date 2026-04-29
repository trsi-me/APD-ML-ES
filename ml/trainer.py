import os
import urllib.request
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from ml.preprocessor import preprocess_text
from ml.corpus_builtins import expanded_rows

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DATA_CSV = os.path.join(DATA_DIR, 'phishing_dataset.csv')
DATA_REMOTE_CSV = os.path.join(DATA_DIR, 'phishing_external.csv')
MODEL_OUT = os.path.join(os.path.dirname(__file__), 'model.pkl')
VECTORIZER_OUT = os.path.join(os.path.dirname(__file__), 'vectorizer.pkl')

URL_CANDIDATES = [
    'https://raw.githubusercontent.com/shreshtha12/Email-Authenticity-Detection/master/spam.csv',
    'https://raw.githubusercontent.com/niranjan-ramesh/Email-Spam-Filter/main/spam.csv',
]


def _try_download_one(url, dest):
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'APD-ML-ES-Trainer/1.0'},
        )
        with urllib.request.urlopen(req, timeout=45) as r:
            data = r.read()
        if len(data) < 5000:
            return False
        with open(dest, 'wb') as f:
            f.write(data)
        return True
    except Exception:
        return False


def _load_external_dataframe():
    if not os.path.isfile(DATA_REMOTE_CSV) or os.path.getsize(DATA_REMOTE_CSV) < 1000:
        for u in URL_CANDIDATES:
            if _try_download_one(u, DATA_REMOTE_CSV):
                break
    if not os.path.isfile(DATA_REMOTE_CSV):
        return None
    try:
        df = pd.read_csv(DATA_REMOTE_CSV, encoding='utf-8', on_bad_lines='skip')
    except TypeError:
        df = pd.read_csv(DATA_REMOTE_CSV, encoding='utf-8', error_bad_lines=False, warn_bad_lines=False)
    except Exception:
        try:
            df = pd.read_csv(DATA_REMOTE_CSV, encoding='latin-1', on_bad_lines='skip')
        except Exception:
            return None
    if df is None or len(df) < 50:
        return None
    cols = [c.lower() for c in df.columns]
    if 'v1' in cols and 'v2' in cols:
        text_col, label_col = 'v2', 'v1'
    elif 'text' in cols and 'label' in cols:
        text_col, label_col = 'text', 'label'
    elif 'message' in cols and 'class' in cols:
        text_col, label_col = 'message', 'class'
    else:
        c0, c1 = df.columns[0], df.columns[1]
        text_col, label_col = c1, c0
    out = []
    for _, row in df.iterrows():
        try:
            t = str(row[text_col])
            y = row[label_col]
            if isinstance(y, str):
                yl = 1 if y.lower() in ('spam', 'phishing', '1', 'true', 'phish', '1.0') else 0
            else:
                yl = 1 if int(float(y)) == 1 else 0
            if t and len(t) > 20:
                out.append({'text': t, 'label': yl})
        except Exception:
            continue
    if len(out) < 100:
        return None
    return pd.DataFrame(out)


def ensure_dataset_file():
    if os.path.isfile(DATA_CSV) and os.path.getsize(DATA_CSV) > 0:
        df0 = pd.read_csv(DATA_CSV)
        if len(df0) >= 1000 and 'text' in df0.columns and 'label' in df0.columns:
            return
    os.makedirs(DATA_DIR, exist_ok=True)
    ext = _load_external_dataframe()
    rows = list(expanded_rows())
    if ext is not None and len(ext) > 0:
        for _, r in ext.iterrows():
            rows.append((str(r['text']), int(r['label'])))
    df = pd.DataFrame(rows, columns=['text', 'label'])
    if len(df) < 200:
        raise ValueError('فشل بناء بيانات التدريب الكافية')
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df.to_csv(DATA_CSV, index=False, encoding='utf-8')


def train_model():
    ensure_dataset_file()
    df = pd.read_csv(DATA_CSV)
    df['text'] = df['text'].astype(str)
    df['processed'] = df['text'].apply(preprocess_text)
    try:
        x_train, x_test, y_train, y_test = train_test_split(
            df['processed'], df['label'], test_size=0.2, random_state=42, stratify=df['label']
        )
    except ValueError:
        x_train, x_test, y_train, y_test = train_test_split(
            df['processed'], df['label'], test_size=0.2, random_state=42
        )
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    x_train_vec = vectorizer.fit_transform(x_train)
    x_test_vec = vectorizer.transform(x_test)
    clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    clf.fit(x_train_vec, y_train)
    y_pred = clf.predict(x_test_vec)
    acc = accuracy_score(y_test, y_pred)
    print(f'دقة النموذج (Accuracy): {acc:.4f}')
    print('تقرير التصنيف:')
    print(classification_report(y_test, y_pred, target_names=['شرعي', 'تصيد']))
    joblib.dump(clf, MODEL_OUT)
    joblib.dump(vectorizer, VECTORIZER_OUT)
    print('تم حفظ النموذج والمحوّل بنجاح.')

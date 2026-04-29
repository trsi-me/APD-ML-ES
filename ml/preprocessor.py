import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))


def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'http\S+|www\S+', ' رابط ', text)
    text = re.sub(r'\S+@\S+', ' بريد ', text)
    text = re.sub(r'\d+', ' رقم ', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = text.split()
    tokens = [stemmer.stem(w) for w in tokens if w not in stop_words and len(w) > 2]
    return ' '.join(tokens)

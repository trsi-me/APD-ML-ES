#!/usr/bin/env bash
set -e

echo "==> تثبيت المكتبات..."
pip install -r requirements.txt

echo "==> تحميل بيانات NLTK..."
python -c "import nltk; nltk.download('stopwords', quiet=True); nltk.download('punkt', quiet=True)"

echo "==> تدريب نموذج ML..."
python -c "from ml.trainer import train_model; train_model()"

echo "==> اكتمل البناء."

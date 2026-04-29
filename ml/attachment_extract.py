import io
import re

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

MAX_PDF_PAGES = 8
MAX_TEXT_LEN = 120_000
MAX_IMAGE_DIM = 4000


def _trunc(s, limit=MAX_TEXT_LEN):
    s = s or ''
    if len(s) > limit:
        return s[:limit] + '\n[... تم اقتصار النص للتحليل ...]'
    return s


def text_from_bytes(data, filename, mime=None):
    name = (filename or '').lower()
    if not data:
        return ''
    ext = name.rsplit('.', 1)[-1] if '.' in name else ''
    if ext in ('txt', 'csv', 'log', 'md', 'eml', 'ics'):
        try:
            t = data.decode('utf-8', errors='replace')
        except Exception:
            t = str(data, errors='replace')
        return _trunc(t)
    if ext in ('html', 'htm') and BeautifulSoup:
        try:
            raw = data.decode('utf-8', errors='replace')
        except Exception:
            raw = str(data, errors='replace')
        s = BeautifulSoup(raw, 'html.parser').get_text(' ', strip=True)
        return _trunc(s)
    if ext == 'pdf' and PdfReader:
        try:
            r = PdfReader(io.BytesIO(data))
            out = []
            for i, p in enumerate(r.pages[:MAX_PDF_PAGES]):
                t = p.extract_text() or ''
                out.append(t)
            return _trunc('\n'.join(out))
        except Exception:
            return f'[PDF: {filename} — تعذر استخراج النص من الملف.]'
    if ext in ('png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp', 'tiff') and Image:
        try:
            im = Image.open(io.BytesIO(data))
            w, h = im.size
            if w > MAX_IMAGE_DIM or h > MAX_IMAGE_DIM:
                return f'[صورة: {filename} — أبعاد كبيرة، تم تخطي التحليل التفصيلي.]'
            if pytesseract is not None:
                try:
                    txt = pytesseract.image_to_string(im, lang='eng+ara', timeout=20)
                except Exception:
                    txt = pytesseract.image_to_string(im, timeout=20)
                if (txt or '').strip():
                    return _trunc('صورة: ' + filename + '\n' + txt)
            return f'[صورة: {filename} — {w}x{h} بكسل. اربط tesseract وpytesseract لاستخراج النص تلقائياً.]'
        except Exception:
            return f'[صورة: {filename} — تعذر فتح الملف.]'
    return f'[مرفق: {filename} — نوع غير مدعوم لاستخراج نص.]'


def merge_email_and_files(email_text, file_storage_list):
    parts = [email_text or '']
    meta = []
    for fs in file_storage_list or []:
        if not fs or not fs.filename:
            continue
        raw = fs.read()
        if not raw:
            continue
        if len(raw) > 6 * 1024 * 1024:
            meta.append(f'{fs.filename} (مرفوع — تخطي: حجم كبير جداً)')
            continue
        block = text_from_bytes(raw, fs.filename, getattr(fs, 'mimetype', None))
        parts.append(f'\n--- [مرفق: {fs.filename}] ---\n' + block)
        meta.append(fs.filename)
    return _trunc('\n'.join(p for p in parts if p)), meta

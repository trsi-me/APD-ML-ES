import imaplib
import email
import email.header
import email.utils
from email import policy
from html import unescape
import re
from types import SimpleNamespace

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

from ml.attachment_extract import text_from_bytes, MAX_TEXT_LEN


def _decode_header(s):
    if not s:
        return ''
    try:
        parts = email.header.decode_header(s)
        out = []
        for part, enc in parts:
            if isinstance(part, bytes):
                out.append(part.decode(enc or 'utf-8', errors='replace'))
            else:
                out.append(part)
        return ''.join(out)
    except Exception:
        return str(s or '')


def _strip_html(s):
    if not s:
        return ''
    if BeautifulSoup:
        return BeautifulSoup(s, 'html.parser').get_text(' ', strip=True)
    t = re.sub(r'<script[^>]*>.*?</script>', ' ', s, flags=re.S | re.I)
    t = re.sub(r'<style[^>]*>.*?</style>', ' ', t, flags=re.S | re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    return unescape(t)


def _message_text(msg):
    bodies = []
    if msg.is_multipart():
        for part in msg.walk():
            ct = (part.get_content_type() or '').lower()
            if ct == 'text/plain':
                pl = part.get_payload(decode=True) or b''
                try:
                    bodies.append(pl.decode(part.get_content_charset() or 'utf-8', errors='replace'))
                except Exception:
                    bodies.append(str(pl, errors='replace'))
            elif ct == 'text/html':
                pl = part.get_payload(decode=True) or b''
                try:
                    h = pl.decode(part.get_content_charset() or 'utf-8', errors='replace')
                except Exception:
                    h = str(pl, errors='replace')
                bodies.append(_strip_html(h))
    else:
        pl = msg.get_payload(decode=True) or b''
        if isinstance(pl, str):
            bodies.append(pl)
        else:
            try:
                bodies.append(
                    pl.decode(msg.get_content_charset() or 'utf-8', errors='replace')
                )
            except Exception:
                bodies.append(str(pl, errors='replace'))
    return '\n'.join(bodies).strip()[: 80_000]


def _attachments_excerpt(msg, max_attach=5):
    parts_out = []
    n = 0
    for part in msg.walk():
        if n >= max_attach:
            break
        if part.get_content_maintype() == 'multipart':
            continue
        filename = part.get_filename()
        if not filename:
            continue
        filename = _decode_header(filename)
        data = part.get_payload(decode=True)
        if not data:
            continue
        n += 1
        block = text_from_bytes(data, filename, part.get_content_type())
        parts_out.append(f'\n--- [مرفق: {filename}] ---\n' + (block or ''))
    return ''.join(parts_out)[: 60_000]


def build_imap_combined_text(msg):
    subj = _decode_header(msg.get('Subject', '')) or ''
    frm = _decode_header(msg.get('From', '')) or ''
    to = _decode_header(msg.get('To', '')) or ''
    main = f'Subject: {subj}\nFrom: {frm}\nTo: {to}\n\n'
    main += _message_text(msg) or ''
    att = _attachments_excerpt(msg)
    full = (main + att).strip()
    if len(full) > MAX_TEXT_LEN:
        full = full[:MAX_TEXT_LEN] + '\n[...]'
    return full


def fetch_inbox_analyze(
    host,
    port,
    user,
    password,
    use_ssl,
    limit,
    folder=b'INBOX',
):
    limit = min(max(1, int(limit or 10)), 30)
    if use_ssl:
        m = imaplib.IMAP4_SSL(host, int(port or 993))
    else:
        m = imaplib.IMAP4(host, int(port or 143))
    m.login(user, password)
    m.select(folder)
    typ, data = m.search(None, 'ALL')
    if typ != 'OK' or not data or not data[0]:
        m.logout()
        return []
    ids = data[0].split()[-limit:]
    out = []
    for mid in ids:
        typ, dat = m.fetch(mid, '(RFC822)')
        if typ != 'OK' or not dat or not dat[0]:
            continue
        raw = dat[0][1] if len(dat[0]) > 1 else dat[0]
        if not isinstance(raw, (bytes, bytearray)):
            continue
        msg = email.message_from_bytes(bytes(raw), policy=policy.default)
        combined = build_imap_combined_text(msg)
        prev = (combined or '')[:120] + '…' if len(combined or '') > 120 else (combined or '')
        subj = _decode_header(msg.get('Subject', '')) or ''
        out.append(
            {
                'subject': subj,
                'from_addr': _decode_header(msg.get('From', '')) or '',
                'preview': prev,
                'combined_text': combined,
            }
        )
    m.logout()
    return out

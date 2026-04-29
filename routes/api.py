import imaplib
from flask import Blueprint, request, jsonify, session
from database.db import get_connection
from database.seed import recompute_statistics
from ml.predictor import predict_email
from ml.attachment_extract import merge_email_and_files
from services.imap_fetch import fetch_inbox_analyze

api_bp = Blueprint('api', __name__)

MAX_COMBINED = 100_000


def _store_analysis(full_text, res, user_id=None):
    preview = (full_text[:200] + '…') if len(full_text) > 200 else full_text
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        '''
        INSERT INTO analyses (email_text, email_preview, result, is_phishing, confidence, analyzed_at, user_id)
        VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'), ?)
        ''',
        (full_text, preview, res['label'], 1 if res['is_phishing'] else 0, res['confidence'], user_id),
    )
    new_id = cur.lastrowid
    cur.execute('SELECT analyzed_at FROM analyses WHERE id = ?', (new_id,))
    at_row = cur.fetchone()
    analyzed_at = at_row['analyzed_at'] if at_row else ''
    conn.commit()
    conn.close()
    recompute_statistics()
    return analyzed_at


@api_bp.route('/analyze', methods=['POST'])
def analyze():
    full_text = ''
    meta = []
    if request.content_type and 'multipart/form-data' in request.content_type:
        body = (request.form.get('email_text') or '').strip()
        files = request.files.getlist('files') or []
        if len(files) > 10:
            return jsonify({'success': False, 'message': 'يُسمح بعشرة مرفقات كحد أقصى.'}), 400
        full_text, meta = merge_email_and_files(body, files)
    else:
        data = request.get_json(silent=True) or {}
        full_text = (data.get('email_text') or '').strip()
    if not full_text:
        return jsonify({'success': False, 'message': 'نص التحليل فارغ. الصق نص البريد أو أضف مرفقات.'}), 400
    if len(full_text) <= 10:
        return jsonify(
            {
                'success': False,
                'message': 'النص المدمج (بريد + مرفقات) يجب أن يتجاوز عشرة أحرف.',
            }
        ), 400
    if len(full_text) > MAX_COMBINED:
        full_text = full_text[:MAX_COMBINED]
    res = predict_email(full_text)
    uid = session.get('user_id')
    analyzed_at = _store_analysis(full_text, res, user_id=uid)
    return jsonify(
        {
            'success': True,
            'result': {
                'label': res['label'],
                'is_phishing': res['is_phishing'],
                'confidence': res['confidence'],
                'analyzed_at': analyzed_at,
            },
            'attachments_parsed': meta,
        }
    )


@api_bp.route('/mail/fetch-analyze', methods=['POST'])
def mail_fetch_analyze():
    if not session.get('user_id'):
        return jsonify(
            {
                'success': False,
                'message': 'سجّل الدخول أولاً ليُحفظ جلب بريدك في سجلك ولوحة التحكم.',
            }
        ), 401
    data = request.get_json(silent=True) or {}
    if not data.get('consent'):
        return jsonify(
            {
                'success': False,
                'message': 'يلزم تفعيل الموافقة على جلب الرسائل وتحليلها محلياً.',
            }
        ), 400
    host = (data.get('host') or '').strip()
    user = (data.get('user') or '').strip()
    password = (data.get('password') or '')
    if not host or not user or not password:
        return jsonify({'success': False, 'message': 'أدخل خادم IMAP، البريد، وكلمة المرور (أو كلمة تطبيق).'}), 400
    port = int(data.get('port') or 993)
    use_ssl = bool(data.get('use_ssl', True))
    try:
        limit = int(data.get('limit') or 12)
    except ValueError:
        limit = 12
    limit = min(max(1, limit), 25)
    try:
        msgs = fetch_inbox_analyze(
            host,
            port,
            user,
            password,
            use_ssl,
            limit,
        )
    except imaplib.IMAP4.error:
        return jsonify(
            {
                'success': False,
                'message': 'فشل الاتصال بخادم البريد. تحقق من الإعدادات وكلمة التطبيق.',
            }
        ), 400
    except Exception:
        return jsonify(
            {
                'success': False,
                'message': 'تعذّر جلب الرسائل. تحقق من الشبكة ومن منفذ IMAP.',
            }
        ), 500
    results = []
    uid = session.get('user_id')
    for m in msgs:
        txt = m.get('combined_text') or ''
        if len(txt) < 15:
            continue
        res = predict_email(txt)
        at = _store_analysis(txt, res, user_id=uid)
        results.append(
            {
                'subject': m.get('subject', '')[:200],
                'from_addr': m.get('from_addr', '')[:200],
                'result': {
                    'label': res['label'],
                    'is_phishing': res['is_phishing'],
                    'confidence': res['confidence'],
                    'analyzed_at': at,
                },
            }
        )
    return jsonify({'success': True, 'count': len(results), 'analyzed': results})


@api_bp.route('/statistics', methods=['GET'])
def get_statistics():
    from routes.main import _get_stats_for_dashboard, _get_stats_for_user

    uid = session.get('user_id')
    stats = _get_stats_for_user(uid) if uid else _get_stats_for_dashboard()
    return jsonify(
        {
            'success': True,
            'stats': stats,
        }
    )


@api_bp.route('/history', methods=['GET'])
def get_history():
    uid = session.get('user_id')
    if not uid:
        return jsonify({'success': False, 'message': 'تسجيل الدخول مطلوب لعرض السجل.', 'analyses': [], 'total': 0}), 401
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        '''
        SELECT id, email_preview, result, is_phishing, confidence, analyzed_at
        FROM analyses
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 100
        ''',
        (int(uid),),
    )
    rows = cur.fetchall()
    conn.close()
    analyses = []
    for r in rows:
        analyses.append(
            {
                'id': r['id'],
                'email_preview': r['email_preview'],
                'result': r['result'],
                'is_phishing': bool(r['is_phishing']),
                'confidence': round(float(r['confidence']), 1) if r['confidence'] is not None else 0.0,
                'analyzed_at': r['analyzed_at'] or '',
            }
        )
    return jsonify({'success': True, 'analyses': analyses, 'total': len(analyses)})


@api_bp.route('/history/<int:analysis_id>', methods=['DELETE'])
def delete_history_item(analysis_id):
    uid = session.get('user_id')
    if not uid:
        return jsonify({'success': False, 'message': 'تسجيل الدخول مطلوب.'}), 401
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM analyses WHERE id = ? AND user_id = ?', (analysis_id, int(uid)))
    n = cur.rowcount
    conn.commit()
    conn.close()
    if n == 0:
        return jsonify({'success': False, 'message': 'السجل غير موجود أو ليس لك.'}), 404
    recompute_statistics()
    return jsonify({'success': True, 'message': 'تم الحذف.'})

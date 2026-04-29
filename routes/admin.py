import os
from functools import wraps
from flask import (
    Blueprint,
    session,
    request,
    render_template,
    redirect,
    url_for,
    jsonify,
)
from config import Config, BASE_DIR
from database.db import get_connection
from database.seed import recompute_statistics

admin_bp = Blueprint('admin', __name__)

MODEL_PKL = os.path.join(BASE_DIR, 'ml', 'model.pkl')
DB_FILE = os.path.join(BASE_DIR, 'data', 'apd_ml_es.db')


def _get_stats():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT total_analyzed, total_phishing, total_legitimate FROM statistics WHERE id = 1')
    row = cur.fetchone()
    conn.close()
    if not row:
        return 0, 0, 0, 0.0, 0.0
    ta = int(row['total_analyzed'] or 0)
    tp = int(row['total_phishing'] or 0)
    tl = int(row['total_legitimate'] or 0)
    if ta <= 0:
        return ta, tp, tl, 0.0, 0.0
    return (
        ta,
        tp,
        tl,
        round(100.0 * tp / ta, 1),
        round(100.0 * tl / ta, 1),
    )


def _list_analyses(limit=500):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        '''
        SELECT a.id, a.email_preview, a.result, a.is_phishing, a.confidence, a.analyzed_at,
               a.user_id, u.email AS user_email, u.full_name AS user_full_name
        FROM analyses a
        LEFT JOIN users u ON u.id = a.user_id
        ORDER BY a.id DESC
        LIMIT ?
        ''',
        (limit,),
    )
    rows = [{k: r[k] for k in r.keys()} for r in cur.fetchall()]
    conn.close()
    return rows


def _count_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) AS c FROM users')
    row = cur.fetchone()
    n = int(row['c'] or 0) if row else 0
    conn.close()
    return n


def _count_analyses_orphan():
    """سجلات بلا user_id (بذر، تحليل قبل تسجيل الدخول، إلخ)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) AS c FROM analyses WHERE user_id IS NULL')
    row = cur.fetchone()
    n = int(row['c'] or 0) if row else 0
    conn.close()
    return n


def _list_users_with_stats():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        '''
        SELECT u.id, u.email, u.full_name, u.phone, u.bio, u.created_at,
               (SELECT COUNT(*) FROM analyses a WHERE a.user_id = u.id) AS analysis_count,
               (SELECT COALESCE(SUM(a.is_phishing), 0) FROM analyses a WHERE a.user_id = u.id) AS phishing_count
        FROM users u
        ORDER BY u.id DESC
        '''
    )
    rows = []
    for r in cur.fetchall():
        total = int(r['analysis_count'] or 0)
        ph = int(r['phishing_count'] or 0)
        rows.append(
            {
                'id': r['id'],
                'email': r['email'] or '',
                'full_name': r['full_name'] or '',
                'phone': r['phone'] or '',
                'bio': (r['bio'] or '')[:200],
                'created_at': r['created_at'] or '',
                'analysis_count': total,
                'phishing_count': ph,
                'legitimate_count': max(0, total - ph),
            }
        )
    conn.close()
    return rows


def admin_required_json(f):
    @wraps(f)
    def inner(*a, **kw):
        if not session.get('adm'):
            return jsonify({'success': False, 'message': 'غير مصرّح.'}), 401
        return f(*a, **kw)
    return inner


def admin_required(f):
    @wraps(f)
    def inner(*a, **kw):
        if not session.get('adm'):
            return redirect(url_for('admin.login'))
        return f(*a, **kw)
    return inner


@admin_bp.route('/')
def root():
    if session.get('adm'):
        return redirect(url_for('admin.panel'))
    return redirect(url_for('admin.login'))


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pwd = (request.form.get('password') or '').strip()
        if pwd == Config.ADMIN_PASSWORD:
            session['adm'] = True
            return redirect(url_for('admin.panel'))
        return render_template('admin/login.html', error='كلمة المرور غير صحيحة')
    if session.get('adm'):
        return redirect(url_for('admin.panel'))
    return render_template('admin/login.html', error=None)


@admin_bp.route('/logout')
def logout():
    session.pop('adm', None)
    return redirect(url_for('admin.login'))


@admin_bp.route('/panel')
@admin_required
def panel():
    ta, tp, tl, pp, pl = _get_stats()
    analyses = _list_analyses(500)
    users = _list_users_with_stats()
    user_n = _count_users()
    orphan_n = _count_analyses_orphan()
    model_ok = os.path.isfile(MODEL_PKL)
    return render_template(
        'admin/panel.html',
        stats={'total': ta, 'phish': tp, 'legit': tl, 'pp': pp, 'pl': pl},
        analyses=analyses,
        users=users,
        user_count=user_n,
        orphan_count=orphan_n,
        model_exists=model_ok,
        db_path=DB_FILE,
    )


@admin_bp.route('/action/recompute', methods=['POST'])
@admin_required_json
def action_recompute():
    recompute_statistics()
    return jsonify({'success': True, 'message': 'تمت إعادة الحساب'})


@admin_bp.route('/action/delete', methods=['POST'])
@admin_required_json
def action_delete():
    data = request.get_json(silent=True) or {}
    try:
        aid = int(data.get('id'))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'معرّف غير صالح.'}), 400
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM analyses WHERE id = ?', (aid,))
    if cur.rowcount < 1:
        conn.close()
        return jsonify({'success': False, 'message': 'السجل غير موجود.'}), 404
    conn.commit()
    conn.close()
    recompute_statistics()
    return jsonify({'success': True, 'message': 'تم الحذف'})


@admin_bp.route('/action/purge', methods=['POST'])
@admin_required_json
def action_purge():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM analyses')
    conn.commit()
    conn.close()
    recompute_statistics()
    return jsonify({'success': True, 'message': 'تم تفريغ السجل'})


@admin_bp.route('/data/refresh', methods=['GET'])
@admin_required_json
def data_refresh():
    ta, tp, tl, pp, pl = _get_stats()
    analyses = _list_analyses(500)
    users = _list_users_with_stats()
    return jsonify(
        {
            'success': True,
            'stats': {'total': ta, 'phish': tp, 'legit': tl, 'pp': pp, 'pl': pl},
            'analyses': analyses,
            'users': users,
            'user_count': _count_users(),
            'orphan_count': _count_analyses_orphan(),
        }
    )


@admin_bp.route('/data/analysis-detail', methods=['GET'])
@admin_required_json
def data_analysis_detail():
    try:
        aid = int(request.args.get('id', ''))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'معرّف غير صالح.'}), 400
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        '''
        SELECT a.id, a.email_text, a.email_preview, a.result, a.is_phishing, a.confidence,
               a.analyzed_at, a.user_id, u.email AS user_email, u.full_name AS user_full_name,
               u.phone AS user_phone
        FROM analyses a
        LEFT JOIN users u ON u.id = a.user_id
        WHERE a.id = ?
        ''',
        (aid,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({'success': False, 'message': 'السجل غير موجود.'}), 404
    r = {k: row[k] for k in row.keys()}
    return jsonify(
        {
            'success': True,
            'analysis': {
                'id': r['id'],
                'email_text': r['email_text'] or '',
                'email_preview': r['email_preview'] or '',
                'result': r['result'] or '',
                'is_phishing': bool(r['is_phishing']),
                'confidence': float(r['confidence'] or 0),
                'analyzed_at': r['analyzed_at'] or '',
                'user_id': r['user_id'],
            },
            'user': {
                'email': r.get('user_email') or '',
                'full_name': r.get('user_full_name') or '',
                'phone': r.get('user_phone') or '',
            }
            if r.get('user_id')
            else None,
        }
    )

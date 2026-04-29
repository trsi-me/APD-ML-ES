import os
from flask import Blueprint, render_template, send_from_directory, current_app, session
from database.db import get_connection
from routes.auth import login_required

main_bp = Blueprint('main', __name__)


def _get_stats_for_dashboard():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        'SELECT total_analyzed, total_phishing, total_legitimate FROM statistics WHERE id = 1'
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return {
            'total_analyzed': 0,
            'total_phishing': 0,
            'total_legitimate': 0,
            'phishing_percentage': 0.0,
            'legitimate_percentage': 0.0,
        }
    ta = int(row['total_analyzed'] or 0)
    tp = int(row['total_phishing'] or 0)
    tl = int(row['total_legitimate'] or 0)
    if ta <= 0:
        return {
            'total_analyzed': 0,
            'total_phishing': 0,
            'total_legitimate': 0,
            'phishing_percentage': 0.0,
            'legitimate_percentage': 0.0,
        }
    return {
        'total_analyzed': ta,
        'total_phishing': tp,
        'total_legitimate': tl,
        'phishing_percentage': round(100.0 * tp / ta, 1),
        'legitimate_percentage': round(100.0 * tl / ta, 1),
    }


def _get_stats_for_user(user_id):
    """إحصاءات مرتبطة بمستخدم مسجّل (تحليلاته فقط)."""
    if not user_id:
        return {
            'total_analyzed': 0,
            'total_phishing': 0,
            'total_legitimate': 0,
            'phishing_percentage': 0.0,
            'legitimate_percentage': 0.0,
        }
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        'SELECT COUNT(*) AS c, COALESCE(SUM(is_phishing),0) AS ph FROM analyses WHERE user_id = ?',
        (int(user_id),),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return {
            'total_analyzed': 0,
            'total_phishing': 0,
            'total_legitimate': 0,
            'phishing_percentage': 0.0,
            'legitimate_percentage': 0.0,
        }
    total = int(row['c'] or 0)
    ph = int(row['ph'] or 0)
    leg = total - ph
    if total <= 0:
        return {
            'total_analyzed': 0,
            'total_phishing': 0,
            'total_legitimate': 0,
            'phishing_percentage': 0.0,
            'legitimate_percentage': 0.0,
        }
    return {
        'total_analyzed': total,
        'total_phishing': ph,
        'total_legitimate': leg,
        'phishing_percentage': round(100.0 * ph / total, 1),
        'legitimate_percentage': round(100.0 * leg / total, 1),
    }


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    stats = _get_stats_for_user(session.get('user_id'))
    return render_template('dashboard.html', stats=stats)


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/assets/images/<path:filename>')
def project_assets_image(filename):
    base = os.path.join(current_app.root_path, 'assets', 'images')
    return send_from_directory(base, filename)

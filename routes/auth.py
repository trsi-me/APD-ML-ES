import re
from functools import wraps
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_connection

auth_bp = Blueprint('auth', __name__)

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def login_required(view):
    @wraps(view)
    def inner(*a, **kw):
        if not session.get('user_id'):
            return redirect(url_for('auth.login', next=request.path))
        return view(*a, **kw)
    return inner


def _get_user_by_email(email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, email, password_hash, full_name FROM users WHERE email = ?', (email.lower(),))
    row = cur.fetchone()
    conn.close()
    return row


def _get_user_by_id(uid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, email, full_name, phone, bio FROM users WHERE id = ?', (int(uid),))
    row = cur.fetchone()
    conn.close()
    return row


def _get_user_with_hash(uid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        'SELECT id, email, password_hash, full_name, phone, bio FROM users WHERE id = ?', (int(uid),)
    )
    row = cur.fetchone()
    conn.close()
    return row


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        full_name = (request.form.get('full_name') or '').strip() or None
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        password2 = request.form.get('password_confirm') or ''
        if not email or not EMAIL_RE.match(email):
            flash('أدخل بريداً إلكترونياً صالحاً.', 'error')
            return render_template('auth/register.html', full_name=full_name, email=email)
        if len(password) < 8:
            flash('كلمة المرور يجب أن لا تقل عن 8 أحرف.', 'error')
            return render_template('auth/register.html', full_name=full_name, email=email)
        if password != password2:
            flash('تأكيد كلمة المرور غير مطابق.', 'error')
            return render_template('auth/register.html', full_name=full_name, email=email)
        if _get_user_by_email(email):
            flash('هذا البريد مسجّل مسبقاً.', 'error')
            return render_template('auth/register.html', full_name=full_name, email=email)
        ph = generate_password_hash(password)
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                'INSERT INTO users (email, password_hash, full_name) VALUES (?, ?, ?)',
                (email, ph, full_name),
            )
            conn.commit()
            uid = cur.lastrowid
        except Exception:
            conn.rollback()
            flash('تعذّر إنشاء الحساب.', 'error')
            conn.close()
            return render_template('auth/register.html', full_name=full_name, email=email)
        conn.close()
        session['user_id'] = uid
        session['user_email'] = email
        session['user_name'] = full_name or email.split('@')[0]
        flash('تم إنشاء حسابك والدخول.', 'ok')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        nxt = request.args.get('next') or url_for('main.index')
        return redirect(nxt)
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        nxt = request.form.get('next') or request.args.get('next') or url_for('main.index')
        if not nxt.startswith('/') or nxt.startswith('//') or '..' in nxt:
            nxt = url_for('main.index')
        row = _get_user_by_email(email)
        if not row or not check_password_hash(row['password_hash'], password):
            flash('البريد أو كلمة المرور غير صحيحة.', 'error')
            return render_template('auth/login.html', email=email, next_param=nxt)
        session['user_id'] = row['id']
        session['user_email'] = row['email']
        name = row['full_name'] if 'full_name' in row.keys() and row['full_name'] else None
        session['user_name'] = name or (row['email'] or email).split('@')[0]
        return redirect(nxt)
    return render_template('auth/login.html', next_param=request.args.get('next') or '')


@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('user_name', None)
    flash('تم تسجيل الخروج.', 'ok')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    uid = int(session['user_id'])
    row = _get_user_with_hash(uid)
    if not row:
        flash('تعذّر تحميل بيانات الحساب.', 'error')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        full_name = (request.form.get('full_name') or '').strip() or None
        phone = (request.form.get('phone') or '').strip() or None
        bio = (request.form.get('bio') or '').strip() or None
        email = (request.form.get('email') or '').strip().lower()
        current_pw = request.form.get('current_password') or ''
        new_pw = request.form.get('new_password') or ''
        new_pw2 = request.form.get('new_password_confirm') or ''
        if not email or not EMAIL_RE.match(email):
            flash('أدخل بريداً إلكترونياً صالحاً.', 'error')
            return render_template('auth/profile.html', user=row)
        other = _get_user_by_email(email)
        if other and int(other['id']) != uid:
            flash('هذا البريد مرتبط بحساب آخر.', 'error')
            return render_template('auth/profile.html', user=row)
        need_current = (email != row['email']) or new_pw or new_pw2
        if need_current and not current_pw:
            flash('أدخل كلمة المرور الحالية لتغيير البريد أو كلمة المرور.', 'error')
            return render_template('auth/profile.html', user=row)
        if need_current and not check_password_hash(row['password_hash'], current_pw):
            flash('كلمة المرور الحالية غير صحيحة.', 'error')
            return render_template('auth/profile.html', user=row)
        new_hash = row['password_hash']
        if new_pw or new_pw2:
            if len(new_pw) < 8:
                flash('كلمة المرور الجديدة يجب ألا تقل عن 8 أحرف.', 'error')
                return render_template('auth/profile.html', user=row)
            if new_pw != new_pw2:
                flash('تأكيد كلمة المرور غير مطابق.', 'error')
                return render_template('auth/profile.html', user=row)
            new_hash = generate_password_hash(new_pw)
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                '''
                UPDATE users
                SET full_name = ?, phone = ?, bio = ?, email = ?, password_hash = ?
                WHERE id = ?
                ''',
                (full_name, phone, bio, email, new_hash, uid),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            conn.close()
            flash('تعذّر حفظ التغييرات.', 'error')
            return render_template('auth/profile.html', user=row)
        conn.close()
        session['user_email'] = email
        session['user_name'] = full_name or email.split('@')[0]
        flash('تم حفظ الملف الشخصي.', 'ok')
        return redirect(url_for('auth.profile'))
    u = _get_user_by_id(uid)
    return render_template('auth/profile.html', user=u)


@auth_bp.app_context_processor
def inject_auth():
    return {
        'current_user_id': session.get('user_id'),
        'current_user_email': session.get('user_email'),
        'current_user_name': session.get('user_name'),
    }

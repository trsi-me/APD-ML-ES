function escapeHtml(s) {
    const d = document.createElement('div');
    d.textContent = s == null ? '' : String(s);
    return d.innerHTML;
}

function getApp() {
    return document.getElementById('admin-app');
}

function getDetailUrl() {
    const app = getApp();
    return app ? app.getAttribute('data-url-analysis-detail') : '';
}

function applyStats(st) {
    const t = document.getElementById('st-total');
    const p = document.getElementById('st-phish');
    const l = document.getElementById('st-legit');
    const pc = document.getElementById('st-pct-val');
    if (t) t.textContent = st.total;
    if (p) p.textContent = st.phish;
    if (l) l.textContent = st.legit;
    if (pc) pc.textContent = st.pp != null ? st.pp : 0;
}

function applyUserMeta(userCount, orphanCount) {
    const u = document.getElementById('st-users');
    const o = document.getElementById('st-orphan');
    if (u && userCount != null) u.textContent = userCount;
    if (o && orphanCount != null) o.textContent = orphanCount;
}

function buildRow(r) {
    const ph = r.is_phishing === 1 || r.is_phishing === true;
    const badge = ph
        ? '<span class="a-badge a-bad">تصيد</span>'
        : '<span class="a-badge a-ok">شرعي</span>';
    const uid = r.user_id != null && r.user_id !== '' ? String(r.user_id) : '';
    const uemail = r.user_email ? escapeHtml(r.user_email) : '';
    const userCell = uid
        ? '<span class="a-user-pill"><i class="fa-solid fa-user" aria-hidden="true"></i> ' + uemail + '</span>'
        : '<span class="a-user-none">—</span>';
    return (
        '<tr data-row-id="' +
        r.id +
        '" data-user-id="' +
        uid +
        '"><td>' +
        r.id +
        '</td><td class="td-user" title="' +
        (r.user_email ? escapeHtml(r.user_email) : '') +
        '">' +
        userCell +
        '</td><td class="td-prev">' +
        escapeHtml(r.email_preview || '') +
        '</td><td>' +
        badge +
        '</td><td>' +
        (r.confidence != null ? r.confidence : '') +
        '%</td><td class="td-time">' +
        escapeHtml(r.analyzed_at || '') +
        '</td><td class="td-actions td-actions-2"><button type="button" class="a-view" data-id="' +
        r.id +
        '" title="تفاصيل كاملة"><i class="fa-solid fa-file-lines" aria-hidden="true"></i></button><button type="button" class="a-del" data-id="' +
        r.id +
        '" title="حذف"><i class="fa-solid fa-trash" aria-hidden="true"></i></button></td></tr>'
    );
}

function buildUserRow(u) {
    const bio = u.bio || '';
    const bioShow = bio.length > 80 ? escapeHtml(bio.slice(0, 80)) + '…' : escapeHtml(bio || '—');
    return (
        '<tr><td>' +
        u.id +
        '</td><td class="td-mail">' +
        escapeHtml(u.email || '') +
        '</td><td>' +
        (u.full_name ? escapeHtml(u.full_name) : '—') +
        '</td><td>' +
        (u.phone ? escapeHtml(u.phone) : '—') +
        '</td><td class="td-bio" title="' +
        escapeHtml(bio) +
        '">' +
        bioShow +
        '</td><td class="td-time">' +
        escapeHtml(u.created_at || '') +
        '</td><td><strong>' +
        (u.analysis_count != null ? u.analysis_count : 0) +
        '</strong></td><td class="n-ph">' +
        (u.phishing_count != null ? u.phishing_count : 0) +
        '</td><td class="n-ok">' +
        (u.legitimate_count != null ? u.legitimate_count : 0) +
        '</td></tr>'
    );
}

function updateUserFilterSelect(users) {
    const sel = document.getElementById('admin-user-filter');
    if (!sel) return;
    const v = sel.value;
    const opts = [
        '<option value="">الكل</option>',
        '<option value="0">— بلا مستخدم (بذر/ضيف) —</option>',
    ];
    (users || []).forEach(function (u) {
        opts.push(
            '<option value="' +
                u.id +
                '">' +
                escapeHtml(u.email || '') +
                ' (' +
                u.id +
                ')</option>'
        );
    });
    sel.innerHTML = opts.join('');
    if (v) {
        for (let i = 0; i < sel.options.length; i++) {
            if (sel.options[i].value === v) {
                sel.selectedIndex = i;
                break;
            }
        }
    }
}

function bindDeleteButtons() {
    document.querySelectorAll('.a-del').forEach((btn) => {
        btn.addEventListener('click', onDelete);
    });
}

function bindViewButtons() {
    document.querySelectorAll('.a-view').forEach((btn) => {
        btn.addEventListener('click', onViewDetail);
    });
}

function onViewDetail(ev) {
    const btn = ev.currentTarget;
    const id = parseInt(btn.getAttribute('data-id'), 10);
    if (!id) return;
    const base = getDetailUrl();
    if (!base) return;
    const url = base + (base.indexOf('?') >= 0 ? '&' : '?') + 'id=' + id;
    const modal = document.getElementById('admin-modal');
    const body = document.getElementById('admin-modal-body');
    if (!modal || !body) return;
    modal.hidden = false;
    document.body.classList.add('admin-modal-open');
    body.innerHTML = '<p class="admin-muted">جارٍ التحميل…</p>';
    fetch(url, { credentials: 'same-origin' })
        .then((r) => r.json())
        .then((d) => {
            if (!d.success || !d.analysis) {
                body.innerHTML = '<p class="admin-err">' + escapeHtml(d.message || 'تعذّر التحميل') + '</p>';
                return;
            }
            const a = d.analysis;
            const u = d.user;
            let userBlock = '<p class="admin-muted">لا مستخدم مرتبط (بذر / تحليل بدون تسجيل دخول).</p>';
            if (u) {
                userBlock =
                    '<ul class="admin-detail-meta">' +
                    '<li><strong>البريد:</strong> ' +
                    escapeHtml(u.email || '') +
                    '</li>' +
                    '<li><strong>الاسم:</strong> ' +
                    escapeHtml(u.full_name || '—') +
                    '</li>' +
                    '<li><strong>الهاتف:</strong> ' +
                    escapeHtml(u.phone || '—') +
                    '</li></ul>';
            }
            body.innerHTML =
                '<div class="admin-detail-top">' +
                '<p><strong>رقم السجل:</strong> ' +
                a.id +
                ' &nbsp;|&nbsp; <strong>النتيجة:</strong> ' +
                escapeHtml(a.result || '') +
                ' &nbsp;|&nbsp; <strong>الثقة:</strong> ' +
                (a.confidence != null ? a.confidence : '') +
                '% &nbsp;|&nbsp; <strong>الوقت:</strong> ' +
                escapeHtml(a.analyzed_at || '') +
                '</p></div><h3 class="admin-h3">صاحب التحليل (من جدول المستخدمين)</h3>' +
                userBlock +
                '<h3 class="admin-h3">نص البريد / المحتوى الكامل</h3><pre class="admin-detail-pre">' +
                escapeHtml(a.email_text || '') +
                '</pre>' +
                '<h3 class="admin-h3">المعاينة المخزّنة</h3><p class="admin-detail-preview">' +
                escapeHtml(a.email_preview || '') +
                '</p>';
        })
        .catch(() => {
            body.innerHTML = '<p class="admin-err">خطأ في الاتصال.</p>';
        });
}

function closeModal() {
    const modal = document.getElementById('admin-modal');
    if (modal) modal.hidden = true;
    document.body.classList.remove('admin-modal-open');
}

function onDelete(ev) {
    const btn = ev.currentTarget;
    const id = parseInt(btn.getAttribute('data-id'), 10);
    if (!id || !confirm('تأكيد حذف السجل؟')) return;
    const app = getApp();
    if (!app) return;
    const url = app.getAttribute('data-url-delete');
    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({ id: id }),
    })
        .then((r) => r.json())
        .then((data) => {
            if (!data.success) {
                alert(data.message || 'تعذّر الحذف');
                return Promise.resolve(null);
            }
            const tr = btn.closest('tr');
            if (tr) tr.remove();
            return fetch(app.getAttribute('data-url-refresh'), { credentials: 'same-origin' }).then((x) =>
                x.json()
            );
        })
        .then((d) => {
            if (d && d.success && d.stats) {
                applyStats(d.stats);
                if (d.user_count != null) applyUserMeta(d.user_count, d.orphan_count);
                if (d.users) {
                    const ut = document.getElementById('admin-users-tbody');
                    if (ut) {
                        ut.innerHTML = d.users.length
                            ? d.users.map(buildUserRow).join('')
                            : '<tr><td colspan="9" class="td-empty">لا يوجد مستخدمون.</td></tr>';
                    }
                    updateUserFilterSelect(d.users);
                }
            }
        })
        .catch(() => alert('خطأ في الاتصال'));
}

function onRefresh() {
    const app = getApp();
    if (!app) return;
    fetch(app.getAttribute('data-url-refresh'), { credentials: 'same-origin' })
        .then((r) => {
            if (r.status === 401) {
                window.location.reload();
                return null;
            }
            return r.json();
        })
        .then((d) => {
            if (!d || !d.success) return;
            applyStats(d.stats);
            if (d.user_count != null) applyUserMeta(d.user_count, d.orphan_count);
            if (d.users) {
                const ut = document.getElementById('admin-users-tbody');
                if (ut) {
                    ut.innerHTML = d.users.length
                        ? d.users.map(buildUserRow).join('')
                        : '<tr><td colspan="9" class="td-empty">لا يوجد مستخدمون.</td></tr>';
                }
                updateUserFilterSelect(d.users);
            }
            const tb = document.getElementById('admin-tbody');
            if (tb && d.analyses) {
                tb.innerHTML = d.analyses.map(buildRow).join('');
                bindDeleteButtons();
                bindViewButtons();
                runFilter();
            }
        })
        .catch(() => alert('تعذّر التحديث'));
}

function onRecompute() {
    if (!confirm('إعادة حساب الإحصاءات من جدول التحليل؟')) return;
    const app = getApp();
    if (!app) return;
    fetch(app.getAttribute('data-url-recompute'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: '{}',
    })
        .then((r) => r.json())
        .then((d) => {
            if (d.success) onRefresh();
            else alert(d.message || 'تعذّر التنفيذ');
        })
        .catch(() => alert('خطأ في الاتصال'));
}

function onPurge() {
    if (!confirm('سيتم حذف جميع سجلات التحليل نهائياً. المتابعة؟')) return;
    if (!confirm('تأكيد نهائي: حذف كل السجلات؟')) return;
    const app = getApp();
    if (!app) return;
    fetch(app.getAttribute('data-url-purge'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: '{}',
    })
        .then((r) => r.json())
        .then((d) => {
            if (d.success) onRefresh();
            else alert(d.message || 'تعذّر التنفيذ');
        })
        .catch(() => alert('خطأ في الاتصال'));
}

function runUserFilter() {
    const sel = document.getElementById('admin-user-filter');
    const v = sel ? String(sel.value) : '';
    document.querySelectorAll('#admin-tbody tr').forEach((tr) => {
        tr.classList.remove('admin-row-hide-user');
    });
    if (v === '') {
        runFilter();
        return;
    }
    document.querySelectorAll('#admin-tbody tr').forEach((tr) => {
        const u = tr.getAttribute('data-user-id') || '';
        if (v === '0') {
            if (u !== '') tr.classList.add('admin-row-hide-user');
        } else if (u !== v) {
            tr.classList.add('admin-row-hide-user');
        }
    });
    runFilter();
}

function runFilter() {
    const q = (document.getElementById('admin-filter') && document.getElementById('admin-filter').value) || '';
    const t = q.trim().toLowerCase();
    document.querySelectorAll('#admin-tbody tr').forEach((tr) => {
        if (tr.classList.contains('admin-row-hide-user')) {
            tr.classList.add('admin-row-hide');
            return;
        }
        const prev = tr.querySelector('.td-prev');
        const ucell = tr.querySelector('.td-user');
        const ptxt = prev ? (prev.textContent || '').toLowerCase() : '';
        const utxt = ucell ? (ucell.textContent || '').toLowerCase() : '';
        if (!t || ptxt.indexOf(t) !== -1 || utxt.indexOf(t) !== -1) {
            tr.classList.remove('admin-row-hide');
        } else {
            tr.classList.add('admin-row-hide');
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    if (!getApp()) return;
    bindDeleteButtons();
    bindViewButtons();
    const f = document.getElementById('admin-filter');
    if (f) f.addEventListener('input', runFilter);
    const ufs = document.getElementById('admin-user-filter');
    if (ufs) ufs.addEventListener('change', runUserFilter);
    const br = document.getElementById('btn-refresh-d');
    const brec = document.getElementById('btn-recompute');
    const bpur = document.getElementById('btn-purge');
    if (br) br.addEventListener('click', onRefresh);
    if (brec) brec.addEventListener('click', onRecompute);
    if (bpur) bpur.addEventListener('click', onPurge);
    const modal = document.getElementById('admin-modal');
    if (modal) {
        modal.querySelectorAll('[data-close]').forEach((el) => {
            el.addEventListener('click', closeModal);
        });
    }
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeModal();
    });
});

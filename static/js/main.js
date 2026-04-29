// تحميل الإحصاء وعرضه في شريط الصفحة الرئيسية
async function loadStatistics() {
    try {
        const res = await fetch('/api/statistics', { credentials: 'same-origin' });
        const data = await res.json();
        if (!data.success || !data.stats) return;
        const s = data.stats;
        const elT = document.getElementById('stat-total');
        const elP = document.getElementById('stat-phish');
        const elL = document.getElementById('stat-legit');
        if (elT) elT.textContent = s.total_analyzed;
        if (elP) elP.textContent = s.total_phishing;
        if (elL) elL.textContent = s.total_legitimate;
    } catch (e) {
        console.error(e);
    }
}

// تحليل البريد الإلكتروني
async function analyzeEmail() {
    const ta = document.getElementById('email-text');
    const finp = document.getElementById('file-attach');
    const box = document.getElementById('result-box');
    const inner = document.getElementById('result-inner');
    const attMeta = document.getElementById('att-meta');
    const btn = document.getElementById('btn-analyze');
    const pFill = document.getElementById('progress-fill');
    const pPct = document.getElementById('confidence-pct');
    if (!ta || !box || !inner) return;
    const text = (ta.value || '').trim();
    const files = finp && finp.files ? finp.files : null;
    const hasFiles = files && files.length > 0;
    if (!text && !hasFiles) {
        alert('أدخل نص البريد أو اختر مرفقات للتحليل.');
        return;
    }
    if (text && text.length <= 10 && !hasFiles) {
        alert('يجب أن يتجاوز نص البريد عشرة أحرف، أو أضف مرفقات.');
        return;
    }
    const btnText = btn ? btn.querySelector('.btn-text') : null;
    const oldLabel = btnText ? btnText.textContent : '';
    if (btn) {
        btn.disabled = true;
        if (btnText) btnText.textContent = 'جارٍ التحليل...';
    }
    try {
        const fd = new FormData();
        fd.append('email_text', text);
        if (hasFiles) {
            for (let i = 0; i < files.length; i++) {
                fd.append('files', files[i]);
            }
        }
        const res = await fetch('/api/analyze', {
            method: 'POST',
            body: fd,
            credentials: 'same-origin',
        });
        const data = await res.json();
        if (!res.ok || !data.success) {
            const msg = (data && data.message) || 'تعذّر إكمال التحليل.';
            alert(msg);
            return;
        }
        const r = data.result;
        if (attMeta) {
            const ap = data.attachments_parsed;
            if (ap && ap.length) {
                attMeta.textContent = 'تمت معالجة المرفقات: ' + ap.join('، ');
                attMeta.classList.remove('hidden');
            } else {
                attMeta.textContent = '';
                attMeta.classList.add('hidden');
            }
        }
        box.classList.remove('hidden', 'result-phish', 'result-ok');
        if (r.is_phishing) {
            box.classList.add('result-phish');
            inner.innerHTML =
                '<p class="result-line-title"><i class="fa-solid fa-triangle-exclamation result-fa result-fa--bad" aria-hidden="true"></i> <span class="result-title text-danger">تصيد احتيالي</span></p><p>قد يكون هذا البريد محاولة احتيال. لا تدخل بياناتك ولا تفتح روابط مشبوهة.</p>';
        } else {
            box.classList.add('result-ok');
            inner.innerHTML =
                '<p class="result-line-title"><i class="fa-solid fa-circle-check result-fa result-fa--ok" aria-hidden="true"></i> <span class="result-title text-success">بريد شرعي</span></p><p>يعتبر النظام المحتوى ضمن فئة المظهر الشرعي وفق النموذج؛ يبقى الحذر العام مفضّلاً.</p>';
        }
        if (pFill) pFill.style.width = (r.confidence || 0) + '%';
        if (pPct) pPct.textContent = (r.confidence || 0) + '%';
        await loadStatistics();
    } catch (e) {
        console.error(e);
        alert('حدث خطأ أثناء الاتصال بالخادم.');
    } finally {
        if (btn) {
            btn.disabled = false;
            if (btnText) btnText.textContent = oldLabel || 'تحليل (نص + مرفقات)';
        }
    }
}

async function fetchAndAnalyzeMail() {
    const consent = document.getElementById('mail-consent');
    const host = document.getElementById('imap-host');
    const port = document.getElementById('imap-port');
    const user = document.getElementById('imap-user');
    const pwd = document.getElementById('imap-pwd');
    const limit = document.getElementById('imap-limit');
    const ssl = document.getElementById('imap-ssl');
    const st = document.getElementById('mail-status');
    if (!consent || !consent.checked) {
        alert('فعّل الموافقة أولاً.');
        return;
    }
    const h = host && host.value ? host.value.trim() : '';
    const u = user && user.value ? user.value.trim() : '';
    const p = pwd && pwd.value ? pwd.value : '';
    if (!h || !u || !p) {
        alert('أكمل حقول الخادم والبريد وكلمة المرور.');
        return;
    }
    if (st) {
        st.classList.remove('hidden');
        st.textContent = 'جارٍ الجلب والتحليل…';
    }
    try {
        const res = await fetch('/api/mail/fetch-analyze', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                consent: true,
                host: h,
                port: parseInt(port && port.value ? port.value : '993', 10) || 993,
                user: u,
                password: p,
                use_ssl: ssl ? ssl.checked : true,
                limit: parseInt(limit && limit.value ? limit.value : '10', 10) || 10,
            }),
        });
        const data = await res.json();
        if (!res.ok || !data.success) {
            if (st) st.textContent = (data && data.message) || 'فشل الطلب';
            return;
        }
        const c = data.count != null ? data.count : 0;
        if (st) st.textContent = 'تم تحليل ' + c + ' رسالة وحفظها في السجل.';
        await loadStatistics();
    } catch (e) {
        console.error(e);
        if (st) st.textContent = 'خطأ في الاتصال بالخادم.';
    }
}

// عداد الأحرف
function updateCharCount(textarea) {
    const el = textarea || document.getElementById('email-text');
    const out = document.getElementById('char-count');
    if (!el || !out) return;
    const n = (el.value || '').length;
    out.textContent = n + ' / 5000 حرف';
}

// مسح الحقل
function clearForm() {
    const ta = document.getElementById('email-text');
    const finp = document.getElementById('file-attach');
    const fh = document.getElementById('file-hint');
    const am = document.getElementById('att-meta');
    const box = document.getElementById('result-box');
    if (ta) ta.value = '';
    if (finp) finp.value = '';
    if (fh) fh.textContent = 'لا توجد مرفقات';
    if (am) {
        am.textContent = '';
        am.classList.add('hidden');
    }
    updateCharCount(ta);
    if (box) {
        box.classList.add('hidden');
        box.classList.remove('result-phish', 'result-ok');
    }
    const pFill = document.getElementById('progress-fill');
    const pPct = document.getElementById('confidence-pct');
    if (pFill) pFill.style.width = '0%';
    if (pPct) pPct.textContent = '0%';
}

// تحميل سجل التحليلات في لوحة التحكم
async function loadHistory() {
    const tbody = document.getElementById('dashboard-tbody');
    if (!tbody) return;
    try {
        const res = await fetch('/api/history', { credentials: 'same-origin' });
        const data = await res.json();
        if (res.status === 401) {
            tbody.innerHTML = '<tr><td colspan="6" class="table-empty">سجّل الدخول لعرض سجل التحليلات المرتبطة بحسابك.</td></tr>';
            return;
        }
        if (!data.success) {
            tbody.innerHTML = '<tr><td colspan="6" class="table-empty">تعذّر تحميل السجل.</td></tr>';
            return;
        }
        const list = (data.analyses || []).slice(0, 100);
        tbody.innerHTML = '';
        if (list.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="table-empty">لا توجد تحليلات بعد. نفّذ تحليلاً من الرئيسية (مع تسجيل الدخول) أو جلب IMAP بعد الدخول ليظهر السجل هنا.</td></tr>';
            return;
        }
        list.forEach((row, idx) => {
            const tr = document.createElement('tr');
            const badgeClass = row.is_phishing ? 'badge badge-danger' : 'badge badge-success';
            tr.innerHTML =
                '<td>' + (idx + 1) + '</td>' +
                '<td>' + escapeHtml(row.email_preview || '') + '</td>' +
                '<td><span class="' + badgeClass + '">' + escapeHtml(row.result || '') + '</span></td>' +
                '<td>' + (row.confidence != null ? row.confidence : '') + '%</td>' +
                '<td>' + escapeHtml(row.analyzed_at || '') + '</td>' +
                '<td><button type="button" class="delete-btn" onclick="deleteAnalysis(' + row.id + ')" title="حذف"><i class="fa-solid fa-trash" aria-hidden="true"></i></button></td>';
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error(e);
    }
}

function escapeHtml(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
}

// حذف تحليل
async function deleteAnalysis(id) {
    if (!confirm('تأكيد حذف هذا السجل؟')) return;
    try {
        const res = await fetch('/api/history/' + id, { method: 'DELETE', credentials: 'same-origin' });
        const data = await res.json();
        if (!res.ok || !data.success) {
            alert((data && data.message) || 'تعذّر الحذف.');
            return;
        }
        await loadHistory();
        await loadDashboardStats();
    } catch (e) {
        console.error(e);
        alert('حدث خطأ أثناء الحذف.');
    }
}

// تحديث الإحصاء البصري في لوحة التحكم
function updateDashboardStats(stats) {
    if (!stats) return;
    const t = document.getElementById('dash-total');
    const p = document.getElementById('dash-phish');
    const l = document.getElementById('dash-legit');
    const c = document.getElementById('dash-pct');
    const sPh = document.getElementById('dist-phish-seg');
    const sLg = document.getElementById('dist-legit-seg');
    if (t) t.textContent = stats.total_analyzed;
    if (p) p.textContent = stats.total_phishing;
    if (l) l.textContent = stats.total_legitimate;
    if (c) c.textContent = (stats.phishing_percentage != null ? stats.phishing_percentage : 0) + '٪';
    if (sPh) sPh.style.width = (stats.phishing_percentage != null ? stats.phishing_percentage : 0) + '%';
    if (sLg) sLg.style.width = (stats.legitimate_percentage != null ? stats.legitimate_percentage : 0) + '%';
}

async function loadDashboardStats() {
    try {
        const res = await fetch('/api/statistics', { credentials: 'same-origin' });
        const data = await res.json();
        if (data.success && data.stats) updateDashboardStats(data.stats);
    } catch (e) {
        console.error(e);
    }
}

function updateFileHint() {
    const finp = document.getElementById('file-attach');
    const fh = document.getElementById('file-hint');
    if (!finp || !fh) return;
    const n = finp.files ? finp.files.length : 0;
    if (n === 0) {
        fh.textContent = 'لا توجد مرفقات';
    } else {
        const names = [];
        for (let i = 0; i < n; i++) {
            names.push(finp.files[i].name);
        }
        fh.textContent = n + ' ملف(ات): ' + names.join('، ');
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const ta = document.getElementById('email-text');
    const finp = document.getElementById('file-attach');
    if (ta) {
        ta.addEventListener('input', function () {
            updateCharCount(ta);
        });
        updateCharCount(ta);
    }
    if (finp) {
        finp.addEventListener('change', updateFileHint);
    }
    if (document.getElementById('analyze-form')) {
        loadStatistics();
    }
    if (document.getElementById('dashboard-table')) {
        loadHistory();
        loadDashboardStats();
    }
});

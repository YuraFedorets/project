/* ══════════════════════════════════════════════════════
   script.js — УКД Talent: вся клієнтська логіка
   ══════════════════════════════════════════════════════ */

// ── Модальні вікна ─────────────────────────────────────────────────────────────
function toggleModal(id) {
    document.getElementById(id).classList.toggle('hidden');
}

// ── Адмін: пошук компанії у модалці "Додати робітника" ────────────────────────
function filterCompanies(val) {
    const dropdown = document.getElementById('company-dropdown');
    const options  = dropdown.querySelectorAll('.company-option');
    const q        = val.toLowerCase().trim();
    dropdown.classList.remove('hidden');
    let visible = 0;
    options.forEach(opt => {
        const show = !q || opt.dataset.name.toLowerCase().includes(q);
        opt.style.display = show ? '' : 'none';
        if (show) visible++;
    });
    if (!q && visible === 0) dropdown.classList.add('hidden');
}

function selectCompany(id, name) {
    document.getElementById('company-id-hidden').value = id;
    document.getElementById('selected-company-name').textContent = name;
    document.getElementById('selected-company-display').classList.remove('hidden');
    document.getElementById('company-dropdown').classList.add('hidden');
    document.getElementById('company-search-input').value = '';
    const btn = document.getElementById('add-emp-submit-btn');
    btn.disabled = false;
    btn.className = 'w-full bg-[#AC0632] text-white py-3.5 rounded-xl font-black uppercase tracking-widest hover:bg-red-800 transition cursor-pointer';
    document.getElementById('add-emp-hint').classList.add('hidden');
}

function clearCompany() {
    document.getElementById('company-id-hidden').value = '';
    document.getElementById('selected-company-display').classList.add('hidden');
    document.getElementById('company-search-input').value = '';
    document.getElementById('company-dropdown').classList.add('hidden');
    const btn = document.getElementById('add-emp-submit-btn');
    btn.disabled = true;
    btn.className = 'w-full bg-gray-300 text-gray-500 py-3.5 rounded-xl font-black uppercase tracking-widest transition cursor-not-allowed';
    document.getElementById('add-emp-hint').classList.remove('hidden');
}

document.addEventListener('click', function(e) {
    const inp  = document.getElementById('company-search-input');
    const drop = document.getElementById('company-dropdown');
    if (inp && drop && !inp.contains(e.target) && !drop.contains(e.target))
        drop.classList.add('hidden');
});

function toggleEmpPassword() {
    const inp = document.getElementById('emp-password');
    const eye = document.getElementById('emp-pass-eye');
    if (inp.type === 'password') { inp.type = 'text';     eye.className = 'fas fa-eye-slash'; }
    else                         { inp.type = 'password'; eye.className = 'fas fa-eye'; }
}

// ── Гостьовий чат підтримки ────────────────────────────────────────────────────
function sendGuestMessage() {
    const input     = document.getElementById('guest-chat-input');
    const nameInput = document.getElementById('guest-name-input');
    const msg       = input.value.trim();
    if (!msg) return;
    const div = document.getElementById('guest-chat-messages');
    div.innerHTML += `<div class="flex gap-2 items-start flex-row-reverse">
        <div class="bg-gray-300 p-1.5 rounded-full w-7 h-7 flex items-center justify-center shrink-0"><i class="fas fa-user text-xs text-gray-600"></i></div>
        <div class="bg-white rounded-2xl rounded-tr-none p-3 shadow-sm text-sm max-w-[80%]">${msg}</div>
    </div>`;
    fetch('/support/send', {
        method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `message=${encodeURIComponent(msg)}&sender_name=${encodeURIComponent(nameInput.value || 'Гість')}`
    }).then(() => {
        div.innerHTML += `<div class="flex gap-2 items-start">
            <div class="bg-[#AC0632] text-white p-1.5 rounded-full w-7 h-7 flex items-center justify-center shrink-0"><i class="fas fa-robot text-xs"></i></div>
            <div class="bg-white rounded-2xl rounded-tl-none p-3 shadow-sm text-sm">Дякуємо! Адміністратор отримав ваше повідомлення і відповість найближчим часом.</div>
        </div>`;
        div.scrollTop = div.scrollHeight;
    });
    input.value = '';
    div.scrollTop = div.scrollHeight;
}

// ── Особистий чат підтримки (залогінені) ──────────────────────────────────────
let _lastMsgId = 0, _pollingInterval = null;

function toggleUserChat() {
    const chat  = document.getElementById('user-support-chat');
    const badge = document.getElementById('support-float-badge');
    if (!chat) return;
    if (!chat.classList.contains('hidden')) {
        chat.classList.add('hidden');
    } else {
        chat.classList.remove('hidden');
        if (badge) badge.classList.add('hidden');
        loadUserChatHistory();
    }
}

function renderMsg(m) {
    const a = m.sender_type === 'admin';
    return `<div class="flex gap-2 items-start ${a ? '' : 'flex-row-reverse'}">
        <div class="${a ? 'bg-[#AC0632]' : 'bg-gray-300'} text-white p-1.5 rounded-full w-7 h-7 flex items-center justify-center shrink-0">
            <i class="fas ${a ? 'fa-user-shield' : 'fa-user'} text-xs"></i>
        </div>
        <div class="${a ? 'bg-[#AC0632] text-white rounded-tl-none' : 'bg-white rounded-tr-none'} rounded-2xl p-3 shadow-sm text-sm max-w-[75%]">${m.message}</div>
    </div>`;
}

function loadUserChatHistory() {
    fetch('/support/history').then(r => r.json()).then(msgs => {
        const div = document.getElementById('user-chat-messages');
        if (!div) return;
        if (msgs.length > 0) {
            div.innerHTML = '';
            msgs.forEach(m => { div.innerHTML += renderMsg(m); if (m.id > _lastMsgId) _lastMsgId = m.id; });
            div.scrollTop = div.scrollHeight;
        }
        if (!_pollingInterval) _pollingInterval = setInterval(checkNewAdminMessages, 3000);
    });
}

function checkNewAdminMessages() {
    fetch('/support/check_new?last_id=' + _lastMsgId).then(r => r.json()).then(msgs => {
        if (!msgs.length) return;
        const div   = document.getElementById('user-chat-messages');
        const chat  = document.getElementById('user-support-chat');
        const badge = document.getElementById('support-float-badge');
        msgs.forEach(m => {
            if (m.id > _lastMsgId) _lastMsgId = m.id;
            if (chat && !chat.classList.contains('hidden') && div) {
                div.innerHTML += renderMsg(m);
                div.scrollTop = div.scrollHeight;
            } else if (badge) {
                badge.classList.remove('hidden');
                badge.style.display = 'flex';
            }
        });
    });
}

function sendUserMessage() {
    const input = document.getElementById('user-chat-input');
    const msg   = input.value.trim();
    if (!msg) return;
    const div = document.getElementById('user-chat-messages');
    div.innerHTML += `<div class="flex gap-2 items-start flex-row-reverse">
        <div class="bg-gray-300 p-1.5 rounded-full w-7 h-7 flex items-center justify-center shrink-0"><i class="fas fa-user text-xs text-gray-600"></i></div>
        <div class="bg-white rounded-2xl rounded-tr-none p-3 shadow-sm text-sm max-w-[75%]">${msg}</div>
    </div>`;
    div.scrollTop = div.scrollHeight;
    input.value = '';
    fetch('/support/send', {
        method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `message=${encodeURIComponent(msg)}`
    }).then(r => r.json()).then(data => {
        if (data.ok) {
            div.innerHTML += `<div class="flex gap-2 items-start">
                <div class="bg-[#AC0632] text-white p-1.5 rounded-full w-7 h-7 flex items-center justify-center shrink-0"><i class="fas fa-robot text-xs"></i></div>
                <div class="bg-white rounded-2xl rounded-tl-none p-3 shadow-sm text-sm">✅ Повідомлення надіслано! Адміністратор відповість незабаром.</div>
            </div>`;
            div.scrollTop = div.scrollHeight;
            if (!_pollingInterval) _pollingInterval = setInterval(checkNewAdminMessages, 3000);
        }
    });
}

// ── Запрошення та профіль студента ────────────────────────────────────────────
function openInviteModal(id, name) {
    document.getElementById('invite-student-id').value = id;
    document.getElementById('invite-student-name').innerText = name;
    toggleModal('invite-modal');
}

function openStudentProfile(userId) {
    fetch('/api/student/' + userId).then(r => r.json()).then(data => {
        if (data.error) return alert(data.error);
        document.getElementById('sv-avatar').src             = data.avatar || '';
        document.getElementById('sv-name').innerText         = [data.last_name, data.first_name, data.patronymic].filter(Boolean).join(' ') || 'Студент';
        document.getElementById('sv-spec').innerText         = [data.course ? data.course + ' курс' : '', data.specialty].filter(Boolean).join(', ') || 'Студент';
        document.getElementById('sv-skills').innerText       = data.skills || '-';
        document.getElementById('sv-contact-info').innerText = data.contact_info || '-';
        let linksHtml = '-';
        if (data.links && data.links.trim()) {
            linksHtml = '';
            data.links.split(',').map(l => l.trim()).forEach(url => {
                if (!url) return;
                const href = url.startsWith('http') ? url : 'https://' + url;
                let icon = 'fas fa-link';
                if (url.toLowerCase().includes('github'))   icon = 'fab fa-github';
                if (url.toLowerCase().includes('linkedin')) icon = 'fab fa-linkedin';
                linksHtml += `<a href="${href}" target="_blank" class="text-2xl hover:text-red-600 transition"><i class="${icon}"></i></a>`;
            });
        }
        document.getElementById('sv-links').innerHTML = linksHtml;
        document.getElementById('sv-email').innerText = data.email || '';
        toggleModal('student-view-modal');
    });
}

// ── Автозапуск polling ─────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('support-float-btn'))
        _pollingInterval = setInterval(checkNewAdminMessages, 5000);
});

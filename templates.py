"""
templates.py — Файл 2: Дизайн проекту.
Містить повний HTML_TEMPLATE з навігацією, всіма вкладками,
модальними вікнами та JavaScript.
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>УКД Recruitment</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root { --ukd-red: #4a0404; --ukd-bright: #8b0000; }
        body {
            background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)),
                              url('https://ukd.edu.ua/sites/default/files/styles/16/public/2024-10/DSC_3783.jpg?h=295b0d92&itok=mx-I0n3V');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }
        .card { background: white; color: black; border-left: 8px solid black; transition: 0.3s; }
        .card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.5); }
        .nav-btn {
            position: relative;
            color: rgba(255, 255, 255, 0.7) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            padding: 8px 16px !important;
            border-radius: 12px;
            overflow: hidden;
        }
        .nav-btn:hover {
            color: #fff !important;
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-2px);
        }
        .nav-btn::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            width: 0;
            height: 2px;
            background: #ff4d4d;
            transition: all 0.3s ease;
            transform: translateX(-50%);
        }
        .nav-btn:hover::after { width: 70%; }
        .nav-btn.active {
            color: #fff !important;
            background: rgba(255, 77, 77, 0.15);
            font-weight: 700 !important;
        }
        .nav-btn.active::after { width: 80%; background: #ff4d4d; }
        input, select, textarea { border: 2px solid #ddd; transition: 0.3s; color: black; }
        input:focus, select:focus, textarea:focus { border-color: var(--ukd-bright); outline: none; }
        .modal-bg { background: rgba(0,0,0,0.9); }
        .table-wrapper { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }
        .label-text { display: block; font-weight: bold; font-size: 0.75rem; text-transform: uppercase; color: #6b7280; margin-bottom: 0.25rem; }
    </style>
</head>
<body class="min-h-screen flex flex-col">

    <!-- ═══════════════════════ НАВІГАЦІЯ ═══════════════════════ -->
    <nav class="p-4 sticky top-0 z-50 shadow-2xl" style="background-color: #a91825 !important; border-bottom: 2px solid rgba(255,255,255,0.1);">
        <div class="container mx-auto flex items-center justify-between">
            <div class="flex items-center space-x-3 cursor-pointer shrink-0" onclick="window.location.href='/'">
                <div class="bg-white p-2 rounded-lg flex items-center justify-center" style="width: 38px; height: 38px;">
                    <i class="fas fa-graduation-cap" style="color: #AC0632;"></i>
                </div>
                <span class="text-xl font-black uppercase tracking-tighter text-white">УКД TALENT</span>
            </div>

            <div class="flex items-center ml-auto">
                {% if session.get('user_id') %}
                <div class="flex items-center space-x-1">
                    <a href="/?tab=home" class="px-3 py-2 text-white font-bold rounded-xl transition-all hover:bg-white/20 flex items-center {{ 'bg-white/20' if active_tab == 'home' else '' }}">
                        <i class="fas fa-home mr-2"></i> Головна
                    </a>
                    <a href="/?tab=ranking" class="px-3 py-2 text-white font-bold rounded-xl transition-all hover:bg-white/20 flex items-center {{ 'bg-white/20' if active_tab == 'ranking' else '' }}">
                        <i class="fas fa-list-ol mr-2"></i> Рейтинг
                    </a>

                    {% if session.get('role') == 'ADMIN' %}
                    <div class="relative group mx-2">
                        <button class="px-4 py-2 bg-black/40 text-white font-bold rounded-xl transition-all hover:bg-black/60 flex items-center border border-white/10">
                            <i class="fas fa-user-shield mr-2"></i>
                            <span>Адміністрування</span>
                            <i class="fas fa-chevron-down ml-2 text-xs transition group-hover:rotate-180"></i>
                        </button>
                        <div class="absolute right-0 mt-2 w-64 bg-white rounded-2xl shadow-2xl border border-gray-100 py-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 z-[100] transform origin-top scale-95 group-hover:scale-100">
                            <p class="px-4 py-1 text-[10px] font-black text-gray-400 uppercase tracking-widest">Керування</p>
                            <a href="/?tab=invitations" class="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-red-50 hover:text-[#AC0632] transition"><i class="fas fa-shield-alt w-5"></i> Адмін Панель</a>
                            <a href="/?tab=users" class="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-red-50 hover:text-[#AC0632] transition"><i class="fas fa-user-graduate w-5"></i> Студенти</a>
                            <a href="/?tab=companies" class="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-red-50 hover:text-[#AC0632] transition"><i class="fas fa-building w-5"></i> Компанії</a>
                            <a href="/?tab=support" class="flex items-center justify-between px-4 py-3 text-gray-700 hover:bg-red-50 hover:text-[#AC0632] transition">
                                <div class="flex items-center gap-3"><i class="fas fa-headset w-5"></i> Підтримка</div>
                                {% if unread_support_count and unread_support_count > 0 %}
                                <span class="bg-[#AC0632] text-white text-[10px] px-2 py-0.5 rounded-full font-black">{{ unread_support_count }}</span>
                                {% endif %}
                            </a>
                            <div class="border-t-2 border-[#AC0632]/20 my-2 mx-2"></div>
                            <button onclick="toggleModal('create-company-modal')" class="w-full text-left flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-red-50 transition"><i class="fas fa-plus-circle w-5 text-green-600"></i> Нова компанія</button>
                            <button onclick="toggleModal('add-employee-modal')" class="w-full text-left flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-red-50 transition"><i class="fas fa-user-plus w-5 text-blue-600"></i> Додати робітника</button>
                        </div>
                    </div>
                    {% endif %}

                    {% if session.get('role') == 'STUDENT' %}
                    <a href="/?tab=invitations" class="px-3 py-2 text-white font-bold rounded-xl transition-all hover:bg-white/20 flex items-center {{ 'bg-white/20' if active_tab == 'invitations' else '' }}">
                        <i class="fas fa-inbox mr-2"></i> Мої Запрошення
                    </a>
                    {% elif session.get('role') in ['COMPANY', 'COMPANY_ADMIN', 'EMPLOYEE'] %}
                    <a href="/?tab=invitations" class="px-3 py-2 text-white font-bold rounded-xl transition-all hover:bg-white/20 flex items-center {{ 'bg-white/20' if active_tab == 'invitations' else '' }}">
                        <i class="fas fa-paper-plane mr-2"></i> Запити
                    </a>
                    {% endif %}

                    <a href="/?tab=profile" class="px-3 py-2 text-white font-bold rounded-xl transition-all hover:bg-white/20 flex items-center {{ 'bg-white/20' if active_tab == 'profile' else '' }}">
                        <i class="fas fa-user-circle mr-2"></i> Профіль
                    </a>

                    <div class="flex items-center space-x-3 ml-4 pl-4 border-l border-white/20">
                        <div class="text-right hidden sm:block">
                            <div class="text-[10px] text-white/70 uppercase font-black leading-tight">{{ session.get('role') }}</div>
                            <div class="text-sm text-white font-bold leading-none">{{ session.get('username') }}</div>
                        </div>
                        <a href="/logout" class="bg-white/10 hover:bg-red-600 p-2 rounded-full text-white transition flex items-center justify-center w-9 h-9">
                            <i class="fas fa-sign-out-alt"></i>
                        </a>
                    </div>
                </div>
                {% else %}
                <div class="flex items-center">
                    <button onclick="toggleModal('login-modal')" class="bg-white text-[#AC0632] px-6 py-2 rounded-xl font-bold hover:bg-gray-100 transition-all shadow-lg uppercase text-xs tracking-widest flex items-center gap-2">
                        <i class="fas fa-sign-in-alt"></i> Вхід
                    </button>
                </div>
                {% endif %}
            </div>
        </div>
    </nav>

    <!-- Мобільне меню -->
    {% if session.get('user_id') %}
    <div class="md:hidden flex justify-around mt-4 border-t border-white/10 pt-2 overflow-x-auto gap-4">
        <a href="/?tab=home" class="text-sm whitespace-nowrap text-white"><i class="fas fa-home"></i> Головна</a>
        <a href="/?tab=ranking" class="text-sm whitespace-nowrap text-white"><i class="fas fa-list"></i> Рейтинг</a>
        <a href="/?tab=invitations" class="text-sm whitespace-nowrap text-white"><i class="fas fa-inbox"></i> Inbox</a>
        {% if session.get('role') == 'ADMIN' %}
        <a href="/?tab=users" class="text-sm text-purple-400 whitespace-nowrap"><i class="fas fa-user-graduate"></i> Студенти</a>
        <a href="/?tab=companies" class="text-sm text-blue-400 whitespace-nowrap"><i class="fas fa-building"></i> Компанії</a>
        {% endif %}
        <a href="/?tab=profile" class="text-sm whitespace-nowrap text-white"><i class="fas fa-user"></i> Профіль</a>
    </div>
    {% endif %}

    <main class="flex-grow relative">

        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="container mx-auto px-4 mt-6">
                <div class="bg-green-600 text-white p-4 rounded-xl text-center font-bold shadow-lg animate-bounce">
                {{ messages[0] }}
                </div>
            </div>
          {% endif %}
        {% endwith %}

        <!-- ═══════════════════════ ЛЕНДІНГ ═══════════════════════ -->
        {% if not session.get('user_id') %}
        <div class="min-h-[80vh] flex items-center justify-center text-center px-4">
            <div class="max-w-4xl mx-auto flex flex-col items-center justify-center">
                <h1 class="text-5xl md:text-7xl font-black uppercase mb-6 drop-shadow-lg text-center text-white">
                    Знайди Своє <span class="text-red-600">Майбутнє</span>
                </h1>
                <p class="text-xl md:text-2xl font-light text-gray-200 text-center">
                    Платформа працевлаштування для студентів Університету Короля Данила.
                </p>
                <button onclick="toggleModal('guest-chat-modal')" class="mt-8 inline-flex items-center gap-3 bg-[#AC0632] hover:bg-red-800 text-white px-8 py-4 rounded-full font-black uppercase transition shadow-xl border border-red-400 hover:border-white transform hover:scale-105">
                    <i class="fas fa-headset text-2xl"></i> Чат Підтримки
                </button>
            </div>
        </div>

        <!-- Модальний чат для гостей -->
        <div id="guest-chat-modal" class="hidden fixed inset-0 modal-bg z-[200] flex items-center justify-center p-4">
            <div class="bg-white text-black rounded-3xl w-full max-w-md relative shadow-2xl flex flex-col" style="max-height:90vh;">
                <div class="flex items-center justify-between p-5 border-b border-gray-100 bg-[#AC0632] rounded-t-3xl">
                    <div class="flex items-center gap-3">
                        <div class="bg-white p-2 rounded-full"><i class="fas fa-headset text-[#AC0632] text-lg"></i></div>
                        <div>
                            <div class="text-white font-black text-lg uppercase">Підтримка УКД</div>
                            <div class="text-red-200 text-xs">Напишіть своє питання</div>
                        </div>
                    </div>
                    <button onclick="toggleModal('guest-chat-modal')" class="text-white text-2xl hover:text-red-200 transition">&times;</button>
                </div>
                <div id="guest-chat-messages" class="flex-1 overflow-y-auto p-5 space-y-3 bg-gray-50" style="min-height:200px;max-height:350px;">
                    <div class="flex gap-2 items-start">
                        <div class="bg-[#AC0632] text-white p-2 rounded-full w-8 h-8 flex items-center justify-center shrink-0"><i class="fas fa-robot text-xs"></i></div>
                        <div class="bg-white rounded-2xl rounded-tl-none p-3 shadow-sm text-sm max-w-[80%]">Вітаємо! Якщо у вас є питання щодо платформи — напишіть нам. Адміністратор відповість якнайшвидше.</div>
                    </div>
                </div>
                <div class="p-4 border-t border-gray-100 bg-white rounded-b-3xl">
                    <div class="mb-2">
                        <input type="text" id="guest-name-input" placeholder="Ваше ім'я (необов'язково)" class="w-full p-2 rounded-xl bg-gray-100 border text-sm mb-2 focus:border-[#AC0632] outline-none">
                    </div>
                    <div class="flex gap-2">
                        <input type="text" id="guest-chat-input" placeholder="Напишіть повідомлення..." class="flex-1 p-3 rounded-xl bg-gray-100 border text-sm focus:border-[#AC0632] outline-none" onkeydown="if(event.key==='Enter') sendGuestMessage()">
                        <button onclick="sendGuestMessage()" class="bg-[#AC0632] text-white px-4 py-2 rounded-xl hover:bg-red-800 transition"><i class="fas fa-paper-plane"></i></button>
                    </div>
                </div>
            </div>
        </div>

        {% else %}
        <!-- ═══════════════════════ ВНУТРІШНЯ ЧАСТИНА ═══════════════════════ -->
        <div class="container mx-auto px-4 py-8">

            <!-- ── ГОЛОВНА ── -->
            {% if active_tab == 'home' %}
            <section class="max-w-6xl mx-auto text-center py-8">
                <h1 class="text-4xl md:text-6xl font-black uppercase mb-6 drop-shadow-lg tracking-tighter text-white">
                    Ласкаво просимо до <span class="text-red-600">УКД Talent</span>
                </h1>
                <p class="text-lg md:text-xl mb-12 font-light text-gray-200 max-w-3xl mx-auto">
                    Платформа, що об'єднує найкращих студентів та провідних роботодавців для побудови успішного майбутнього.
                </p>
                <div class="grid md:grid-cols-2 gap-8 text-left mb-16">
                    <div class="bg-white text-black p-8 rounded-3xl shadow-2xl border-l-8 border-red-700 transition hover:-translate-y-2">
                        <div class="text-red-700 text-4xl mb-4"><i class="fas fa-university"></i></div>
                        <h2 class="text-2xl font-black uppercase mb-4">Університет Короля Данила (УКД)</h2>
                        <p class="text-gray-700 font-medium leading-relaxed">
                            Університет Короля Данила — це сучасний заклад вищої освіти, який фокусується на практичних навичках, інноваціях та успішному працевлаштуванні випускників. Ми створюємо умови для розвитку талантів та тісно співпрацюємо з провідними компаніями.
                        </p>
                    </div>
                    <div class="bg-white text-black p-8 rounded-3xl shadow-2xl border-l-8 border-black transition hover:-translate-y-2">
                        <div class="text-black text-4xl mb-4"><i class="fas fa-project-diagram"></i></div>
                        <h2 class="text-2xl font-black uppercase mb-4">Про Проєкт</h2>
                        <p class="text-gray-700 font-medium leading-relaxed">
                            <b>УКД Recruitment Platform</b> — інноваційне рішення для спрощення процесу пошуку першої роботи для студентів та молодих спеціалістів. Студенти створюють портфоліо, а компанії надсилають їм прямі запрошення на роботу.
                        </p>
                    </div>
                </div>
                <div class="mt-8 border-t border-white/20 pt-12 pb-6">
                    <p class="text-gray-400 font-bold uppercase mb-6">Потрібна допомога? Напишіть нам:</p>
                    <button onclick="toggleUserChat()" class="inline-flex items-center gap-3 bg-[#AC0632] hover:bg-red-800 text-white px-8 py-4 rounded-full font-black uppercase transition shadow-xl border border-red-400 hover:border-white transform hover:scale-105">
                        <i class="fas fa-headset text-2xl"></i> Чат Підтримки
                    </button>
                </div>
            </section>
            {% endif %}

            <!-- ── РЕЙТИНГ ── -->
            {% if active_tab == 'ranking' %}
            <section class="max-w-7xl mx-auto">
                <h2 class="text-4xl font-black mb-8 uppercase tracking-tighter border-b-4 border-white pb-2 text-white">Рейтинг Студентів</h2>
                <form method="GET" action="/" class="bg-black/40 backdrop-blur-xl text-white p-6 rounded-[30px] border border-white/10 shadow-2xl mb-8 flex flex-wrap gap-4 items-end">
                    <input type="hidden" name="tab" value="ranking">
                    <div class="flex-grow min-w-[200px]">
                        <label class="block text-xs font-black uppercase text-gray-400 mb-2 ml-1 tracking-widest">Пошук (Ім'я, Навички)</label>
                        <div class="relative">
                            <i class="fas fa-search absolute left-4 top-4 text-gray-500"></i>
                            <input type="text" name="search" value="{{ current_filters.search }}" class="w-full pl-12 pr-4 py-3.5 rounded-2xl bg-white/5 border border-white/10 focus:border-red-500/50 transition-all outline-none text-white placeholder-gray-500" placeholder="Наприклад: Python, Дизайн...">
                        </div>
                    </div>
                    <div class="w-full md:w-auto">
                        <label class="block text-xs font-black uppercase text-gray-400 mb-2 ml-1 tracking-widest">Курс</label>
                        <select name="course" class="w-full p-3.5 rounded-2xl bg-white/5 border border-white/10 focus:border-red-500/50 transition-all outline-none text-white appearance-none cursor-pointer">
                            <option value="" class="bg-gray-900">Всі курси</option>
                            {% for c in unique_courses %}
                            <option value="{{ c }}" {% if current_filters.course == c|string %}selected{% endif %} class="bg-gray-900">{{ c }} курс</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="w-full md:w-auto">
                        <label class="block text-xs font-black uppercase text-gray-400 mb-2 ml-1 tracking-widest">Спеціальність</label>
                        <select name="specialty" class="w-full p-3.5 rounded-2xl bg-white/5 border border-white/10 focus:border-red-500/50 transition-all outline-none text-white appearance-none cursor-pointer">
                            <option value="" class="bg-gray-900">Всі спеціальності</option>
                            {% for s in unique_specialties %}
                            <option value="{{ s }}" {% if current_filters.specialty == s %}selected{% endif %} class="bg-gray-900">{{ s }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="w-full md:w-auto">
                        <label class="block text-xs font-black uppercase text-gray-400 mb-2 ml-1 tracking-widest">Сортування</label>
                        <select name="sort" class="w-full p-3.5 rounded-2xl bg-white/5 border border-white/10 focus:border-red-500/50 transition-all outline-none text-white appearance-none cursor-pointer">
                            <option value="desc" {% if current_filters.sort == 'desc' %}selected{% endif %} class="bg-gray-900">Рейтинг: Топ</option>
                            <option value="asc" {% if current_filters.sort == 'asc' %}selected{% endif %} class="bg-gray-900">Рейтинг: Зростання</option>
                        </select>
                    </div>
                    <div class="w-full md:w-auto flex gap-3">
                        <button type="submit" class="bg-red-600 hover:bg-red-500 text-white px-8 py-3.5 rounded-2xl font-black uppercase tracking-widest shadow-lg transition-all active:scale-95 flex items-center gap-2">
                            <i class="fas fa-filter"></i> Знайти
                        </button>
                        <a href="/?tab=ranking" class="bg-white/10 hover:bg-white/20 text-white px-5 py-3.5 rounded-2xl transition-all active:scale-95 flex items-center justify-center shadow-lg" title="Скинути">
                            <i class="fas fa-sync-alt"></i>
                        </a>
                    </div>
                </form>

                {% if students %}
                <div class="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {% for std in students %}
                    <div class="card rounded-2xl p-6 relative group overflow-hidden flex flex-col h-full">
                        <div class="absolute top-4 right-4 bg-yellow-400 text-black px-2 py-1 rounded-lg font-black text-sm shadow-md">
                            <i class="fas fa-star text-xs"></i> {{ std.rating or 0 }}
                        </div>
                        <div class="flex items-center space-x-4 mb-4">
                            <img src="{{ std.avatar }}" class="w-16 h-16 rounded-full border-2 border-black object-cover bg-gray-200">
                            <div class="pr-8">
                                <h3 class="text-lg font-black uppercase leading-tight">{{ std.last_name }} {{ std.first_name }}</h3>
                                <p class="text-xs text-gray-500 font-bold mt-1">{{ std.course or '?' }} курс, {{ std.specialty or 'Спеціальність не вказана' }}</p>
                            </div>
                        </div>
                        <div class="mb-4 flex-grow overflow-hidden">
                            <p class="text-[10px] font-bold uppercase text-gray-400 mb-1">Навички:</p>
                            <div class="flex flex-wrap gap-1 max-h-16 overflow-y-auto">
                                {% for skill in (std.skills or '').split(',') %}
                                    {% if skill.strip() %}
                                    <span class="bg-gray-200 text-black px-2 py-0.5 rounded text-[10px] font-bold">{{ skill.strip() }}</span>
                                    {% endif %}
                                {% endfor %}
                                {% if not std.skills %}<span class="text-gray-400 text-xs italic">Немає даних</span>{% endif %}
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2 mt-auto pt-4 border-t border-gray-100">
                            <button onclick="openStudentProfile({{ std.id }})" class="bg-black text-white py-2 rounded-lg font-bold text-xs uppercase hover:bg-gray-800 transition">
                                <i class="fas fa-eye mr-1"></i> Профіль
                            </button>
                            {% if session.get('role') in ['COMPANY', 'COMPANY_ADMIN', 'EMPLOYEE', 'ADMIN'] %}
                            <button onclick="openInviteModal({{ std.id }}, '{{ std.first_name }}')" class="bg-red-700 text-white py-2 rounded-lg font-bold text-xs uppercase hover:bg-red-800 transition">
                                <i class="fas fa-handshake mr-1"></i> Найняти
                            </button>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <div class="text-center opacity-50 text-xl py-20 bg-black/20 rounded-2xl border border-white/10 text-white">
                    <i class="fas fa-search mb-4 text-4xl"></i><br>
                    Студентів за такими критеріями не знайдено.
                </div>
                {% endif %}
            </section>
            {% endif %}

            <!-- ── ЗАПРОШЕННЯ ── -->
            {% if active_tab == 'invitations' %}
            <section class="max-w-6xl mx-auto px-4">
                <h2 class="text-3xl font-black mb-8 uppercase flex items-center gap-3 text-white">
                    {% if session.get('role') == 'ADMIN' %}<i class="fas fa-shield-alt text-white"></i> Панель Керування Заявками
                    {% elif session.get('role') == 'STUDENT' %}<i class="fas fa-inbox text-white"></i> Мої Запрошення
                    {% else %}<i class="fas fa-paper-plane text-white"></i> Надіслані Пропозиції{% endif %}
                </h2>

                {% if session.get('role') == 'ADMIN' %}
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                    <div class="bg-white p-6 rounded-3xl shadow-xl border-l-8 border-[#AC0632]">
                        <div class="text-gray-500 text-xs font-bold uppercase">Усього заявок</div>
                        <div class="text-3xl font-black text-black">{{ invitations|length }}</div>
                    </div>
                    <div class="bg-white p-6 rounded-3xl shadow-xl border-l-8 border-green-500">
                        <div class="text-gray-500 text-xs font-bold uppercase">Прийнято</div>
                        <div class="text-3xl font-black text-black">{{ invitations|selectattr('status', 'equalto', 'accepted')|list|length }}</div>
                    </div>
                    <div class="bg-white p-6 rounded-3xl shadow-xl border-l-8 border-yellow-500">
                        <div class="text-gray-500 text-xs font-bold uppercase">Очікують</div>
                        <div class="text-3xl font-black text-black">{{ invitations|selectattr('status', 'equalto', 'pending')|list|length }}</div>
                    </div>
                    <div class="bg-white p-6 rounded-3xl shadow-xl border-l-8 border-red-600 animate-pulse">
                        <div class="text-gray-500 text-xs font-bold uppercase">Потребують уваги</div>
                        <div class="text-3xl font-black text-red-600">{{ invitations|selectattr('flagged', 'equalto', true)|list|length }}</div>
                    </div>
                </div>
                {% endif %}

                <div class="bg-white text-black rounded-3xl shadow-2xl overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left min-w-max">
                            <thead class="bg-gray-50 border-b border-gray-200">
                                <tr>
                                    {% if session.get('role') not in ['COMPANY', 'COMPANY_ADMIN', 'EMPLOYEE'] %}<th class="p-5 font-black uppercase text-xs text-gray-400">Від Кого</th>{% endif %}
                                    {% if session.get('role') not in ['STUDENT'] %}<th class="p-5 font-black uppercase text-xs text-gray-400">Кому (Студент)</th>{% endif %}
                                    <th class="p-5 font-black uppercase text-xs text-gray-400">Повідомлення</th>
                                    <th class="p-5 font-black uppercase text-xs text-gray-400">Статус</th>
                                    <th class="p-5 font-black uppercase text-xs text-gray-400 text-center">Дії</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100">
                                {% for inv in invitations %}
                                <tr class="hover:bg-gray-50/80 transition-all {% if session.get('role') == 'ADMIN' and inv.flagged %}bg-red-50/50{% endif %}">
                                    {% if session.get('role') not in ['COMPANY', 'COMPANY_ADMIN', 'EMPLOYEE'] %}
                                    <td class="p-5">
                                        <div class="flex items-center space-x-3">
                                            <img src="{{ inv.company_avatar or 'https://cdn-icons-png.flaticon.com/512/3061/3061341.png' }}" class="w-10 h-10 rounded-xl object-cover shadow-sm">
                                            <div>
                                                <span class="font-bold text-black block leading-tight">{{ inv.company_name or 'Невідома Компанія' }}</span>
                                                <span class="text-[10px] text-gray-400 font-bold uppercase tracking-widest">{{ inv.created_at }}</span>
                                            </div>
                                        </div>
                                    </td>
                                    {% endif %}
                                    {% if session.get('role') not in ['STUDENT'] %}
                                    <td class="p-5"><span class="font-bold text-gray-800">{{ inv.last_name }} {{ inv.first_name }}</span></td>
                                    {% endif %}
                                    <td class="p-5"><div class="text-sm text-gray-600 italic max-w-xs truncate">"{{ inv.message }}"</div></td>
                                    <td class="p-5">
                                        {% if inv.status == 'pending' %}<span class="bg-yellow-100 text-yellow-700 px-3 py-1 rounded-lg text-[10px] font-black uppercase">Очікує</span>
                                        {% elif inv.status == 'accepted' %}<span class="bg-green-100 text-green-700 px-3 py-1 rounded-lg text-[10px] font-black uppercase">Прийнято</span>
                                        {% elif inv.status == 'rejected' %}<span class="bg-red-100 text-red-700 px-3 py-1 rounded-lg text-[10px] font-black uppercase">Відхилено</span>{% endif %}
                                    </td>
                                    <td class="p-5">
                                        <div class="flex gap-2 justify-center">
                                            {% if session.get('role') == 'STUDENT' and inv.status == 'pending' %}
                                            <form action="/respond_invite" method="POST" class="m-0">
                                                <input type="hidden" name="invite_id" value="{{ inv.id }}">
                                                <input type="hidden" name="action" value="accept">
                                                <button class="bg-[#AC0632] text-white px-4 py-1.5 rounded-lg hover:bg-black transition-all text-xs font-bold uppercase">Так</button>
                                            </form>
                                            <form action="/respond_invite" method="POST" class="m-0">
                                                <input type="hidden" name="invite_id" value="{{ inv.id }}">
                                                <input type="hidden" name="action" value="reject">
                                                <button class="border-2 border-gray-200 text-gray-500 px-4 py-1.5 rounded-lg hover:bg-gray-100 transition-all text-xs font-bold uppercase">Ні</button>
                                            </form>
                                            {% endif %}
                                            {% if session.get('role') in ['COMPANY_ADMIN', 'EMPLOYEE', 'ADMIN'] %}
                                            <form action="/delete_invite" method="POST" class="m-0" onsubmit="return confirm('Видалити запит?');">
                                                <input type="hidden" name="invite_id" value="{{ inv.id }}">
                                                <button class="w-9 h-9 flex items-center justify-center bg-gray-100 text-gray-400 hover:bg-[#AC0632] hover:text-white rounded-xl transition-all"><i class="fas fa-trash-alt text-sm"></i></button>
                                            </form>
                                            {% endif %}
                                        </div>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>
            {% endif %}

            <!-- ── СТУДЕНТИ (ADMIN) ── -->
            {% if active_tab == 'users' and session.get('role') == 'ADMIN' %}
            <section class="w-full max-w-[95%] mx-auto">
                <h2 class="text-3xl font-black mb-6 uppercase flex items-center gap-3 text-white">
                    <i class="fas fa-users text-purple-400"></i> Управління Студентами
                </h2>
                <div class="bg-white text-black rounded-3xl shadow-2xl overflow-hidden">
                    <div class="table-wrapper">
                        <table class="w-full text-left text-sm min-w-max">
                            <thead class="bg-gray-100 border-b-2 border-black">
                                <tr>
                                    <th class="p-4 font-black uppercase whitespace-nowrap">ID</th>
                                    <th class="p-4 font-black uppercase whitespace-nowrap">Логін</th>
                                    <th class="p-4 font-black uppercase whitespace-nowrap">Email</th>
                                    <th class="p-4 font-black uppercase min-w-[200px]">ПІБ</th>
                                    <th class="p-4 font-black uppercase min-w-[150px]">Курс / Спеціальність</th>
                                    <th class="p-4 font-black uppercase whitespace-nowrap">Рейтинг</th>
                                    <th class="p-4 font-black uppercase min-w-[200px]">Контакти</th>
                                    <th class="p-4 font-black uppercase whitespace-nowrap">Статус</th>
                                    <th class="p-4 font-black uppercase whitespace-nowrap">Дії</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200">
                                {% for u in all_students %}
                                <tr class="hover:bg-gray-50 transition {% if u.status == 'blocked' %}bg-red-50 opacity-75{% endif %}">
                                    <td class="p-4 font-bold">{{ u.id }}</td>
                                    <td class="p-4 font-mono text-sm">{{ u.username or '-' }}</td>
                                    <td class="p-4 text-blue-700">{{ u.email or '-' }}</td>
                                    <td class="p-4"><b>{{ u.last_name }}</b> {{ u.first_name }} {{ u.patronymic or '' }}</td>
                                    <td class="p-4">
                                        <div class="font-bold">{{ u.course or '-' }} курс</div>
                                        <div class="text-xs text-red-600">{{ u.specialty or '-' }}</div>
                                    </td>
                                    <td class="p-4 text-center"><span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded font-black">⭐ {{ u.rating or 0 }}</span></td>
                                    <td class="p-4 text-xs">{{ u.contact_info or '-' }}</td>
                                    <td class="p-4 whitespace-nowrap">
                                        {% if u.status == 'blocked' %}<span class="bg-red-200 text-red-800 px-2 py-1 rounded text-xs font-black uppercase">Заблок.</span>
                                        {% else %}<span class="bg-green-200 text-green-800 px-2 py-1 rounded text-xs font-black uppercase">Активний</span>{% endif %}
                                    </td>
                                    <td class="p-4">
                                        <div class="flex gap-2">
                                            <form action="/admin/toggle_block" method="POST" class="m-0">
                                                <input type="hidden" name="user_id" value="{{ u.id }}">
                                                <input type="hidden" name="user_type" value="student">
                                                {% if u.status == 'blocked' %}<button class="bg-green-600 text-white px-3 py-1.5 rounded text-xs font-bold uppercase"><i class="fas fa-unlock mr-1"></i>Розблок.</button>
                                                {% else %}<button class="bg-orange-500 text-white px-3 py-1.5 rounded text-xs font-bold uppercase" onclick="return confirm('Заблокувати?')"><i class="fas fa-ban mr-1"></i>Блок.</button>{% endif %}
                                            </form>
                                            <form action="/admin/delete_user" method="POST" class="m-0" onsubmit="return confirm('Видалити назавжди?')">
                                                <input type="hidden" name="user_id" value="{{ u.id }}">
                                                <input type="hidden" name="user_type" value="student">
                                                <button class="bg-red-700 text-white px-3 py-1.5 rounded text-xs font-bold uppercase"><i class="fas fa-trash mr-1"></i>Видалити</button>
                                            </form>
                                        </div>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>
            {% endif %}

            <!-- ── КОМПАНІЇ (ADMIN) ── -->
            {% if active_tab == 'companies' and session.get('role') == 'ADMIN' %}
            <section class="w-full max-w-[95%] mx-auto">
                <h2 class="text-3xl font-black mb-6 uppercase flex items-center gap-3 text-white">
                    <i class="fas fa-building text-blue-400"></i> Компанії та Працівники
                </h2>
                {% for comp in all_companies %}
                <div class="bg-white text-black rounded-3xl shadow-2xl overflow-hidden mb-8 border-l-8 border-blue-500">
                    <div class="p-6 bg-blue-50 flex items-center gap-4">
                        <img src="{{ comp.avatar or 'https://cdn-icons-png.flaticon.com/512/3061/3061341.png' }}" class="w-12 h-12 rounded-xl object-contain bg-white border">
                        <div>
                            <h3 class="text-xl font-black">{{ comp.company_name }}</h3>
                            <p class="text-sm text-gray-500">{{ comp.contact_info or '' }}</p>
                        </div>
                    </div>
                    <div class="table-wrapper">
                        <table class="w-full text-left text-sm">
                            <thead class="bg-gray-100 border-b border-gray-200">
                                <tr>
                                    <th class="p-3 font-black uppercase text-xs">ID</th>
                                    <th class="p-3 font-black uppercase text-xs">Логін</th>
                                    <th class="p-3 font-black uppercase text-xs">Email</th>
                                    <th class="p-3 font-black uppercase text-xs">Посада</th>
                                    <th class="p-3 font-black uppercase text-xs">Роль</th>
                                    <th class="p-3 font-black uppercase text-xs">Статус</th>
                                    <th class="p-3 font-black uppercase text-xs">Дії</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100">
                                {% for emp in comp.employees %}
                                <tr class="hover:bg-gray-50 {% if emp.status == 'blocked' %}bg-red-50 opacity-75{% endif %}">
                                    <td class="p-3 font-bold">{{ emp.id }}</td>
                                    <td class="p-3 font-mono">{{ emp.username or '-' }}</td>
                                    <td class="p-3 text-blue-700">{{ emp.email }}</td>
                                    <td class="p-3">{{ emp.position or '-' }}</td>
                                    <td class="p-3"><span class="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-bold">{{ emp.role }}</span></td>
                                    <td class="p-3">
                                        {% if emp.status == 'blocked' %}<span class="bg-red-200 text-red-800 px-2 py-1 rounded text-xs font-black">Заблок.</span>
                                        {% else %}<span class="bg-green-200 text-green-800 px-2 py-1 rounded text-xs font-black">Активний</span>{% endif %}
                                    </td>
                                    <td class="p-3">
                                        <div class="flex gap-2">
                                            <form action="/admin/toggle_block" method="POST" class="m-0">
                                                <input type="hidden" name="user_id" value="{{ emp.id }}">
                                                <input type="hidden" name="user_type" value="employee">
                                                {% if emp.status == 'blocked' %}<button class="bg-green-600 text-white px-3 py-1.5 rounded text-xs font-bold"><i class="fas fa-unlock"></i></button>
                                                {% else %}<button class="bg-orange-500 text-white px-3 py-1.5 rounded text-xs font-bold" onclick="return confirm('Заблокувати?')"><i class="fas fa-ban"></i></button>{% endif %}
                                            </form>
                                            <form action="/admin/delete_user" method="POST" class="m-0" onsubmit="return confirm('Видалити?')">
                                                <input type="hidden" name="user_id" value="{{ emp.id }}">
                                                <input type="hidden" name="user_type" value="employee">
                                                <button class="bg-red-700 text-white px-3 py-1.5 rounded text-xs font-bold"><i class="fas fa-trash"></i></button>
                                            </form>
                                        </div>
                                    </td>
                                </tr>
                                {% endfor %}
                                {% if not comp.employees %}
                                <tr><td colspan="7" class="p-4 text-center text-gray-400 italic">Немає працівників</td></tr>
                                {% endif %}
                            </tbody>
                        </table>
                    </div>
                </div>
                {% endfor %}
            </section>
            {% endif %}

            <!-- ── ПІДТРИМКА (ADMIN) ── -->
            {% if active_tab == 'support' and session.get('role') == 'ADMIN' %}
            <section class="w-full max-w-5xl mx-auto">
                <h2 class="text-3xl font-black mb-6 uppercase flex items-center gap-3 text-white">
                    <i class="fas fa-headset text-red-400"></i> Чат Підтримки
                </h2>
                <div class="grid md:grid-cols-3 gap-6">
                    <div class="bg-white text-black rounded-3xl shadow-xl overflow-hidden">
                        <div class="p-4 bg-gray-50 border-b flex items-center justify-between">
                            <span class="font-black uppercase text-sm text-gray-500">Діалоги</span>
                            {% if show_archived %}
                            <a href="/?tab=support" class="text-xs text-[#AC0632] font-bold hover:underline">← Активні</a>
                            {% else %}
                            <a href="/?tab=support&show_archived=1" class="text-xs text-gray-400 hover:text-[#AC0632] font-bold">Архів</a>
                            {% endif %}
                        </div>
                        <div class="divide-y divide-gray-100 overflow-y-auto" style="max-height:500px;">
                            {% for conv in support_conversations %}
                            <div class="flex items-center gap-2 p-3 hover:bg-gray-50 transition {% if conv.session_key == active_conv_key %}bg-red-50 border-l-4 border-[#AC0632]{% endif %}">
                                <a href="/?tab=support&conv_key={{ conv.session_key }}{% if show_archived %}&show_archived=1{% endif %}" class="flex items-center gap-2 min-w-0 flex-1">
                                    <div class="w-9 h-9 rounded-full bg-[#AC0632] flex items-center justify-center text-white font-black text-sm shrink-0">{{ (conv.sender_name or 'Г')[0].upper() }}</div>
                                    <div class="min-w-0">
                                        <div class="font-bold text-sm truncate">{{ conv.sender_name or 'Гість' }}</div>
                                        <div class="text-xs text-gray-400 truncate">{{ conv.last_message or '' }}</div>
                                    </div>
                                    {% if conv.unread_count > 0 %}
                                    <span class="bg-[#AC0632] text-white text-[10px] px-1.5 py-0.5 rounded-full ml-auto font-black shrink-0">{{ conv.unread_count }}</span>
                                    {% endif %}
                                </a>
                                <div class="flex flex-col gap-1 shrink-0">
                                    {% if not show_archived %}
                                    <form action="/admin/support_archive" method="POST" class="m-0">
                                        <input type="hidden" name="conv_key" value="{{ conv.session_key }}">
                                        <input type="hidden" name="action" value="archive">
                                        <button title="Архівувати" class="w-7 h-7 flex items-center justify-center text-gray-300 hover:text-yellow-500 rounded-lg transition text-xs"><i class="fas fa-archive"></i></button>
                                    </form>
                                    {% else %}
                                    <form action="/admin/support_archive" method="POST" class="m-0">
                                        <input type="hidden" name="conv_key" value="{{ conv.session_key }}">
                                        <input type="hidden" name="action" value="unarchive">
                                        <button title="Відновити" class="w-7 h-7 flex items-center justify-center text-gray-300 hover:text-green-500 rounded-lg transition text-xs"><i class="fas fa-inbox"></i></button>
                                    </form>
                                    {% endif %}
                                    <form action="/admin/support_archive" method="POST" class="m-0" onsubmit="return confirm('Видалити цей діалог назавжди?')">
                                        <input type="hidden" name="conv_key" value="{{ conv.session_key }}">
                                        <input type="hidden" name="action" value="delete">
                                        <button title="Видалити" class="w-7 h-7 flex items-center justify-center text-gray-300 hover:text-red-600 rounded-lg transition text-xs"><i class="fas fa-trash"></i></button>
                                    </form>
                                </div>
                            </div>
                            {% else %}
                            <div class="p-6 text-center text-gray-400 text-sm italic">Немає повідомлень</div>
                            {% endfor %}
                        </div>
                    </div>
                    <div class="md:col-span-2 bg-white text-black rounded-3xl shadow-xl flex flex-col overflow-hidden" style="max-height:560px;">
                        {% if active_conv_key %}
                        <div class="p-4 bg-gray-50 border-b font-black text-sm flex items-center gap-2">
                            <i class="fas fa-user text-[#AC0632]"></i> {{ active_conv_sender or 'Гість' }}
                        </div>
                        <div class="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
                            {% for msg in active_conv_messages %}
                            <div class="flex gap-2 items-start {% if msg.sender_type == 'admin' %}flex-row-reverse{% endif %}">
                                <div class="{% if msg.sender_type == 'admin' %}bg-[#AC0632]{% else %}bg-gray-300{% endif %} text-white p-1.5 rounded-full w-7 h-7 flex items-center justify-center shrink-0">
                                    <i class="fas {% if msg.sender_type == 'admin' %}fa-user-shield{% else %}fa-user{% endif %} text-xs"></i>
                                </div>
                                <div class="{% if msg.sender_type == 'admin' %}bg-[#AC0632] text-white rounded-tr-none{% else %}bg-white rounded-tl-none{% endif %} rounded-2xl p-3 shadow-sm text-sm max-w-[75%]">
                                    {{ msg.message }}
                                    <div class="text-[10px] {% if msg.sender_type == 'admin' %}text-red-200{% else %}text-gray-400{% endif %} mt-1">{{ msg.created_at }}</div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                        <form action="/admin/support_reply" method="POST" class="p-4 border-t flex gap-2 bg-white">
                            <input type="hidden" name="conv_key" value="{{ active_conv_key }}">
                            <input type="hidden" name="last_msg_id" value="{{ active_conv_messages[-1].id if active_conv_messages else '' }}">
                            <input type="text" name="reply" placeholder="Відповідь..." required class="flex-1 p-2.5 rounded-xl bg-gray-100 border text-sm focus:border-[#AC0632] outline-none">
                            <button class="bg-[#AC0632] text-white px-4 py-2 rounded-xl hover:bg-red-800 transition font-bold"><i class="fas fa-paper-plane mr-1"></i> Надіслати</button>
                        </form>
                        {% else %}
                        <div class="flex-1 flex items-center justify-center text-gray-400 text-sm italic p-8 text-center">
                            <div><i class="fas fa-comments text-4xl mb-4 block"></i>Оберіть діалог зліва</div>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </section>
            {% endif %}

            <!-- ── ПРОФІЛЬ ── -->
            {% if active_tab == 'profile' %}
            <section class="max-w-4xl mx-auto">
                <div class="bg-white text-black rounded-[2rem] p-8 md:p-12 shadow-2xl relative">
                    {% if session.get('role') == 'ADMIN' %}
                    <div class="absolute top-4 right-4 bg-yellow-300 px-3 py-1 rounded-lg text-xs font-bold uppercase">Admin Mode</div>
                    {% endif %}
                    <h2 class="text-3xl font-black mb-6 uppercase border-b pb-4 flex items-center justify-between">
                        Редагування Профілю
                        <span class="text-sm bg-black text-white px-3 py-1 rounded-full font-normal">{{ user_info.role }}</span>
                    </h2>
                    <form action="/update_profile" method="POST" class="space-y-6">
                        <div class="bg-gray-50 p-4 rounded-xl border">
                            <label class="label-text">Логін / Email</label>
                            {% if session.get('role') == 'ADMIN' %}
                            <input type="email" name="email" value="{{ user_info.email or user_info.username or '' }}" class="w-full p-3 rounded-xl bg-white font-bold border focus:border-red-500" placeholder="email@example.com">
                            <p class="text-xs text-gray-400 mt-1">Логін і email є одним і тим самим.</p>
                            {% else %}
                            <input type="email" value="{{ user_info.email or user_info.username or '' }}" disabled class="w-full p-3 rounded-xl bg-gray-200 cursor-not-allowed font-mono">
                            <p class="text-xs text-gray-400 mt-1">Логін та email не можна змінювати самостійно.</p>
                            {% endif %}
                        </div>

                        {% if user_info.role == 'STUDENT' %}
                        {% if session.get('role') == 'ADMIN' %}
                        <div class="bg-yellow-50 p-4 rounded-xl border border-yellow-400 mb-6 shadow-inner">
                            <label class="label-text text-yellow-800"><i class="fas fa-star text-yellow-500"></i> Рейтинг Студента (Тільки для Адміністратора)</label>
                            <input type="number" name="rating" value="{{ profile_data.rating or 0 }}" class="w-full p-3 rounded-xl border-2 border-yellow-300 bg-white font-black text-xl">
                        </div>
                        {% endif %}
                        <div class="space-y-4">
                            <div class="grid md:grid-cols-3 gap-4">
                                <div>
                                    <label class="label-text">Прізвище</label>
                                    {% if session.get('role') == 'ADMIN' %}<input type="text" name="last_name" value="{{ profile_data.last_name or '' }}" class="w-full p-3 rounded-xl border">
                                    {% else %}<input type="text" value="{{ profile_data.last_name or '' }}" disabled class="w-full p-3 rounded-xl bg-gray-200 cursor-not-allowed"><input type="hidden" name="last_name" value="{{ profile_data.last_name or '' }}">{% endif %}
                                </div>
                                <div>
                                    <label class="label-text">Ім'я</label>
                                    {% if session.get('role') == 'ADMIN' %}<input type="text" name="first_name" value="{{ profile_data.first_name or '' }}" class="w-full p-3 rounded-xl border">
                                    {% else %}<input type="text" value="{{ profile_data.first_name or '' }}" disabled class="w-full p-3 rounded-xl bg-gray-200 cursor-not-allowed"><input type="hidden" name="first_name" value="{{ profile_data.first_name or '' }}">{% endif %}
                                </div>
                                <div>
                                    <label class="label-text">По батькові</label>
                                    {% if session.get('role') == 'ADMIN' %}<input type="text" name="patronymic" value="{{ profile_data.patronymic or '' }}" class="w-full p-3 rounded-xl border">
                                    {% else %}<input type="text" value="{{ profile_data.patronymic or '' }}" disabled class="w-full p-3 rounded-xl bg-gray-200 cursor-not-allowed"><input type="hidden" name="patronymic" value="{{ profile_data.patronymic or '' }}">{% endif %}
                                </div>
                            </div>
                            {% if session.get('role') != 'ADMIN' %}<p class="text-xs text-gray-400 -mt-2"><i class="fas fa-lock mr-1"></i> ПІБ може редагувати лише адміністратор.</p>{% endif %}
                            <div class="grid md:grid-cols-2 gap-4">
                                <div>
                                    <label class="label-text">Курс</label>
                                    {% if session.get('role') == 'ADMIN' %}<input type="number" name="course" value="{{ profile_data.course or '' }}" class="w-full p-3 rounded-xl border" placeholder="1-6">
                                    {% else %}<input type="number" value="{{ profile_data.course or '' }}" disabled class="w-full p-3 rounded-xl bg-gray-200 cursor-not-allowed"><input type="hidden" name="course" value="{{ profile_data.course or '' }}">{% endif %}
                                </div>
                                <div>
                                    <label class="label-text">Спеціальність</label>
                                    {% if session.get('role') == 'ADMIN' %}<input type="text" name="specialty" value="{{ profile_data.specialty or '' }}" class="w-full p-3 rounded-xl border">
                                    {% else %}<input type="text" value="{{ profile_data.specialty or '' }}" disabled class="w-full p-3 rounded-xl bg-gray-200 cursor-not-allowed"><input type="hidden" name="specialty" value="{{ profile_data.specialty or '' }}">{% endif %}
                                </div>
                            </div>
                            <div class="grid md:grid-cols-[auto_1fr] gap-4 items-start pt-2">
                                <img src="{{ profile_data.avatar }}" class="w-20 h-20 rounded-full border bg-gray-100 object-cover">
                                <div>
                                    <label class="label-text">Посилання на фото (Аватар)</label>
                                    <input type="text" name="avatar" value="{{ profile_data.avatar or '' }}" class="w-full p-3 rounded-xl border" placeholder="https://...">
                                </div>
                            </div>
                            <label class="label-text">Навички (через кому)</label>
                            <textarea name="skills" class="w-full p-3 rounded-xl border h-20" placeholder="Python, SQL, Figma...">{{ profile_data.skills or '' }}</textarea>
                            <hr class="my-4">
                            <h3 class="font-black text-red-700 uppercase mb-2">Контакти та Зв'язок</h3>
                            <div>
                                <label class="label-text">Контактна інформація</label>
                                <input type="text" name="contact_info" value="{{ profile_data.contact_info or '' }}" class="w-full p-3 rounded-xl border" placeholder="+380... або @username">
                            </div>
                            <div>
                                <label class="label-text">Link (GitHub, LinkedIn, Портфоліо)</label>
                                <input type="text" name="links" value="{{ profile_data.links or '' }}" class="w-full p-3 rounded-xl border" placeholder="https://github.com/...">
                                <p class="text-xs text-gray-500 mt-1">Додайте посилання через кому.</p>
                            </div>
                        </div>

                        {% elif user_info.role in ['COMPANY', 'COMPANY_ADMIN', 'EMPLOYEE'] %}
                        <div class="space-y-4">
                            <div>
                                <label class="label-text text-blue-800">Назва Компанії</label>
                                <input type="text" name="company_name" value="{{ profile_data.company_name or '' }}" class="w-full p-3 rounded-xl border-2 border-blue-100 font-bold text-lg">
                            </div>
                            <div>
                                <label class="label-text text-blue-800">Ваша Посада</label>
                                <input type="text" name="position" value="{{ profile_data.position or '' }}" class="w-full p-3 rounded-xl border-2 border-blue-100 font-bold">
                            </div>
                            <div class="grid md:grid-cols-[auto_1fr] gap-4 items-start bg-blue-50 p-4 rounded-xl">
                                <img src="{{ profile_data.avatar }}" class="w-24 h-24 rounded-lg border bg-white object-contain">
                                <div class="w-full">
                                    <label class="label-text text-blue-800">Логотип Компанії (URL)</label>
                                    <input type="text" name="avatar" value="{{ profile_data.avatar or '' }}" class="w-full p-3 rounded-xl border">
                                </div>
                            </div>
                            <div>
                                <label class="label-text text-blue-800">Контактна інформація</label>
                                <input type="text" name="contact_info" value="{{ profile_data.contact_info or '' }}" class="w-full p-3 rounded-xl border-2 border-blue-100">
                            </div>
                            <div>
                                <label class="label-text text-blue-800">Опис Компанії / Вакансії</label>
                                <textarea name="description" class="w-full p-3 rounded-xl border h-32">{{ profile_data.description or '' }}</textarea>
                            </div>
                        </div>
                        {% endif %}

                        <button type="submit" class="w-full bg-black text-white py-4 rounded-xl font-black uppercase tracking-widest hover:bg-red-700 transition transform hover:-translate-y-1 shadow-xl">
                            Зберегти Профіль
                        </button>
                    </form>

                    {% if session.get('role') == 'ADMIN' %}
                    <div class="mt-12 pt-8 border-t-2 border-dashed border-gray-300">
                        <h3 class="font-bold mb-4">Адмін: Редагувати іншого користувача</h3>
                        <form action="/admin/select_user" method="POST" class="flex gap-2">
                            <input type="number" name="target_user_id" placeholder="ID" class="p-3 rounded-xl border-2 border-black w-24 text-center">
                            <button class="bg-yellow-400 text-black px-6 rounded-xl font-bold uppercase hover:bg-yellow-500">Вибрати</button>
                        </form>
                    </div>
                    {% endif %}
                </div>
            </section>
            {% endif %}

        </div>
        {% endif %}

    <!-- ════ ГЛОБАЛЬНИЙ ЧАТ ПІДТРИМКИ (доступний на ВСІХ вкладках) ════ -->
    {% if session.get('user_id') and session.get('role') != 'ADMIN' %}

    <!-- Плаваюча кнопка -->
    <button onclick="toggleUserChat()" id="support-float-btn"
        class="fixed bottom-6 right-6 z-[199] bg-[#AC0632] hover:bg-red-800 text-white w-14 h-14 rounded-full shadow-2xl flex items-center justify-center transition-all transform hover:scale-110 border-2 border-white/30"
        title="Підтримка">
        <i class="fas fa-headset text-xl"></i>
        <span id="support-float-badge"
            class="hidden absolute -top-1 -right-1 bg-yellow-400 text-black text-[10px] w-5 h-5 rounded-full font-black items-center justify-center">!</span>
    </button>

    <!-- Вікно чату — особистий чат кожного юзера окремо -->
    <div id="user-support-chat"
        class="hidden fixed bottom-24 right-6 z-[200] w-96 bg-white rounded-3xl shadow-2xl flex flex-col border border-gray-200"
        style="max-height:520px;">
        <!-- Заголовок -->
        <div class="flex items-center justify-between p-4 bg-[#AC0632] rounded-t-3xl">
            <div class="flex items-center gap-3">
                <div class="bg-white p-2 rounded-full"><i class="fas fa-headset text-[#AC0632]"></i></div>
                <div>
                    <div class="text-white font-black uppercase">Підтримка УКД</div>
                    <div class="text-red-200 text-xs">{{ session.get('username') }} · особистий чат</div>
                </div>
            </div>
            <button onclick="toggleUserChat()" class="text-white text-2xl hover:text-red-200 leading-none">&times;</button>
        </div>
        <!-- Повідомлення -->
        <div id="user-chat-messages"
            class="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50"
            style="min-height:200px; max-height:320px;">
            <div class="flex gap-2 items-start">
                <div class="bg-[#AC0632] text-white p-1.5 rounded-full w-7 h-7 flex items-center justify-center shrink-0">
                    <i class="fas fa-robot text-xs"></i>
                </div>
                <div class="bg-white rounded-2xl rounded-tl-none p-3 shadow-sm text-sm">
                    Вітаємо, <b>{{ session.get('username') }}</b>! Це ваш особистий чат з підтримкою.
                </div>
            </div>
        </div>
        <!-- Поле вводу -->
        <div class="p-3 border-t border-gray-100 bg-white rounded-b-3xl">
            <div class="flex gap-2">
                <input type="text" id="user-chat-input"
                    placeholder="Напишіть повідомлення..."
                    class="flex-1 p-2.5 rounded-xl bg-gray-100 border text-sm focus:border-[#AC0632] outline-none"
                    onkeydown="if(event.key==='Enter') sendUserMessage()">
                <button onclick="sendUserMessage()"
                    class="bg-[#AC0632] text-white px-3 py-2 rounded-xl hover:bg-red-800 transition">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        </div>
    </div>
    {% endif %}

    </main>

    <!-- ═══════════════════════ МОДАЛЬНІ ВІКНА ═══════════════════════ -->

    <!-- Вхід -->
    <div id="login-modal" class="hidden fixed inset-0 modal-bg z-[100] flex items-center justify-center p-4">
        <div class="bg-white text-black p-8 rounded-3xl w-full max-w-sm relative shadow-2xl">
            <button onclick="toggleModal('login-modal')" class="absolute top-4 right-4 text-2xl font-bold hover:text-red-600">&times;</button>
            <h2 class="text-3xl font-black mb-6 text-center uppercase">Вхід</h2>
            <form action="/login" method="POST" class="space-y-4">
                <input type="text" name="username" placeholder="Логін" required class="w-full p-3 rounded-xl font-bold bg-gray-100 border focus:border-black">
                <input type="password" name="password" placeholder="Пароль" required class="w-full p-3 rounded-xl font-bold bg-gray-100 border focus:border-black">
                <button class="w-full bg-black text-white py-3 rounded-xl font-black uppercase hover:bg-red-700 transition">Увійти</button>
            </form>
        </div>
    </div>

    <!-- Створити компанію (Admin) -->
    <div id="create-company-modal" class="hidden fixed inset-0 modal-bg z-[100] flex items-center justify-center p-4">
        <div class="bg-white text-black p-8 rounded-3xl w-full max-w-md relative shadow-2xl">
            <button onclick="toggleModal('create-company-modal')" class="absolute top-4 right-4 text-2xl font-bold hover:text-red-600">&times;</button>
            <h2 class="text-2xl font-black mb-6 uppercase"><i class="fas fa-building mr-2 text-red-600"></i>Створити Компанію</h2>
            <form action="/admin/create_company" method="POST" class="space-y-4">
                <div>
                    <label class="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Назва компанії</label>
                    <input type="text" name="company_name" required placeholder="TechUkraine LLC" class="w-full p-3 rounded-xl bg-gray-50 border-2 border-gray-100 focus:border-red-600 outline-none">
                </div>
                <div>
                    <label class="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Email директора (логін)</label>
                    <input type="email" name="email" required placeholder="director@company.com" class="w-full p-3 rounded-xl bg-gray-50 border-2 border-gray-100 focus:border-red-600 outline-none">
                </div>
                <div>
                    <label class="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Логін директора</label>
                    <input type="text" name="username" required placeholder="company_admin" class="w-full p-3 rounded-xl bg-gray-50 border-2 border-gray-100 focus:border-red-600 outline-none">
                </div>
                <div>
                    <label class="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Пароль</label>
                    <input type="password" name="password" required placeholder="••••••••" class="w-full p-3 rounded-xl bg-gray-50 border-2 border-gray-100 focus:border-red-600 outline-none">
                </div>
                <button type="submit" class="w-full bg-red-600 text-white py-3 rounded-xl font-black uppercase hover:bg-red-700 transition">Створити компанію</button>
            </form>
        </div>
    </div>

    <!-- Запрошення -->
    <div id="invite-modal" class="hidden fixed inset-0 modal-bg z-[100] flex items-center justify-center p-4">
        <div class="bg-white text-black p-8 rounded-3xl w-full max-w-md relative shadow-2xl">
            <button onclick="toggleModal('invite-modal')" class="absolute top-4 right-4 text-2xl font-bold">&times;</button>
            <h2 class="text-2xl font-black mb-2 uppercase text-red-700">Найняти Студента</h2>
            <p id="invite-student-name" class="text-xl font-bold mb-6">...</p>
            <form action="/send_invite" method="POST" class="space-y-4">
                <input type="hidden" name="student_id" id="invite-student-id">
                <textarea name="message" placeholder="Напишіть коротке повідомлення..." required class="w-full p-4 rounded-xl bg-gray-100 h-32 border focus:border-black"></textarea>
                <button class="w-full bg-green-600 text-white py-3 rounded-xl font-black uppercase hover:bg-green-700 transition">Надіслати Запрошення</button>
            </form>
        </div>
    </div>

    <!-- Перегляд студента -->
    <div id="student-view-modal" class="hidden fixed inset-0 modal-bg z-[100] flex items-center justify-center p-4">
        <div class="bg-white text-black p-0 rounded-3xl w-full max-w-lg relative shadow-2xl overflow-hidden">
            <button onclick="toggleModal('student-view-modal')" class="absolute top-4 right-4 text-gray-400 hover:text-red-600 text-3xl font-light transition z-50">&times;</button>
            <div class="px-8 pb-8 text-center pt-10">
                <div class="w-32 h-32 mx-auto mb-4">
                    <img id="sv-avatar" src="" class="w-full h-full rounded-full border-4 border-gray-100 shadow-md object-contain bg-white p-1">
                </div>
                <h2 id="sv-name" class="text-3xl font-black uppercase tracking-tight"></h2>
                <p id="sv-spec" class="text-red-600 font-bold mb-6 text-lg"></p>
                <div class="text-left bg-gray-50 p-6 rounded-2xl space-y-4 text-sm border border-gray-200">
                    <div>
                        <span class="block text-xs font-bold uppercase text-gray-400 mb-1">Навички</span>
                        <p id="sv-skills" class="font-medium bg-white p-2 rounded border border-gray-100"></p>
                    </div>
                    <div>
                        <span class="block text-xs font-bold uppercase text-gray-400 mb-1">Контактна інформація</span>
                        <p id="sv-contact-info" class="font-bold text-gray-800 bg-white p-2 rounded border border-gray-100 truncate"></p>
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <span class="block text-xs font-bold uppercase text-gray-400 mb-1">Link (Мережі)</span>
                            <div id="sv-links" class="text-blue-600 flex gap-3 flex-wrap mt-1"></div>
                        </div>
                        <div>
                            <span class="block text-xs font-bold uppercase text-gray-400 mb-1">Email</span>
                            <p id="sv-email" class="text-gray-800 font-bold truncate mt-1"></p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Додати робітника (Admin) -->
    <div id="add-employee-modal" class="hidden fixed inset-0 modal-bg z-[100] flex items-center justify-center p-4">
        <div class="bg-white text-black rounded-3xl w-full max-w-lg relative shadow-2xl border-l-8 border-red-600 overflow-hidden">
            <div class="bg-gradient-to-r from-[#AC0632] to-red-800 p-6">
                <button onclick="toggleModal('add-employee-modal')" class="absolute top-4 right-5 text-white/70 hover:text-white text-2xl font-bold transition">&times;</button>
                <div class="flex items-center gap-3">
                    <div class="bg-white/20 p-3 rounded-xl"><i class="fas fa-user-plus text-white text-xl"></i></div>
                    <div>
                        <h2 class="text-2xl font-black text-white uppercase tracking-tight">Новий Робітник</h2>
                        <p class="text-red-200 text-sm">Додавання працівника до компанії</p>
                    </div>
                </div>
            </div>
            <form action="/admin/add_employee" method="POST" class="p-6 space-y-4">
                <div>
                    <label class="block text-xs font-black text-gray-500 uppercase tracking-widest mb-2"><i class="fas fa-building text-[#AC0632] mr-1"></i> Компанія</label>
                    <div class="relative">
                        <input type="text" id="company-search-input" placeholder="Пошук компанії..." autocomplete="off" class="w-full p-3 pl-10 rounded-xl bg-gray-50 border-2 border-gray-200 focus:border-[#AC0632] outline-none text-sm transition" oninput="filterCompanies(this.value)">
                        <i class="fas fa-search absolute left-3 top-3.5 text-gray-400 text-sm"></i>
                    </div>
                    <div id="company-dropdown" class="mt-1 border-2 border-gray-200 rounded-xl overflow-hidden hidden" style="max-height:180px;overflow-y:auto;">
                        {% for comp in all_companies %}
                        <div class="company-option flex items-center gap-3 p-3 hover:bg-red-50 cursor-pointer transition border-b border-gray-100 last:border-0" data-id="{{ comp.id }}" data-name="{{ comp.company_name }}" onclick="selectCompany({{ comp.id }}, '{{ comp.company_name }}')">
                            <img src="{{ comp.avatar or 'https://cdn-icons-png.flaticon.com/512/3061/3061341.png' }}" class="w-8 h-8 rounded-lg object-contain bg-gray-100 border shrink-0">
                            <div>
                                <div class="font-bold text-sm">{{ comp.company_name }}</div>
                                {% if comp.contact_info %}<div class="text-xs text-gray-400">{{ comp.contact_info }}</div>{% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    <div id="selected-company-display" class="hidden mt-2 flex items-center gap-3 bg-red-50 border-2 border-red-200 p-3 rounded-xl">
                        <i class="fas fa-check-circle text-[#AC0632]"></i>
                        <span id="selected-company-name" class="font-bold text-sm text-[#AC0632]"></span>
                        <button type="button" onclick="clearCompany()" class="ml-auto text-gray-400 hover:text-red-600 text-xs">✕ Змінити</button>
                    </div>
                    <input type="hidden" name="company_id" id="company-id-hidden" required>
                </div>
                <div>
                    <label class="block text-xs font-black text-gray-500 uppercase tracking-widest mb-2"><i class="fas fa-envelope text-[#AC0632] mr-1"></i> Email / Логін</label>
                    <input type="email" name="email" required placeholder="hr@company.com" class="w-full p-3 rounded-xl bg-gray-50 border-2 border-gray-200 focus:border-[#AC0632] outline-none transition text-sm">
                </div>
                <div>
                    <label class="block text-xs font-black text-gray-500 uppercase tracking-widest mb-2"><i class="fas fa-briefcase text-[#AC0632] mr-1"></i> Посада</label>
                    <input type="text" name="position" required placeholder="HR Менеджер, Рекрутер..." class="w-full p-3 rounded-xl bg-gray-50 border-2 border-gray-200 focus:border-[#AC0632] outline-none transition text-sm">
                </div>
                <div>
                    <label class="block text-xs font-black text-gray-500 uppercase tracking-widest mb-2"><i class="fas fa-lock text-[#AC0632] mr-1"></i> Пароль</label>
                    <div class="relative">
                        <input type="password" name="password" id="emp-password" required placeholder="••••••••" class="w-full p-3 pr-12 rounded-xl bg-gray-50 border-2 border-gray-200 focus:border-[#AC0632] outline-none transition text-sm">
                        <button type="button" onclick="toggleEmpPassword()" class="absolute right-3 top-3 text-gray-400 hover:text-gray-700 transition"><i class="fas fa-eye" id="emp-pass-eye"></i></button>
                    </div>
                </div>
                <button type="submit" id="add-emp-submit-btn" disabled class="w-full bg-gray-300 text-gray-500 py-3.5 rounded-xl font-black uppercase tracking-widest transition cursor-not-allowed">
                    <i class="fas fa-user-plus mr-2"></i>Додати Робітника
                </button>
                <p id="add-emp-hint" class="text-xs text-center text-gray-400">Спочатку оберіть компанію</p>
            </form>
        </div>
    </div>

    <!-- ═══════════════════════ JAVASCRIPT ═══════════════════════ -->
    <script>
        function toggleModal(id) {
            document.getElementById(id).classList.toggle('hidden');
        }

        // Admin: company search dropdown
        function filterCompanies(val) {
            const dropdown = document.getElementById('company-dropdown');
            const options = dropdown.querySelectorAll('.company-option');
            const q = val.toLowerCase().trim();
            dropdown.classList.remove('hidden');
            let visible = 0;
            options.forEach(opt => {
                const name = opt.dataset.name.toLowerCase();
                const show = !q || name.includes(q);
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
            const inp = document.getElementById('company-search-input');
            const drop = document.getElementById('company-dropdown');
            if (inp && drop && !inp.contains(e.target) && !drop.contains(e.target)) drop.classList.add('hidden');
        });

        function toggleEmpPassword() {
            const inp = document.getElementById('emp-password');
            const eye = document.getElementById('emp-pass-eye');
            if (inp.type === 'password') { inp.type = 'text'; eye.className = 'fas fa-eye-slash'; }
            else { inp.type = 'password'; eye.className = 'fas fa-eye'; }
        }

        // Guest support chat
        function sendGuestMessage() {
            const input = document.getElementById('guest-chat-input');
            const nameInput = document.getElementById('guest-name-input');
            const msg = input.value.trim();
            if (!msg) return;
            const messagesDiv = document.getElementById('guest-chat-messages');
            messagesDiv.innerHTML += `<div class="flex gap-2 items-start flex-row-reverse">
                <div class="bg-gray-300 p-1.5 rounded-full w-7 h-7 flex items-center justify-center shrink-0"><i class="fas fa-user text-xs text-gray-600"></i></div>
                <div class="bg-white rounded-2xl rounded-tr-none p-3 shadow-sm text-sm max-w-[80%]">${msg}</div>
            </div>`;
            fetch('/support/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: `message=${encodeURIComponent(msg)}&sender_name=${encodeURIComponent(nameInput.value || 'Гість')}`
            }).then(() => {
                messagesDiv.innerHTML += `<div class="flex gap-2 items-start">
                    <div class="bg-[#AC0632] text-white p-1.5 rounded-full w-7 h-7 flex items-center justify-center shrink-0"><i class="fas fa-robot text-xs"></i></div>
                    <div class="bg-white rounded-2xl rounded-tl-none p-3 shadow-sm text-sm">Дякуємо! Адміністратор отримав ваше повідомлення і відповість найближчим часом.</div>
                </div>`;
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            });
            input.value = '';
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        // ══ ОСОБИСТИЙ ЧАТ ПІДТРИМКИ (унікальний для кожного user_id) ══════════
        let _lastMsgId = 0;
        let _pollingInterval = null;

        // Відкрити/закрити чат
        function toggleUserChat() {
            const chat  = document.getElementById('user-support-chat');
            const badge = document.getElementById('support-float-badge');
            if (!chat) return;
            const isOpen = !chat.classList.contains('hidden');
            if (isOpen) {
                chat.classList.add('hidden');
            } else {
                chat.classList.remove('hidden');
                if (badge) badge.classList.add('hidden'); // прибираємо бейдж
                loadUserChatHistory(); // завантажуємо СВОЮ історію
            }
        }

        // Рендер одного повідомлення
        function renderMsg(m) {
            const isAdmin = m.sender_type === 'admin';
            return `<div class="flex gap-2 items-start ${isAdmin ? '' : 'flex-row-reverse'}">
                <div class="${isAdmin ? 'bg-[#AC0632]' : 'bg-gray-300'} text-white p-1.5 rounded-full w-7 h-7 flex items-center justify-center shrink-0">
                    <i class="fas ${isAdmin ? 'fa-user-shield' : 'fa-user'} text-xs"></i>
                </div>
                <div class="${isAdmin ? 'bg-[#AC0632] text-white rounded-tl-none' : 'bg-white rounded-tr-none'} rounded-2xl p-3 shadow-sm text-sm max-w-[75%]">${m.message}</div>
            </div>`;
        }

        // Завантажити повну історію чату ЦЬОГО юзера
        function loadUserChatHistory() {
            fetch('/support/history')
                .then(r => r.json())
                .then(msgs => {
                    const div = document.getElementById('user-chat-messages');
                    if (!div) return;
                    if (msgs.length > 0) {
                        div.innerHTML = ''; // прибираємо привітальне
                        msgs.forEach(m => {
                            div.innerHTML += renderMsg(m);
                            if (m.id > _lastMsgId) _lastMsgId = m.id;
                        });
                        div.scrollTop = div.scrollHeight;
                    }
                    // Запускаємо polling якщо ще не запущений
                    if (!_pollingInterval) {
                        _pollingInterval = setInterval(checkNewAdminMessages, 3000);
                    }
                });
        }

        // Перевірити нові відповіді адміна (тільки для ЦЬОГО юзера)
        function checkNewAdminMessages() {
            fetch('/support/check_new?last_id=' + _lastMsgId)
                .then(r => r.json())
                .then(msgs => {
                    if (!msgs.length) return;
                    const div   = document.getElementById('user-chat-messages');
                    const chat  = document.getElementById('user-support-chat');
                    const badge = document.getElementById('support-float-badge');
                    msgs.forEach(m => {
                        if (m.id > _lastMsgId) _lastMsgId = m.id;
                        // Якщо чат відкритий — показуємо одразу
                        if (chat && !chat.classList.contains('hidden') && div) {
                            div.innerHTML += renderMsg(m);
                            div.scrollTop = div.scrollHeight;
                        } else {
                            // Чат закритий — показуємо бейдж на кнопці
                            if (badge) {
                                badge.classList.remove('hidden');
                                badge.style.display = 'flex';
                            }
                        }
                    });
                });
        }

        // Надіслати повідомлення
        function sendUserMessage() {
            const input = document.getElementById('user-chat-input');
            const msg   = input.value.trim();
            if (!msg) return;
            const div = document.getElementById('user-chat-messages');

            // Одразу показуємо своє повідомлення
            div.innerHTML += `<div class="flex gap-2 items-start flex-row-reverse">
                <div class="bg-gray-300 p-1.5 rounded-full w-7 h-7 flex items-center justify-center shrink-0">
                    <i class="fas fa-user text-xs text-gray-600"></i>
                </div>
                <div class="bg-white rounded-2xl rounded-tr-none p-3 shadow-sm text-sm max-w-[75%]">${msg}</div>
            </div>`;
            div.scrollTop = div.scrollHeight;
            input.value = '';

            fetch('/support/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: `message=${encodeURIComponent(msg)}`
            }).then(r => r.json()).then(data => {
                if (data.ok) {
                    div.innerHTML += `<div class="flex gap-2 items-start">
                        <div class="bg-[#AC0632] text-white p-1.5 rounded-full w-7 h-7 flex items-center justify-center shrink-0">
                            <i class="fas fa-robot text-xs"></i>
                        </div>
                        <div class="bg-white rounded-2xl rounded-tl-none p-3 shadow-sm text-sm">
                            ✅ Повідомлення надіслано! Адміністратор відповість незабаром.
                        </div>
                    </div>`;
                    div.scrollTop = div.scrollHeight;
                    // Запускаємо polling якщо ще не запущений
                    if (!_pollingInterval) {
                        _pollingInterval = setInterval(checkNewAdminMessages, 3000);
                    }
                }
            });
        }

        // Запускаємо polling одразу при завантаженні сторінки
        // (щоб бейдж з'явився навіть якщо чат ще не відкривали)
        document.addEventListener('DOMContentLoaded', function() {
            const btn = document.getElementById('support-float-btn');
            if (btn) {
                _pollingInterval = setInterval(checkNewAdminMessages, 5000);
            }
        });

        function openInviteModal(id, name) {
            document.getElementById('invite-student-id').value = id;
            document.getElementById('invite-student-name').innerText = name;
            toggleModal('invite-modal');
        }

        function openStudentProfile(userId) {
            fetch('/api/student/' + userId)
                .then(r => r.json())
                .then(data => {
                    if (data.error) return alert(data.error);
                    document.getElementById('sv-avatar').src = data.avatar || '';
                    let fullName = [data.last_name, data.first_name, data.patronymic].filter(Boolean).join(' ');
                    document.getElementById('sv-name').innerText = fullName || 'Студент';
                    let specText = [];
                    if (data.course) specText.push(data.course + ' курс');
                    if (data.specialty) specText.push(data.specialty);
                    document.getElementById('sv-spec').innerText = specText.join(', ') || 'Студент';
                    document.getElementById('sv-skills').innerText = data.skills || '-';
                    document.getElementById('sv-contact-info').innerText = data.contact_info || '-';
                    let linksHtml = '';
                    if (data.links && data.links.trim() !== '') {
                        data.links.split(',').map(l => l.trim()).forEach(url => {
                            if (!url) return;
                            let href = url.startsWith('http') ? url : 'https://' + url;
                            let iconClass = 'fas fa-link';
                            if (url.toLowerCase().includes('github')) iconClass = 'fab fa-github';
                            if (url.toLowerCase().includes('linkedin')) iconClass = 'fab fa-linkedin';
                            linksHtml += `<a href="${href}" target="_blank" class="text-2xl hover:text-red-600 transition"><i class="${iconClass}"></i></a>`;
                        });
                    } else { linksHtml = '-'; }
                    document.getElementById('sv-links').innerHTML = linksHtml;
                    document.getElementById('sv-email').innerText = data.email || '';
                    toggleModal('student-view-modal');
                });
        }
    </script>
</body>
</html>
"""

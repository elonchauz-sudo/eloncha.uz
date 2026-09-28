import os
import time
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'maxfiy_kalit_soz_super_xavfsiz_2026'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ma'lumotlar bazasi (Xotirada saqlash uchun)
USERS_DB = [
    {'id': 1, 'name': 'Dilshod', 'phone': '+998901234567', 'password': '123'}
]

# 12 ta Asosiy kategoriya va ularning sub-kategoriyalari
CATEGORIES_STRUCTURE = {
    "🏠 Uy-joy": ["Uy", "Kvartira", "Yer", "Ijara", "Tijorat binolari"],
    "🚗 Avtomobil": ["Yengil avtomobil", "Yuk mashinasi", "Moto", "Ehtiyot qismlar", "Avto xizmatlar"],
    "💼 Ish va vakansiyalar": ["Ish qidiraman", "Ishchi kerak", "Masofaviy ish", "Xizmat ko‘rsatish"],
    "📱 Elektronika": ["Telefon", "Kompyuter", "Noutbuk", "Televizor", "Aksessuarlar"],
    "🛋️ Uy va mebel": ["Mebel", "Maishiy texnika", "Uy jihozlari"],
    "👕 Kiyim-kechak": ["Erkaklar", "Ayollar", "Bolalar", "Oyoq kiyim"],
    "🛒 Tovarlar": ["Yangi", "Ishlatilgan", "Shaxsiy savdo"],
    "🛠️ Xizmatlar": ["Ta’mirlash", "Yetkazib berish", "Usta xizmatlari", "IT xizmatlar", "Boshqa xizmatlar"],
    "🐄 Hayvonlar": ["Uy hayvonlari", "Chorva", "Qushlar"],
    "📚 Ta’lim": ["Kurslar", "Repetitor", "O‘quv markazlari"],
    "🎮 Hobbi va ko‘ngilochar": ["O‘yinlar", "Sport", "Musiqa", "To‘plamlar"],
    "📦 Boshqa": ["Boshqa"]
}

# Har bir kategoriya uchun o'ziga xos ranglar (Badges uchun)
CATEGORY_COLORS = {
    "🏠 Uy-joy": "bg-blue-600 text-white",
    "🚗 Avtomobil": "bg-emerald-600 text-white",
    "💼 Ish va vakansiyalar": "bg-purple-600 text-white",
    "📱 Elektronika": "bg-amber-600 text-white",
    "🛋️ Uy va mebel": "bg-rose-600 text-white",
    "👕 Kiyim-kechak": "bg-indigo-600 text-white",
    "🛒 Tovarlar": "bg-cyan-600 text-white",
    "🛠️ Xizmatlar": "bg-teal-600 text-white",
    "🐄 Hayvonlar": "bg-orange-600 text-white",
    "📚 Ta’lim": "bg-pink-600 text-white",
    "🎮 Hobbi va ko‘ngilochar": "bg-violet-600 text-white",
    "📦 Boshqa": "bg-slate-600 text-white"
}

REGIONS = [
    "Toshkent shahri", "Farg'ona viloyati", "Andijon viloyati", 
    "Namangan viloyati", "Samarqand viloyati", "Buxoro viloyati", 
    "Qashqadaryo viloyati", "Surxondaryo viloyati", "Jizzax viloyati", 
    "Sirdaryo viloyati", "Navoiy viloyati", "Xorazm viloyati", 
    "Qoraqalpog'iston Respublikasi"
]

JOBS_DB = [
    {
        'id': 1,
        'title': 'Senior Python Developer (AI & Backend)',
        'company': 'Tech Solutions Global',
        'category': '💼 Ish va vakansiyalar',
        'sub_category': 'Masofaviy ish',
        'region': 'Toshkent shahri',
        'salary': '12 000 000 - 18 000 000 so\'m',
        'description': 'Sun\'iy intellekt texnologiyalarida yuqori darajadagi dasturlarni yaratish.',
        'phone': '+998901234567',
        'job_img': '',     
        'check_img': '',   
        'status': 'active',
        'user_id': 1,
        'views': 142,
        'likes': 25,
        'comments_list': [{'user': 'Aziz', 'text': 'Zo‘r imkoniyat!'}],
        'badge_color': 'bg-purple-600 text-white'
    }
]

# Tizim bildirishnomalari (Admin tomonidan yuboriladi)
NOTIFICATIONS_DB = [
    {'id': 1, 'text': 'eloncha.uz platformasiga xush kelibsiz! Yangi imkoniyatlar qo‘shildi.', 'date': '2026-09-28'}
]
# Foydalanuvchilar o'qigan bildirishnoma ID lari
USER_READ_NOTIFICATIONS = {}

@app.route('/')
def index():
    query = request.args.get('q', '').lower()
    selected_region = request.args.get('region', 'Barchasi')
    selected_category = request.args.get('category', 'Barchasi')
    
    filtered_jobs = [j for j in JOBS_DB if j['status'] == 'active']
    
    if query:
        filtered_jobs = [j for j in filtered_jobs if query in j['title'].lower() or query in j['description'].lower()]
    if selected_region and selected_region != 'Barchasi':
        filtered_jobs = [j for j in filtered_jobs if j['region'] == selected_region]
    if selected_category and selected_category != 'Barchasi':
        filtered_jobs = [j for j in filtered_jobs if j['category'] == selected_category]

    # Bildirishnoma qizil nishonini tekshirish
    unread_notifs = 0
    user_id = session.get('user_id')
    if user_id:
        read_list = USER_READ_NOTIFICATIONS.get(user_id, [])
        unread_notifs = len([n for n in NOTIFICATIONS_DB if n['id'] not in read_list])
    else:
        unread_notifs = len(NOTIFICATIONS_DB)

    return render_template('index.html', jobs=filtered_jobs, categories=CATEGORIES_STRUCTURE, regions=REGIONS, 
                           selected_region=selected_region, selected_category=selected_category, query=query,
                           unread_notifs=unread_notifs)

@app.route('/ad/<int:job_id>')
def view_ad(job_id):
    job = next((j for j in JOBS_DB if j['id'] == job_id), None)
    if not job:
        return redirect(url_for('index'))
    
    # Ko'rsatishlar sonini oshirish
    job['views'] = job.get('views', 0) + 1
    return render_template('view_ad.html', job=job)

@app.route('/ad/<int:job_id>/like', methods=['POST'])
def like_ad(job_id):
    job = next((j for j in JOBS_DB if j['id'] == job_id), None)
    if job:
        job['likes'] = job.get('likes', 0) + 1
    return redirect(url_for('view_ad', job_id=job_id))

@app.route('/ad/<int:job_id>/comment', methods=['POST'])
def add_comment(job_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    job = next((j for j in JOBS_DB if j['id'] == job_id), None)
    comment_text = request.form.get('comment_text')
    if job and comment_text:
        if 'comments_list' not in job:
            job['comments_list'] = []
        job['comments_list'].append({'user': session.get('user_name', 'Foydalanuvchi'), 'text': comment_text})
    return redirect(url_for('view_ad', job_id=job_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        user = next((u for u in USERS_DB if u['phone'] == phone and u['password'] == password), None)
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['is_admin'] = False
            return redirect(url_for('index'))
        else:
            error = "Telefon raqam yoki parol noto'g'ri!"
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        if any(u['phone'] == phone for u in USERS_DB):
            error = "Bu raqam allaqachon ro'yxatdan o'tgan!"
        else:
            new_user = {'id': len(USERS_DB) + 1, 'name': name, 'phone': phone, 'password': password}
            USERS_DB.append(new_user)
            session['user_id'] = new_user['id']
            session['user_name'] = new_user['name']
            session['is_admin'] = False
            return redirect(url_for('index'))
    return render_template('register.html', error=error)

@app.route('/get-subcategories/<category_name>')
def get_subcategories(category_name):
    # AJAX orqali sub-kategoriyalarni qaytarish uchun
    subs = CATEGORIES_STRUCTURE.get(category_name, [])
    return jsonify(subs)

@app.route('/add-job', methods=['GET', 'POST'])
def add_job():
    if not session.get('user_id'):
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        job_filename = ''
        job_file = request.files.get('job_img')
        if job_file and job_file.filename != '':
            filename = secure_filename(job_file.filename)
            unique_filename = f"job_{int(time.time())}_{filename}"
            job_file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            job_filename = unique_filename

        check_filename = ''
        check_file = request.files.get('check_img')
        if check_file and check_file.filename != '':
            filename = secure_filename(check_file.filename)
            unique_filename = f"check_{int(time.time())}_{filename}"
            check_file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            check_filename = unique_filename

        category = request.form.get('category')
        badge_color = CATEGORY_COLORS.get(category, "bg-gray-600 text-white")

        new_job = {
            'id': len(JOBS_DB) + 1,
            'title': request.form.get('title'),
            'company': request.form.get('company', ''),
            'category': category,
            'sub_category': request.form.get('sub_category'),
            'region': request.form.get('region'),
            'salary': request.form.get('salary'),
            'description': request.form.get('description'),
            'phone': request.form.get('phone'),
            'job_img': job_filename,
            'check_img': check_filename,
            'status': 'pending',
            'user_id': session.get('user_id'),
            'views': 0,
            'likes': 0,
            'comments_list': [],
            'badge_color': badge_color
        }
        JOBS_DB.append(new_job)
        return redirect(url_for('my_ads'))
        
    return render_template('add_job.html', categories=CATEGORIES_STRUCTURE, regions=REGIONS)

@app.route('/my-ads')
def my_ads():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_jobs = [j for j in JOBS_DB if j['user_id'] == session.get('user_id')]
    return render_template('my_ads.html', jobs=user_jobs)

@app.route('/notifications')
def notifications():
    user_id = session.get('user_id')
    if user_id:
        if user_id not in USER_READ_NOTIFICATIONS:
            USER_READ_NOTIFICATIONS[user_id] = []
        # Hammasini o'qilgan deb belgilash
        for n in NOTIFICATIONS_DB:
            if n['id'] not in USER_READ_NOTIFICATIONS[user_id]:
                USER_READ_NOTIFICATIONS[user_id].append(n['id'])
    return render_template('notifications.html', notifications=NOTIFICATIONS_DB)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if request.form.get('username') == 'admin' and request.form.get('password') == 'dilshod2026':
            session['is_admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            error = "Admin login yoki paroli xato!"
    return render_template('admin_login.html', error=error)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        notif_text = request.form.get('notification_text')
        if notif_text:
            new_notif = {
                'id': len(NOTIFICATIONS_DB) + 1,
                'text': notif_text,
                'date': time.strftime('%Y-%m-%d')
            }
            NOTIFICATIONS_DB.append(new_notif)
        return redirect(url_for('admin_panel'))

    return render_template('admin_panel.html', jobs=JOBS_DB, users=USERS_DB, notifications=NOTIFICATIONS_DB)

@app.route('/admin/approve-job/<int:job_id>')
def admin_approve_job(job_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    for j in JOBS_DB:
        if j['id'] == job_id:
            j['status'] = 'active'
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete-job/<int:job_id>')
def admin_delete_job(job_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    global JOBS_DB
    JOBS_DB = [j for j in JOBS_DB if j['id'] != job_id]
    return redirect(url_for('admin_panel'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

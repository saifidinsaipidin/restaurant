import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date, time, timedelta
import html

# =====================================================================
# 1. КОНФИГУРАЦИЯ ЖАНА НЕГИЗГИ МААЛЫМАТТАР
# =====================================================================
st.set_page_config(
    page_title="Ала-Тоо Дент — Заманбап Стоматология",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

CLINIC_INFO = {
    "name": "Ала-Тоо Дент",
    "city": "Бишкек",
    "address": "Чүй проспектиси 145, 2-кабат",
    "phone": "+996 (700) 123-456",
    "whatsapp": "996700123456",
    "hours": "Дш–Иш: 09:00 – 20:00 | Жш: 10:00 – 17:00",
    "admin_pass": "admin123",
    "promo_code": "SMILE10",
    "promo_discount": 0.10
}

SERVICES = [
    {"id": 1, "category": "Терапия", "name": "Консультация жана 3D диагностика", "price": 500, "duration": 30,
     "desc": "Толук кароо, дарылоо планын түзүү жана рентген."},
    {"id": 2, "category": "Терапия", "name": "Кариести дарылоо (жарык пломба)", "price": 2500, "duration": 60,
     "desc": "Япондук заманбап композиттик пломба коюу."},
    {"id": 3, "category": "Терапия", "name": "Пульпитти дарылоо (1 канал)", "price": 3500, "duration": 60,
     "desc": "Микроскоп алдында каналдарды тазалоо жана пломбалоо."},
    {"id": 4, "category": "Гигиена", "name": "Тиштерди ультраүн менен тазалоо (AirFlow)", "price": 3000, "duration": 45,
     "desc": "Тиш таштарын жана каралжын тактарды кетирүү."},
    {"id": 5, "category": "Гигиена", "name": "Zoom 4 лазердик агартуу", "price": 12000, "duration": 90,
     "desc": "Тиштерди 6-8 тонго чейин коопсуз агартуу."},
    {"id": 6, "category": "Хирургия", "name": "Жөнөкөй тиш жулуу", "price": 1500, "duration": 30,
     "desc": "Оорутпай, сапаттуу анестезия менен тиш алуу."},
    {"id": 7, "category": "Хирургия", "name": "Акыл тишти (8-тиш) жулуу", "price": 4500, "duration": 60,
     "desc": "Татаал өскөн акыл тиштерди хирургиялык жол менен алуу."},
    {"id": 8, "category": "Имплантация", "name": "Имплант орнотуу (Osstem, Корея)", "price": 22000, "duration": 60,
     "desc": "Өмүр бою кепилдиги бар кореялык имплант."},
    {"id": 9, "category": "Имплантация", "name": "Имплант орнотуу (Straumann, Швейцария)", "price": 45000,
     "duration": 60, "desc": "Премиум класстагы швейцариялык имплант."},
    {"id": 10, "category": "Ортопедия", "name": "Цирконий коронкасы", "price": 14000, "duration": 45,
     "desc": "Табигый тиштен айырмаланбаган бышык коронка."},
    {"id": 11, "category": "Ортопедия", "name": "Керамикалык винир (1 тиш)", "price": 18000, "duration": 60,
     "desc": "Голливуд жылмаюусун түзүү үчүн жука пластинкалар."},
    {"id": 12, "category": "Ортодонтия", "name": "Металл брекет системасы (1 жаак)", "price": 18000, "duration": 60,
     "desc": "Тиштердин түзөлүшү үчүн классикалык брекет."},
    {"id": 13, "category": "Ортодонтия", "name": "Элайнерлер (Invisalign)", "price": 85000, "duration": 60,
     "desc": "Көрүнбөгөн тунук каптар менен тиш түздөө."},
    {"id": 14, "category": "Балдар бөлүмү", "name": "Сүт тишти дарылоо", "price": 1500, "duration": 30,
     "desc": "Балдар үчүн коркунучсуз жана оорутпай дарылоо."},
]

DOCTORS = [
    {"id": 1, "name": "Др. Азамат Токтосунов", "role": "Башкы врач, Имплантолог-хирург", "exp": "14 жыл тажрыйба",
     "rating": 4.9, "categories": ["Хирургия", "Имплантация"],
     "bio": "Германия жана Түштүк Кореяда стажировкадан өткөн. 3000ден ашык ийгиликтүү имплантация жасаган."},
    {"id": 2, "name": "Др. Айгүл Садыкова", "role": "Терапевт-эндодонтист", "exp": "10 жыл тажрыйба", "rating": 5.0,
     "categories": ["Терапия", "Гигиена"],
     "bio": "Микроскоп менен тиш каналдарын дарылоо жана эстетикалык реставрация боюнча адис."},
    {"id": 3, "name": "Др. Бакыт Эсенов", "role": "Ортопед-гнатолог", "exp": "12 жыл тажрыйба", "rating": 4.8,
     "categories": ["Ортопедия"],
     "bio": "Цирконий коронкалар жана винирлер аркылуу жылмаюуну калыбына келтирүү чебери."},
    {"id": 4, "name": "Др. Мээрим Касымова", "role": "Ортодонт", "exp": "8 жыл тажрыйба", "rating": 4.9,
     "categories": ["Ортодонтия"],
     "bio": "Брекет системалары жана элайнерлер менен тиш катарын түздөө боюнча эксперт."},
    {"id": 5, "name": "Др. Жылдыз Алиева", "role": "Балдар стоматологу", "exp": "7 жыл тажрыйба", "rating": 5.0,
     "categories": ["Балдар бөлүмү", "Гигиена"],
     "bio": "Ар бир балага өзгөчө психологиялык мамиле жасап, оорутпай дарылайт."},
]

FAQS = [
    ("Тишти дарылоо оорутабы?",
     "Жок, биз эң акыркы муундагы жергиликтүү анестетиктерди колдонобуз. Ийне саярдын алдында тиш этине атайын ооруну сездирбөөчү гель сүйкөлөт."),
    ("Биринчи консультация кандай өтөт?",
     "Врач ооз көңдөйүн толук карап, зарыл болсо санариптик рентген жасайт жана дарылоонун так баасы жазылган планын түзүп берет."),
    ("Бөлүп төлөө (рассрочка) барбы?",
     "Ооба, имплантация, брекет жана протездөө кызматтарына 3 айдан 12 айга чейин пайызсыз бөлүп төлөө каралган."),
    ("Канча убакытта бир тишти тазалатып туруу керек?",
     "Стоматологдор ар 6 айда бир жолу профессионалдык гигиеналык тазалоодон өтүп турууну сунушташат.")
]

# =====================================================================
# 2. МААЛЫМАТ БАЗАСЫ (SQLite)
# =====================================================================
DB_FILE = "dental_clinic.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            service_name TEXT NOT NULL,
            doctor_name TEXT NOT NULL,
            app_date TEXT NOT NULL,
            app_time TEXT NOT NULL,
            comment TEXT,
            status TEXT DEFAULT 'Жаңы',
            created_at TEXT NOT NULL
        )
    """)
    # Бир врачка бир дата жана убакытка эки адам жазыла албашы үчүн чектөө
    c.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_slot 
        ON appointments(doctor_name, app_date, app_time) 
        WHERE status != 'Жокко чыгарылды'
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            doctor_name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            text TEXT NOT NULL,
            approved INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
    """)
    # Баштапкы демо отзывдар
    c.execute("SELECT COUNT(*) FROM reviews")
    if c.fetchone()[0] == 0:
        demo_reviews = [
            ("Айпери М.", "Др. Айгүл Садыкова", 5,
             "Тишимди эч оорутпай дарылап берди. Клиника абдан таза жана заманбап экен!", 1,
             datetime.now().strftime("%Y-%m-%d")),
            ("Нурлан К.", "Др. Азамат Токтосунов", 5, "Имплант койдурдум, баары жогорку деңгээлде өттү. Чоң рахмат!", 1,
             datetime.now().strftime("%Y-%m-%d")),
            ("Элмира Т.", "Др. Жылдыз Алиева", 5,
             "Балам стоматологдон коркчу эле, бирок Жылдыз эжеге ыйлабай отуруп тишин дарылатты.", 1,
             datetime.now().strftime("%Y-%m-%d")),
        ]
        c.executemany(
            "INSERT INTO reviews (author, doctor_name, rating, text, approved, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            demo_reviews)
    conn.commit()
    conn.close()


def get_booked_slots(doctor_name: str, app_date: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT app_time FROM appointments 
        WHERE doctor_name = ? AND app_date = ? AND status != 'Жокко чыгарылды'
    """, (doctor_name, app_date))
    slots = [row[0] for row in c.fetchall()]
    conn.close()
    return slots


def create_appointment(name, phone, service, doctor, app_date, app_time, comment):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO appointments (patient_name, phone, service_name, doctor_name, app_date, app_time, comment, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Жаңы', ?)
        """, (name, phone, service, doctor, app_date, app_time, comment, datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        return True, "Сиз ийгиликтүү жазылдыңыз! Администратор жакын арада байланышат."
    except sqlite3.IntegrityError:
        return False, "Кечиресиз, бул убакыт жаңы эле бош эмес болуп калды. Башка убакыт тандаңыз."
    finally:
        conn.close()


# =====================================================================
# 3. СТИЛЬ ЖАНА CSS (UI)
# =====================================================================
def inject_css():
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #0077b6 0%, #00b4d8 100%);
            padding: 2.5rem;
            border-radius: 15px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0, 119, 182, 0.2);
        }
        .main-header h1 { color: white; margin-bottom: 0.5rem; font-size: 2.4rem; }
        .main-header p { font-size: 1.1rem; opacity: 0.95; }
        .card {
            background-color: #ffffff;
            border: 1px solid #e0e6ed;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            transition: transform 0.2s ease;
        }
        .card:hover { transform: translateY(-3px); border-color: #00b4d8; }
        .price-tag {
            background-color: #e0f7fa;
            color: #006064;
            padding: 4px 10px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.95rem;
        }
        .doc-avatar {
            width: 60px; height: 60px;
            background: #0077b6; color: white;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.4rem; font-weight: bold;
            margin-bottom: 10px;
        }
    </style>
    """, unsafe_allow_html=True)


# =====================================================================
# 4. БАРАКЧАЛАР (VIEWS)
# =====================================================================
def page_home():
    st.markdown(f"""
    <div class="main-header">
        <h1>🦷 {CLINIC_INFO['name']} — Сиздин дени сак жылмаюуңуз</h1>
        <p>Заманбап жабдуулар, тажрыйбалуу дарыгерлер жана эч кандай оорутпай дарылоо кепилдиги.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Иш тажрыйбабыз", "12+ жыл", "Ишенимдүү клиника")
    c2.metric("Ыраазы кардарлар", "15,000+", "99% оң пикир")
    c3.metric("Дарыгерлер", "5 адис", "Эл аралык сертификат")
    c4.metric("Кепилдик", "10 жылга чейин", "Расмий келишим")

    st.markdown("---")
    st.subheader("🌟 Эмне үчүн бизди тандашат?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            '<div class="card"><h4>🔬 Микроскоп менен дарылоо</h4><p>Эң татаал тиш каналдарын 25 эсе чоңойтуп көрсөтүүчү микроскоп менен сактап калабыз.</p></div>',
            unsafe_allow_html=True)
    with col2:
        st.markdown(
            '<div class="card"><h4>💉 100% Оорутпай дарылоо</h4><p>Компьютердик анестезия жана сапаттуу препараттар аркылуу эч кандай оору сезилбейт.</p></div>',
            unsafe_allow_html=True)
    with col3:
        st.markdown(
            '<div class="card"><h4>🛡️ Стерилдүүлүк көзөмөлү</h4><p>Ар бир аспап 4 этаптуу стерилизациядан өтүп, кардардын көзүнчө ачылат.</p></div>',
            unsafe_allow_html=True)

    st.subheader("🔥 Популярдуу кызматтар")
    cols = st.columns(3)
    for idx, srv in enumerate(SERVICES[:3]):
        with cols[idx]:
            st.markdown(f"""
            <div class="card">
                <h4>{srv['name']}</h4>
                <p style="color:#555; font-size:0.9rem;">{srv['desc']}</p>
                <span class="price-tag">{srv['price']:,} сом</span> • <small>⏱ {srv['duration']} мүн</small>
            </div>
            """, unsafe_allow_html=True)


def page_services():
    st.title("📋 Кызматтар жана Баалар")
    search = st.text_input("🔍 Кызматты издөө (мисалы: имплант, тазалоо, кариес...)")

    categories = ["Баары"] + sorted(list(set(s["category"] for s in SERVICES)))
    selected_cat = st.radio("Категорияны тандаңыз:", categories, horizontal=True)

    filtered = SERVICES
    if selected_cat != "Баары":
        filtered = [s for s in filtered if s["category"] == selected_cat]
    if search:
        filtered = [s for s in filtered if search.lower() in s["name"].lower() or search.lower() in s["desc"].lower()]

    if not filtered:
        st.warning("Сиздин сурооңуз боюнча кызмат табылган жок.")
    else:
        for srv in filtered:
            with st.container():
                c1, c2, c3 = st.columns([4, 1.5, 1.5])
                with c1:
                    st.markdown(f"**{srv['name']}** `{srv['category']}`")
                    st.caption(srv['desc'])
                with c2:
                    st.markdown(f"<span class='price-tag'>{srv['price']:,} сом</span>", unsafe_allow_html=True)
                    st.caption(f"Убактысы: {srv['duration']} мүнөт")
                with c3:
                    if st.button("Жазылуу ➡️", key=f"srv_{srv['id']}"):
                        st.session_state["preselected_service"] = srv["name"]
                        st.session_state["nav_page"] = "📅 Кабыл алууга жазылуу"
                        st.rerun()
                st.divider()


def page_doctors():
    st.title("👨‍⚕️ Биздин Дарыгерлер")
    cols = st.columns(2)
    for idx, doc in enumerate(DOCTORS):
        initials = "".join([w[0] for w in doc["name"].split()[1:3]])
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="card">
                <div style="display:flex; align-items:center; gap:15px;">
                    <div class="doc-avatar">{initials}</div>
                    <div>
                        <h4 style="margin:0;">{doc['name']}</h4>
                        <p style="margin:0; color:#0077b6; font-weight:600;">{doc['role']}</p>
                        <small>⭐ {doc['rating']} | 💼 {doc['exp']}</small>
                    </div>
                </div>
                <p style="margin-top:12px; color:#444;">{doc['bio']}</p>
                <p><b>Багыттары:</b> {', '.join(doc['categories'])}</p>
            </div>
            """, unsafe_allow_html=True)


def page_calculator():
    st.title("🧮 Дарылоо баасын эсептөө калькулятору")
    st.write("Керектүү кызматтарды жана алардын санын тандап, болжолдуу сумманы эсептеңиз.")

    selected_items = []
    total_price = 0
    total_time = 0

    col1, col2 = st.columns([2, 1])
    with col1:
        for srv in SERVICES:
            c_chk, c_qty = st.columns([3, 1])
            with c_chk:
                checked = st.checkbox(f"{srv['name']} ({srv['price']:,} сом)", key=f"calc_chk_{srv['id']}")
            with c_qty:
                qty = st.number_input("Саны", min_value=1, max_value=32, value=1, key=f"calc_qty_{srv['id']}",
                                      disabled=not checked, label_visibility="collapsed")
            if checked:
                sub_price = srv["price"] * qty
                sub_time = srv["duration"] * qty
                selected_items.append({"Кызмат": srv["name"], "Саны": qty, "Сумма (сом)": sub_price})
                total_price += sub_price
                total_time += sub_time

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🧾 Жыйынтык эсеп")
        if selected_items:
            st.table(pd.DataFrame(selected_items))
            promo = st.text_input("Промокод (мисалы: SMILE10)").strip().upper()
            discount = 0
            if promo == CLINIC_INFO["promo_code"]:
                discount = int(total_price * CLINIC_INFO["promo_discount"])
                st.success(f"Промокод кабыл алынды! -10% (-{discount:,} сом)")
            elif promo:
                st.error("Мындай промокод жок.")

            final_price = total_price - discount
            st.metric("Жалпы сумма:", f"{final_price:,} сом", f"-{discount:,} сом арзандатуу" if discount else None)
            st.write(f"⏱ Болжолдуу убакыт: **{total_time} мүнөт**")
        else:
            st.info("Сол жактан кызматтарды тандаңыз.")
        st.markdown('</div>', unsafe_allow_html=True)


def page_booking():
    st.title("📅 Кабыл алууга онлайн жазылуу")

    service_names = [s["name"] for s in SERVICES]
    default_idx = 0
    if "preselected_service" in st.session_state and st.session_state["preselected_service"] in service_names:
        default_idx = service_names.index(st.session_state["preselected_service"])

    col1, col2 = st.columns(2)
    with col1:
        selected_service = st.selectbox("1. Кызматты тандаңыз:", service_names, index=default_idx)
        srv_obj = next(s for s in SERVICES if s["name"] == selected_service)

        # Кызматка тиешелүү врачтарды фильтрлөө
        matching_docs = [d["name"] for d in DOCTORS if srv_obj["category"] in d["categories"]]
        if not matching_docs:
            matching_docs = [d["name"] for d in DOCTORS]
        selected_doctor = st.selectbox("2. Дарыгерди тандаңыз:", matching_docs)

    with col2:
        selected_date = st.date_input("3. Күндү тандаңыз:", min_value=date.today(),
                                      max_value=date.today() + timedelta(days=30))
        date_str = selected_date.strftime("%Y-%m-%d")

        # Бош убакыттарды эсептөө
        all_slots = [f"{h:02d}:00" for h in range(9, 19)]
        booked = get_booked_slots(selected_doctor, date_str)

        available_slots = []
        now_time = datetime.now().time()
        for slot in all_slots:
            if slot in booked:
                continue
            if selected_date == date.today():
                slot_hour = int(slot.split(":")[0])
                if slot_hour <= now_time.hour:
                    continue
            available_slots.append(slot)

        if available_slots:
            selected_time = st.selectbox("4. Бош убакытты тандаңыз:", available_slots)
        else:
            selected_time = None
            st.error("Бул күнгө бош убакыт калган жок. Башка күн тандаңыз.")

    st.markdown("---")
    with st.form("booking_form"):
        st.subheader("5. Жеке маалыматтарыңыз")
        p_name = st.text_input("Аты-жөнүңүз *")
        p_phone = st.text_input("Телефон номериңиз (WhatsApp) *", placeholder="+996 700 000 000")
        p_comment = st.text_area("Кошумча маалымат же даттануу (милдеттүү эмес)")
        submitted = st.form_submit_button("✅ Жазылууну тастыктоо", use_container_width=True)

        if submitted:
            if not p_name.strip() or len(p_phone.strip()) < 9:
                st.error("Сураныч, аты-жөнүңүздү жана туура телефон номериңизди жазыңыз!")
            elif not selected_time:
                st.error("Бош убакыт тандалган жок!")
            else:
                ok, msg = create_appointment(
                    html.escape(p_name.strip()),
                    html.escape(p_phone.strip()),
                    selected_service,
                    selected_doctor,
                    date_str,
                    selected_time,
                    html.escape(p_comment.strip())
                )
                if ok:
                    st.success(msg)
                    st.balloons()
                else:
                    st.error(msg)


def page_reviews():
    st.title("💬 Кардарлардын пикирлери жана Суроо-жооп (FAQ)")
    tab1, tab2 = st.tabs(["⭐ Пикирлер (Отзывдар)", "❓ Көп берилүүчү суроолор"])

    with tab1:
        c_list, c_form = st.columns([2, 1])
        with c_list:
            conn = sqlite3.connect(DB_FILE)
            df_rev = pd.read_sql_query("SELECT * FROM reviews WHERE approved = 1 ORDER BY id DESC", conn)
            conn.close()
            for _, row in df_rev.iterrows():
                stars = "⭐" * int(row["rating"])
                st.markdown(f"""
                <div class="card">
                    <b>{row['author']}</b> • <small>{row['created_at']}</small><br>
                    <small style="color:#0077b6;">Врач: {row['doctor_name']}</small> | {stars}
                    <p style="margin-top:8px;">{row['text']}</p>
                </div>
                """, unsafe_allow_html=True)

        with c_form:
            with st.form("review_form"):
                st.subheader("Пикир калтыруу")
                r_author = st.text_input("Сиздин атыңыз *")
                r_doc = st.selectbox("Кайсы врачка бардыңыз?", [d["name"] for d in DOCTORS])
                r_rating = st.slider("Баалоо", 1, 5, 5)
                r_text = st.text_area("Пикириңиз *")
                if st.form_submit_button("Жөнөтүү"):
                    if r_author.strip() and r_text.strip():
                        conn = sqlite3.connect(DB_FILE)
                        c = conn.cursor()
                        c.execute(
                            "INSERT INTO reviews (author, doctor_name, rating, text, approved, created_at) VALUES (?, ?, ?, ?, 1, ?)",
                            (html.escape(r_author.strip()), r_doc, r_rating, html.escape(r_text.strip()),
                             datetime.now().strftime("%Y-%m-%d")))
                        conn.commit()
                        conn.close()
                        st.success("Пикириңиз кошулду! Рахмат!")
                        st.rerun()
                    else:
                        st.error("Бардык талааларды толтуруңуз.")

    with tab2:
        for q, a in FAQS:
            with st.expander(q):
                st.write(a)


def page_contacts():
    st.title("📍 Байланыш жана Дарек")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="card">
            <h3>🏥 {CLINIC_INFO['name']}</h3>
            <p><b>📍 Дарек:</b> {CLINIC_INFO['city']}, {CLINIC_INFO['address']}</p>
            <p><b>📞 Телефон:</b> {CLINIC_INFO['phone']}</p>
            <p><b>🕒 Иштөө убактысы:</b> {CLINIC_INFO['hours']}</p>
            <br>
            <a href="https://wa.me/{CLINIC_INFO['whatsapp']}" target="_blank" style="background:#25D366; color:white; padding:10px 20px; border-radius:8px; text-decoration:none; font-weight:bold;">
                💬 WhatsApp аркылуу жазуу
            </a>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        # Бишкек борборунун координаттары
        map_data = pd.DataFrame({'lat': [42.8765], 'lon': [74.6037]})
        st.map(map_data, zoom=14)


def page_admin():
    st.title("🔐 Администратор панели")
    if "admin_auth" not in st.session_state:
        st.session_state["admin_auth"] = False

    if not st.session_state["admin_auth"]:
        pwd = st.text_input("Паролду киргизиңиз (демо: admin123):", type="password")
        if st.button("Кирүү"):
            if pwd == CLINIC_INFO["admin_pass"]:
                st.session_state["admin_auth"] = True
                st.rerun()
            else:
                st.error("Пароль туура эмес!")
        return

    if st.sidebar.button("🚪 Админден чыгуу"):
        st.session_state["admin_auth"] = False
        st.rerun()

    conn = sqlite3.connect(DB_FILE)
    df_app = pd.read_sql_query("SELECT * FROM appointments ORDER BY id DESC", conn)

    # Аналитика
    m1, m2, m3 = st.columns(3)
    m1.metric("Бардык жазылуулар", len(df_app))
    m2.metric("Жаңы заявкалар", len(df_app[df_app["status"] == "Жаңы"]) if not df_app.empty else 0)
    m3.metric("Кабыл алынгандар", len(df_app[df_app["status"] == "Аяктады"]) if not df_app.empty else 0)

    st.subheader("📋 Заявкаларды башкаруу")
    if df_app.empty:
        st.info("Азырынча жазылуулар жок.")
    else:
        st.dataframe(df_app, use_container_width=True)

        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            app_id = st.number_input("Заявка ID:", min_value=1, step=1)
        with c2:
            new_status = st.selectbox("Жаңы статус:", ["Жаңы", "Тастыкталды", "Аяктады", "Жокко чыгарылды"])
        with c3:
            st.write("")
            st.write("")
            if st.button("Статусту өзгөртүү"):
                c = conn.cursor()
                c.execute("UPDATE appointments SET status = ? WHERE id = ?", (new_status, app_id))
                conn.commit()
                st.success(f"ID #{app_id} статусу өзгөртүлдү!")
                st.rerun()

        csv = df_app.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 Excel/CSV жүктөп алуу", data=csv, file_name="appointments.csv", mime="text/csv")

    conn.close()


# =====================================================================
# 5. НЕГИЗГИ НАВИГАЦИЯ
# =====================================================================
def main():
    init_db()
    inject_css()

    menu = [
        "🏠 Башкы бет",
        "📋 Кызматтар жана баалар",
        "👨‍⚕️ Дарыгерлер",
        "🧮 Баа эсептөө (Калькулятор)",
        "📅 Кабыл алууга жазылуу",
        "💬 Пикирлер жана FAQ",
        "📍 Байланыш",
        "🔐 Админ панель"
    ]

    if "nav_page" not in st.session_state:
        st.session_state["nav_page"] = menu[0]

    with st.sidebar:
        st.markdown(f"## 🦷 {CLINIC_INFO['name']}")
        st.caption(f"📍 {CLINIC_INFO['city']}, {CLINIC_INFO['address']}")
        st.markdown("---")
        choice = st.radio("Меню:", menu, index=menu.index(st.session_state["nav_page"]))
        st.session_state["nav_page"] = choice
        st.markdown("---")
        st.info(f"📞 Номер: +996706678084")

    if choice == menu[0]:
        page_home()
    elif choice == menu[1]:
        page_services()
    elif choice == menu[2]:
        page_doctors()
    elif choice == menu[3]:
        page_calculator()
    elif choice == menu[4]:
        page_booking()
    elif choice == menu[5]:
        page_reviews()
    elif choice == menu[6]:
        page_contacts()
    elif choice == menu[7]:
        page_admin()


if __name__ == "__main__":
    main()
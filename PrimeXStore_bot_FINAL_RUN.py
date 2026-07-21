import telebot
from telebot import types
import json, os
from datetime import datetime

TOKEN = "8315190785:AAGY-gLTz8ZPXe9z4j-pTOhsNArJx6OwMu0"
ADMIN_ID = 8933825471
SUPPORT_USERNAME = "@PrimeXStore22"
ANNOUNCEMENT_CHANNEL = "@adscahneel"
DELIVERY_CHANNEL_ID = -1004496209902

bot = telebot.TeleBot(TOKEN)
pending_orders = {}
carts = {}
waiting_for_qty = {}

CLEAN = {
    "india": {"name": "🇮🇳 الهند", "price": 0.3},
    "egypt": {"name": "🇪🇬 مصر", "price": 0.5},
    "vietnam": {"name": "🇻🇳 فيتنام", "price": 0.9},
    "ksa": {"name": "🇸🇦 السعودية", "price": 1.5},
    "pakistan": {"name": "🇵🇰 باكستان", "price": 0.7},
    "morocco": {"name": "🇲🇦 المغرب", "price": 0.6},
    "myanmar": {"name": "🇲🇲 ماينمار", "price": 0.3},
    "kenya": {"name": "🇰🇪 كينيا", "price": 0.5},
    "indonesia": {"name": "🇮🇩 اندونيسيا", "price": 0.6},
    "nigeria": {"name": "🇳🇬 نيجيريا", "price": 0.5},
}
SPAM = {
    "india": {"name": "🇮🇳 الهند", "price": 0.2},
    "random": {"name": "🌍 عشوائي", "price": 0.3},
    "rare": {"name": "💎 دول نادرة وقديم", "price": 0.45},
    "usa": {"name": "🇺🇸 امريكا", "price": 0.25},
    "myanmar": {"name": "🇲🇲 ماينمار", "price": 0.2},
}
WHATSAPP = {"indonesia": {"name": "🇮🇩 اندونيسيا", "price": 0.2}}
TIKTOK = {"germany": {"name": "🇩🇪 المانيا", "price": 0.25}, "sudan": {"name": "🇸🇩 السودان", "price": 0.2}}
INSTA = {"ghana": {"name": "🇬🇭 غانا", "price": 0.15}}
FACEBOOK = {
    "ghana": {"name": "🇬🇭 غانا", "price": 0.1},
    "indonesia": {"name": "🇮🇩 اندونيسيا", "price": 0.15},
    "zimbabwe": {"name": "🇿🇼 زيمبابوي", "price": 0.1},
    "sudan": {"name": "🇸🇩 السودان", "price": 0.15},
}
PRICE_PER_10 = 0.09
FOLLOWERS_PLATFORMS = {
    "tiktok": "🎵 تيك توك",
    "facebook": "👤 فيسبوك",
    "twitter": "🐦 تويتر / X",
    "instagram": "📸 انستغرام",
    "youtube": "▶️ يوتيوب",
    "telegram": "📩 تليجرام",
}
STARS_GIFTS = {
    "bear": {"name": "🧸 دب", "stars": 15, "price": 0.18},
    "rose": {"name": "🌹 وردة", "stars": 25, "price": 0.29},
    "cake": {"name": "🎂 كيكة", "stars": 50, "price": 0.57},
    "ring": {"name": "💍 خاتم", "stars": 100, "price": 1.15},
}

STOCK_FILE = "stock_v16.json"
ORDERS_FILE = "orders_v16.json"
CARTS_FILE = "carts_v16.json"
if not os.path.exists(STOCK_FILE): open(STOCK_FILE,"w",encoding="utf-8").write("{}")
if not os.path.exists(ORDERS_FILE): open(ORDERS_FILE,"w",encoding="utf-8").write("[]")
if not os.path.exists(CARTS_FILE): open(CARTS_FILE,"w",encoding="utf-8").write("{}")

def get_stock():
    try: return json.load(open(STOCK_FILE,"r",encoding="utf-8"))
    except: return {}
def save_stock(s): json.dump(s, open(STOCK_FILE,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
def get_orders():
    try: return json.load(open(ORDERS_FILE,"r",encoding="utf-8"))
    except: return []
def save_order(order):
    orders = get_orders()
    orders.append(order)
    json.dump(orders, open(ORDERS_FILE,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
def get_carts():
    try: return json.load(open(CARTS_FILE,"r",encoding="utf-8"))
    except: return {}
def save_carts(c): json.dump(c, open(CARTS_FILE,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

def calc_price(qty): return round((qty / 10) * PRICE_PER_10, 2)

def admin_main_menu():
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("📊 الاحصائيات", callback_data="admin_stats"), types.InlineKeyboardButton("📦 المخزون", callback_data="admin_stock"))
    m.add(types.InlineKeyboardButton("➕ اضافة ارقام", callback_data="admin_add_info"), types.InlineKeyboardButton("🗑️ حذف المخزون", callback_data="admin_clear_stock"))
    m.add(types.InlineKeyboardButton("📋 الطلبات المعلقة", callback_data="admin_pending"), types.InlineKeyboardButton("📜 سجل الطلبات", callback_data="admin_history"))
    m.add(types.InlineKeyboardButton("💰 الاسعار", callback_data="admin_prices"), types.InlineKeyboardButton("📢 اذاعة", callback_data="admin_broadcast_info"))
    return m

def main_menu(user_id=None):
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("🛒 شراء ارقام", callback_data="buy_numbers"))
    m.add(types.InlineKeyboardButton("👥 شراء متابعين", callback_data="buy_followers"))
    m.add(types.InlineKeyboardButton("⭐ شراء نجوم", callback_data="buy_stars"))
    cart_count = len(get_carts().get(str(user_id), [])) if user_id else 0
    m.add(types.InlineKeyboardButton(f"🛒 سلة المشتريات ({cart_count})", callback_data="my_cart"))
    m.add(types.InlineKeyboardButton("📢 الاعلانات", callback_data="announcement"), types.InlineKeyboardButton("💬 الدعم", callback_data="support"))
    m.add(types.InlineKeyboardButton("ℹ️ من نحن", callback_data="about_us"))
    return m

def categories_menu():
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("📩 تليجرام", callback_data="cat_telegram"))
    m.add(types.InlineKeyboardButton("💚 واتساب", callback_data="cat_whatsapp"))
    m.add(types.InlineKeyboardButton("📸 انستا", callback_data="cat_insta"))
    m.add(types.InlineKeyboardButton("🎵 تيك توك", callback_data="cat_tiktok"))
    m.add(types.InlineKeyboardButton("👤 فيسبوك", callback_data="cat_facebook"))
    m.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_main"))
    return m

def followers_main_menu():
    m = types.InlineKeyboardMarkup(row_width=2)
    for k,name in FOLLOWERS_PLATFORMS.items():
        m.add(types.InlineKeyboardButton(name, callback_data=f"follow_{k}"))
    m.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_main"))
    return m

def stars_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    for key, info in STARS_GIFTS.items():
        m.add(types.InlineKeyboardButton(f"{info['name']} - {info['stars']} نجمة - ${info['price']}", callback_data=f"stars_{key}"))
    m.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_main"))
    return m

def qty_menu(platform):
    m = types.InlineKeyboardMarkup(row_width=3)
    m.add(types.InlineKeyboardButton("10 = $0.09", callback_data=f"qty_{platform}_10"), types.InlineKeyboardButton("20 = $0.18", callback_data=f"qty_{platform}_20"), types.InlineKeyboardButton("50 = $0.45", callback_data=f"qty_{platform}_50"))
    m.add(types.InlineKeyboardButton("100 = $0.9", callback_data=f"qty_{platform}_100"), types.InlineKeyboardButton("200 = $1.8", callback_data=f"qty_{platform}_200"), types.InlineKeyboardButton("300 = $2.7", callback_data=f"qty_{platform}_300"))
    m.add(types.InlineKeyboardButton("400 = $3.6", callback_data=f"qty_{platform}_400"), types.InlineKeyboardButton("500 = $4.5", callback_data=f"qty_{platform}_500"))
    m.add(types.InlineKeyboardButton("✏️ عدد مخصص", callback_data=f"custom_{platform}"))
    m.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="buy_followers"))
    return m

def telegram_type_menu():
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("🚫 عادي", callback_data="type_telegram_spam"), types.InlineKeyboardButton("✅ سليم", callback_data="type_telegram_clean"))
    m.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="buy_numbers"))
    return m

def menu_from_dict(d, prefix):
    m = types.InlineKeyboardMarkup(row_width=1)
    for k,v in d.items():
        m.add(types.InlineKeyboardButton(f"{v['name']} - ${v['price']}", callback_data=f"{prefix}_{k}"))
    m.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_main"))
    return m

@bot.message_handler(commands=['start'])
def start(msg):
    if msg.chat.id == ADMIN_ID:
        bot.send_message(msg.chat.id, "👋 اهلا يا مدير\nاختار:", reply_markup=main_menu(msg.chat.id))
        bot.send_message(msg.chat.id, "🎛️ لوحة الادمن:", reply_markup=admin_main_menu())
    else:
        bot.send_message(msg.chat.id, "👋 اهلا بيك في متجرنا\nاختار الخدمة:", reply_markup=main_menu(msg.chat.id))

@bot.message_handler(commands=['admin'])
def admin_cmd(msg):
    if msg.chat.id!= ADMIN_ID: return
    bot.send_message(msg.chat.id, "🎛️ لوحة تحكم المدير:", reply_markup=admin_main_menu())

@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    if call.data.startswith("admin_"):
        if call.message.chat.id!= ADMIN_ID: return
        if call.data=="admin_stats":
            stock = get_stock()
            total_nums = sum(len(v) for v in stock.values())
            orders = get_orders()
            total_sales = sum(o.get("price",0) for o in orders)
            txt = f"📊 الاحصائيات:\n📦 مخزون: {total_nums}\n⏳ معلقة: {len(pending_orders)}\n✅ مكتملة: {len(orders)}\n💰 مبيعات: ${round(total_sales,2)}"
            bot.send_message(call.message.chat.id, txt)
        elif call.data=="admin_stock":
            stock = get_stock()
            txt="📦 المخزون:\n"
            for k,v in stock.items(): txt+=f"{k}: {len(v)}\n"
            if not stock: txt+="فاضي"
            bot.send_message(call.message.chat.id, txt)
        return

    if call.data=="my_cart":
        carts_data = get_carts()
        my_cart = carts_data.get(str(call.message.chat.id), [])
        if not my_cart:
            m = types.InlineKeyboardMarkup()
            m.add(types.InlineKeyboardButton("🛒 تسوق الان", callback_data="buy_numbers"))
            bot.edit_message_text("🛒 سلتك فاضية\nلم تشتري اي شيء بعد", call.message.chat.id, call.message.message_id, reply_markup=m)
            return
        txt = "🛒 سلة المشتريات:\n\n"
        total = 0
        for i, item in enumerate(my_cart, 1):
            txt+=f"{i}. {item.get('name')} - ${item.get('price')}\n"
            total+=item.get("price",0)
        txt+=f"\n💰 الاجمالي: ${round(total,2)}\n📦 عدد المنتجات: {len(my_cart)}"
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(types.InlineKeyboardButton("💳 اتمام الشراء", callback_data="checkout"))
        m.add(types.InlineKeyboardButton("🗑️ تفريغ السلة", callback_data="clear_cart"))
        m.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_main"))
        bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=m)

    elif call.data=="clear_cart":
        carts_data = get_carts()
        if str(call.message.chat.id) in carts_data:
            del carts_data[str(call.message.chat.id)]
            save_carts(carts_data)
        bot.edit_message_text("✅ تم تفريغ السلة", call.message.chat.id, call.message.message_id, reply_markup=main_menu(call.message.chat.id))

    elif call.data=="checkout":
        carts_data = get_carts()
        my_cart = carts_data.get(str(call.message.chat.id), [])
        if not my_cart:
            bot.answer_callback_query(call.id, "السلة فاضية")
            return
        total = sum(i.get("price",0) for i in my_cart)
        pending_orders[call.message.chat.id] = {"cat":"cart","items":my_cart,"price":total,"name":f"سلة فيها {len(my_cart)} منتج"}
        bot.send_message(call.message.chat.id, f"🛒 سلتك: {len(my_cart)} منتج - الاجمالي ${round(total,2)}\nحول المبلغ وابعث سكرين الدفع 👇")
        del carts_data[str(call.message.chat.id)]
        save_carts(carts_data)

    elif call.data=="support":
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton("💬 تواصل مع الدعم", url=f"https://t.me/{SUPPORT_USERNAME.replace('@','')}"))
        bot.edit_message_text(f"💬 الدعم الفني:\n\nلو عندك اي مشكلة تواصل معنا:\n{SUPPORT_USERNAME}\n\nنرد في اقل من 5 دقائق ⚡", call.message.chat.id, call.message.message_id, reply_markup=m)

    elif call.data=="announcement":
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(types.InlineKeyboardButton("📢 قناة الاعلانات", url=f"https://t.me/{ANNOUNCEMENT_CHANNEL.replace('@','')}"))
        m.add(types.InlineKeyboardButton(f"💬 الدعم {SUPPORT_USERNAME}", url=f"https://t.me/{SUPPORT_USERNAME.replace('@','')}"))
        m.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_main"))
        bot.edit_message_text(f"📢 الاعلانات والعروض:\n\nتابع قناتنا لكل العروض الجديدة:\n{ANNOUNCEMENT_CHANNEL}\n\nللاستفسار: {SUPPORT_USERNAME}", call.message.chat.id, call.message.message_id, reply_markup=m)

    elif call.data=="about_us":
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton("💬 الدعم", callback_data="support"))
        m.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_main"))
        txt = f"ℹ️ من نحن:\n\nنحن متجر متخصص في:\n🛒 بيع ارقام لتفعيل جميع المنصات\n👥 بيع متابعين لكل المنصات\n⭐ بيع نجوم وهدايا تليجرام\n\n✅ ارقام مضمونة\n⚡ تسليم فوري\n💬 دعم 24/7\n\nالدعم: {SUPPORT_USERNAME}"
        bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=m)

    elif call.data=="back_main":
        bot.edit_message_text("👋 اهلا بيك\nاختار الخدمة:", call.message.chat.id, call.message.message_id, reply_markup=main_menu(call.message.chat.id))
    elif call.data=="buy_numbers":
        bot.edit_message_text("🛒 اختار نوع الرقم:", call.message.chat.id, call.message.message_id, reply_markup=categories_menu())
    elif call.data=="buy_followers":
        bot.edit_message_text("👥 اختار المنصة:", call.message.chat.id, call.message.message_id, reply_markup=followers_main_menu())
    elif call.data=="buy_stars":
        bot.edit_message_text("⭐ هدايا تليجرام:", call.message.chat.id, call.message.message_id, reply_markup=stars_menu())

    elif call.data.startswith("stars_"):
        key = call.data.split("_")[1]
        info = STARS_GIFTS.get(key)
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(types.InlineKeyboardButton("🛒 اضافة للسلة", callback_data=f"addcart_{key}"), types.InlineKeyboardButton("💳 شراء مباشر", callback_data=f"buynow_stars_{key}"))
        bot.edit_message_text(f"{info['name']} - {info['stars']} نجمة\nالسعر: ${info['price']}", call.message.chat.id, call.message.message_id, reply_markup=m)

    elif call.data.startswith("buynow_stars_"):
        k = call.data.split("_")[2]
        info = STARS_GIFTS.get(k)
        pending_orders[call.message.chat.id] = {"cat":"stars","key":k,"price":info["price"],"name":f"{info['name']} {info['stars']} نجمة"}
        bot.send_message(call.message.chat.id, f"طلبك: {info['name']} - ${info['price']}\nابعت يوزر المستلم + سكرين 👇")

    elif call.data.startswith("addcart_"):
        item_key = call.data.replace("addcart_","")
        carts_data = get_carts()
        uid = str(call.message.chat.id)
        if uid not in carts_data: carts_data[uid]=[]
        if item_key in STARS_GIFTS:
            v = STARS_GIFTS[item_key]
            info = {"name": f"{v['name']} {v['stars']} نجمة", "price": v["price"]}
        elif "follow" in item_key:
            _,plat,qty = item_key.split("_")
            qty=int(qty); price=calc_price(qty)
            info = {"name": f"{FOLLOWERS_PLATFORMS.get(plat)} {qty} متابع", "price": price}
        else:
            info = {"name": item_key, "price": 0.5}
        carts_data[uid].append(info)
        save_carts(carts_data)
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton(f"🛒 السلة ({len(carts_data[uid])})", callback_data="my_cart"))
        bot.send_message(call.message.chat.id, f"✅ تم اضافة {info['name']} للسلة - ${info['price']}", reply_markup=m)

    elif call.data.startswith("follow_"):
        plat = call.data.split("_")[1]
        bot.edit_message_text(f"{FOLLOWERS_PLATFORMS.get(plat)}\nاختار عدد المتابعين:", call.message.chat.id, call.message.message_id, reply_markup=qty_menu(plat))

    elif call.data.startswith("qty_"):
        _, plat, qty = call.data.split("_")
        qty = int(qty); price = calc_price(qty)
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(types.InlineKeyboardButton("🛒 اضافة للسلة", callback_data=f"addcart_follow_{plat}_{qty}"), types.InlineKeyboardButton("💳 شراء مباشر", callback_data=f"buynow_follow_{plat}_{qty}"))
        bot.edit_message_text(f"{FOLLOWERS_PLATFORMS.get(plat)} {qty} متابع - ${price}", call.message.chat.id, call.message.message_id, reply_markup=m)

    elif call.data.startswith("buynow_follow_"):
        _,_,plat,qty = call.data.split("_")
        qty=int(qty); price=calc_price(qty)
        pending_orders[call.message.chat.id] = {"cat":"followers","platform":plat,"qty":qty,"price":price,"name":f"{FOLLOWERS_PLATFORMS.get(plat)} {qty} متابع"}
        bot.send_message(call.message.chat.id, f"طلبك: {FOLLOWERS_PLATFORMS.get(plat)} {qty} - ${price}\nابعت رابط حسابك + سكرين 👇")

    elif call.data=="cat_telegram":
        bot.edit_message_text("📩 تليجرام:", call.message.chat.id, call.message.message_id, reply_markup=telegram_type_menu())
    elif call.data=="cat_whatsapp":
        bot.edit_message_text("💚 واتساب:", call.message.chat.id, call.message.message_id, reply_markup=menu_from_dict(WHATSAPP, "buy_whatsapp"))
    elif call.data=="cat_tiktok":
        bot.edit_message_text("🎵 تيك توك:", call.message.chat.id, call.message.message_id, reply_markup=menu_from_dict(TIKTOK, "buy_tiktok"))
    elif call.data=="cat_insta":
        bot.edit_message_text("📸 انستا:", call.message.chat.id, call.message.message_id, reply_markup=menu_from_dict(INSTA, "buy_insta"))
    elif call.data=="cat_facebook":
        bot.edit_message_text("👤 فيسبوك:", call.message.chat.id, call.message.message_id, reply_markup=menu_from_dict(FACEBOOK, "buy_facebook"))

    elif call.data.startswith("type_telegram_"):
        t = call.data.split("_")[2]
        d = CLEAN if t=="clean" else SPAM
        bot.edit_message_text(f"تليجرام - {t}:", call.message.chat.id, call.message.message_id, reply_markup=menu_from_dict(d, f"buy_telegram_{t}"))

    elif call.data.startswith("buy_telegram_"):
        _,_,type_f,country = call.data.split("_")
        d = CLEAN if type_f=="clean" else SPAM
        info = d[country]
        key = f"telegram_{type_f}_{country}"
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(types.InlineKeyboardButton("🛒 اضافة للسلة", callback_data=f"addcart_{key}"), types.InlineKeyboardButton("💳 شراء مباشر", callback_data=f"buynow_telegram_{type_f}_{country}"))
        bot.edit_message_text(f"{info['name']} - ${info['price']}", call.message.chat.id, call.message.message_id, reply_markup=m)

    elif call.data.startswith("buynow_telegram_"):
        _,_,type_f,country = call.data.split("_")
        d = CLEAN if type_f=="clean" else SPAM
        info = d[country]
        pending_orders[call.message.chat.id] = {"cat":"telegram","type":type_f,"country":country,"price":info["price"],"name":info["name"]}
        bot.send_message(call.message.chat.id, f"طلبك: {info['name']} - ${info['price']}\nحول وابعث سكرين 👇")

    elif call.data.startswith("accept_"):
        if call.message.chat.id!= ADMIN_ID: return
        cid = int(call.data.split("_")[1])
        bot.send_message(call.message.chat.id, f"قبول {cid}\nاكتب الرد/الرقم:")
        bot.register_next_step_handler(call.message, lambda m: do_send(m, cid))
    elif call.data.startswith("reject_"):
        if call.message.chat.id!= ADMIN_ID: return
        cid = int(call.data.split("_")[1])
        bot.send_message(cid, "❌ تم الرفض")
        bot.send_message(call.message.chat.id, "تم الرفض")

def do_send(message, cid):
    txt = message.text
    info = pending_orders.get(cid, {})
    order_data = {"user_id":cid,"name":info.get("name"),"price":info.get("price"),"time":datetime.now().strftime("%Y-%m-%d %H:%M")}
    save_order(order_data)
    bot.send_message(cid, f"✅ تم تسليم طلبك:\n{info.get('name')} - ${info.get('price')}\nالتفاصيل: {txt}")
    bot.send_message(message.chat.id, f"تم الارسال للعميل {cid} ✅")
    try:
        delivery_text = f"✅ تم تسليم طلب جديد\n\n👤 العميل: {cid}\n📦 المنتج: {info.get('name')}\n💰 السعر: ${info.get('price')}\n🕐 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n📝 التفاصيل: {txt}"
        bot.send_message(DELIVERY_CHANNEL_ID, delivery_text)
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ لم استطع الارسال لقناة التسليمات: {e}")
    if cid in pending_orders: del pending_orders[cid]

@bot.message_handler(content_types=['photo','document','text'])
def handler(message):
    if message.text and message.text.startswith("/"):
        if message.text.startswith("/add"):
            if message.chat.id!= ADMIN_ID: return
            try:
                parts = message.text.split()
                if parts[1] in ["whatsapp","tiktok","insta","facebook"]:
                    _, cat, country, num = parts
                    key = f"{cat}_{country}"
                else:
                    _, type_f, country, num = parts
                    key = f"telegram_{type_f}_{country}"
                stock = get_stock()
                if key not in stock: stock[key]=[]
                stock[key].append(num)
                save_stock(stock)
                bot.send_message(message.chat.id, f"تم اضافة {num} الى {key} ✅")
            except Exception as e:
                bot.send_message(message.chat.id, f"خطأ: {e}")
            return
        return
    info = pending_orders.get(message.chat.id, {})
    if not info: return
    bot.send_message(message.chat.id, "✅ استلمت، انتظار الادمن")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ قبول", callback_data=f"accept_{message.chat.id}"))
    markup.add(types.InlineKeyboardButton("❌ رفض", callback_data=f"reject_{message.chat.id}"))
    try: bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    except: pass
    bot.send_message(ADMIN_ID, f"🔔 طلب جديد\n{info.get('name')}\nعميل: {message.chat.id}\nسعر: ${info.get('price')}", reply_markup=markup)

print("V16 مع سلة + دعم + اعلان + من نحن + قناة تسليمات شغال...")
bot.infinity_polling()

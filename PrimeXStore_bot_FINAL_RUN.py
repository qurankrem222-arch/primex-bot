import telebot
from telebot import types
import json, os, re, time
from datetime import datetime

TOKEN = "8315190785:AAGY-gLTz8ZPXe9z4j-pTOhsNArJx6OwMu0"
ADMIN_ID = 8933825471
SUPPORT_USERNAME = "@PrimeXStore22"
DELIVERY_CHANNEL_ID = -1004496209902
FORCE_CHANNELS = ["@PrimeXStore0", "@adscahneel", "@kingfreebots"]

MIN_RECHARGE = 0.1
MIN_ORDER = 0.1

bot = telebot.TeleBot(TOKEN)
pending_orders = {}
pending_recharge = {}
carts = {}

# ========== الاسعار ==========
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

# ========== طرق الدفع - زر الشحن ==========
PAYMENT_METHODS = {
    "cwallet": {"name": "👛 C-Wallet - 61824874", "info": "🆔 *C-Wallet ID:*\n`61824874`\n\n📸 بعد التحويل ابعت سكرين + المبلغ"},
    "usdt_erc20": {"name": "💎 USDT ERC20", "info": "💎 *USDT ERC20*\n\n`0x8D7dDE7719e9d6D3e5175CE170Fae00372715493`\n\n⚠️ شبكة ERC20"},
    "usdt_bep20": {"name": "💛 USDT BEP20", "info": "💛 *USDT BEP20 (BSC)*\n\n`0xA7fE0a5Ae6Adcd5b47df238F836449b4d0866155`\n\n⚠️ شبكة BSC"},
    "usdt_trc20": {"name": "❤️ USDT TRC20 - الأرخص ✅", "info": "❤️ *USDT TRC20 (Tron - الأرخص)*\n\n`TRHUB8kuMpdCoDzST6c4AJ4cJdk6tToz97`\n\n✅ ننصح بهذه الشبكة - رسوم قليلة"},
    "usdt_polygon": {"name": "💜 USDT POLYGON", "info": "💜 *USDT POLYGON*\n\n`0xA7fE0a5Ae6Adcd5b47df238F836449b4d0866155`\n\n⚠️ شبكة Polygon"},
    "faucetpay": {"name": "🚰 FaucetPay", "info": "🚰 *FaucetPay*\n\n`@primexstore22`\n\nابعت على اليوزر"},
    "gram": {"name": "💎 GRAM - TON", "info": "💎 *GRAM - شبكة TON*\n\n`UQBdPqUEG7TkF2TYWDOEclSYPDec4-HGOsN5ss0Zcnby1mCL`\n\n⚠️ شبكة TON فقط"},
}

# ========== ملفات ==========
STOCK_FILE = "stock_v17.json"; ORDERS_FILE = "orders_v17.json"; BALANCE_FILE = "balance_v17.json"; USERS_FILE = "users_v17.json"; CARTS_FILE = "carts_v17.json"
for f, default in [(STOCK_FILE,"{}"),(ORDERS_FILE,"[]"),(BALANCE_FILE,"{}"),(USERS_FILE,"{}"),(CARTS_FILE,"{}")]:
    if not os.path.exists(f): open(f,"w",encoding="utf-8").write(default)

def get_stock():
    try: return json.load(open(STOCK_FILE,"r",encoding="utf-8"))
    except: return {}
def save_stock(s): json.dump(s, open(STOCK_FILE,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
def get_orders():
    try: return json.load(open(ORDERS_FILE,"r",encoding="utf-8"))
    except: return []
def save_order(o):
    os_ = get_orders(); os_.append(o); json.dump(os_, open(ORDERS_FILE,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
def get_balances():
    try: return json.load(open(BALANCE_FILE,"r",encoding="utf-8"))
    except: return {}
def save_balances(b): json.dump(b, open(BALANCE_FILE,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
def get_balance(uid): return float(get_balances().get(str(uid), 0))
def add_balance(uid, amount):
    b = get_balances(); b[str(uid)] = float(b.get(str(uid),0)) + float(amount); save_balances(b); return b[str(uid)]
def deduct_balance(uid, amount):
    b = get_balances(); bal = float(b.get(str(uid),0))
    if bal < amount: return False
    b[str(uid)] = bal - amount; save_balances(b); return True
def get_carts():
    try: return json.load(open(CARTS_FILE,"r",encoding="utf-8"))
    except: return {}
def save_carts(c): json.dump(c, open(CARTS_FILE,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

def calc_price(qty): return round((qty / 10) * PRICE_PER_10, 2)

def check_force_sub(user_id):
    if not FORCE_CHANNELS: return True, []
    not_joined = []
    for ch in FORCE_CHANNELS:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status in ['left','kicked']: not_joined.append(ch)
        except: pass
    return len(not_joined)==0, not_joined

def force_sub_markup(not_joined):
    m = types.InlineKeyboardMarkup(row_width=1)
    for ch in not_joined: m.add(types.InlineKeyboardButton(f"📢 اشترك في {ch} 📢", url=f"https://t.me/{ch.replace('@','')}"))
    m.add(types.InlineKeyboardButton("✅ تحققت من الاشتراك", callback_data="check_sub")); return m

def admin_main_menu():
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("📊 الاحصائيات", callback_data="admin_stats"), types.InlineKeyboardButton("📦 المخزون", callback_data="admin_stock"))
    m.add(types.InlineKeyboardButton("➕ اضافة ارقام", callback_data="admin_add_info"), types.InlineKeyboardButton("🗑️ مسح المخزون", callback_data="admin_clear_stock"))
    m.add(types.InlineKeyboardButton("💰 اضافة رصيد", callback_data="admin_add_balance_info"), types.InlineKeyboardButton("📢 اذاعة", callback_data="admin_broadcast_info"))
    m.add(types.InlineKeyboardButton("👥 وضع العميل", callback_data="admin_view_as_user"))
    return m

def main_menu(uid=None):
    bal = get_balance(uid) if uid else 0
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(types.InlineKeyboardButton(f"💰 رصيدك: ${round(bal,2)} 💰", callback_data="my_balance"))
    m.add(types.InlineKeyboardButton("🛒・ شــــراء أرقــــام 🛒", callback_data="buy_numbers"))
    m.add(types.InlineKeyboardButton("👥・ شــــراء متــابعين 👥", callback_data="buy_followers"))
    m.add(types.InlineKeyboardButton("⭐・ شــــراء نجـــوم ⭐", callback_data="buy_stars"))
    m.add(types.InlineKeyboardButton("💳・ الشــــحن / اضافة رصيد 💳", callback_data="recharge"))
    m.add(types.InlineKeyboardButton("📢・ الاعـــلانات 📢", url="https://t.me/adscahneel"))
    m.add(types.InlineKeyboardButton("💬・ الدعــــم الفـــني 💬", url=f"https://t.me/{SUPPORT_USERNAME.replace('@','')}"))
    return m

def categories_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(types.InlineKeyboardButton("📩 تليجرام", callback_data="cat_telegram"))
    m.add(types.InlineKeyboardButton("💚 واتساب", callback_data="cat_whatsapp"))
    m.add(types.InlineKeyboardButton("📸 انستا", callback_data="cat_insta"))
    m.add(types.InlineKeyboardButton("🎵 تيك توك", callback_data="cat_tiktok"))
    m.add(types.InlineKeyboardButton("👤 فيسبوك", callback_data="cat_facebook"))
    m.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_main"))
    return m

def followers_main_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    for k,name in FOLLOWERS_PLATFORMS.items(): m.add(types.InlineKeyboardButton(name, callback_data=f"follow_{k}"))
    m.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_main")); return m

def stars_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    for key, info in STARS_GIFTS.items(): m.add(types.InlineKeyboardButton(f"{info['name']} - {info['stars']} نجمة - ${info['price']}", callback_data=f"stars_{key}"))
    m.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_main")); return m

def qty_menu(platform):
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("10 = $0.09", callback_data=f"qty_{platform}_10"), types.InlineKeyboardButton("20 = $0.18", callback_data=f"qty_{platform}_20"))
    m.add(types.InlineKeyboardButton("50 = $0.45", callback_data=f"qty_{platform}_50"), types.InlineKeyboardButton("100 = $0.9", callback_data=f"qty_{platform}_100"))
    m.add(types.InlineKeyboardButton("✏️ عدد مخصص", callback_data=f"custom_{platform}"))
    m.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="buy_followers")); return m

def telegram_type_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(types.InlineKeyboardButton("✅ سليم (يشتغل تطبيقات)", callback_data="type_telegram_clean"))
    m.add(types.InlineKeyboardButton("🚫 عادي (سبام)", callback_data="type_telegram_spam"))
    m.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="buy_numbers")); return m

def menu_from_dict(d, prefix):
    m = types.InlineKeyboardMarkup(row_width=1)
    for k,v in d.items(): m.add(types.InlineKeyboardButton(f"{v['name']} - ${v['price']}", callback_data=f"{prefix}_{k}"))
    m.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_main")); return m

def recharge_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    for k,v in PAYMENT_METHODS.items(): m.add(types.InlineKeyboardButton(v['name'], callback_data=f"pay_{k}"))
    m.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_main")); return m

def insufficient_balance_markup(price):
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(types.InlineKeyboardButton(f"❌ رصيدك لا يكفي - تحتاج ${price}", callback_data="my_balance"))
    m.add(types.InlineKeyboardButton("💳 اذهب للشحن 💳", callback_data="recharge"))
    m.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_main")); return m

def buy_item_markup(key):
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(types.InlineKeyboardButton("💳 شراء فوري وخصم من الرصيد", callback_data=f"buynow_{key}"))
    m.add(types.InlineKeyboardButton("🛒 اضافة للسلة", callback_data=f"addcart_{key}"))
    m.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_main")); return m

@bot.message_handler(commands=['start'])
def start(msg):
    try:
        users = json.load(open(USERS_FILE,"r",encoding="utf-8")); users[str(msg.chat.id)] = msg.chat.first_name
        json.dump(users, open(USERS_FILE,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    except: pass
    if msg.chat.id == ADMIN_ID:
        bot.send_message(msg.chat.id, "👑 *أهلا بملك المتجر* 👑\n\n🎛️ *لوحة تحكم PrimeX Store*", parse_mode="Markdown", reply_markup=admin_main_menu())
        return
    ok, not_joined = check_force_sub(msg.chat.id)
    if not ok:
        bot.send_message(msg.chat.id, "⚠️ *نورتنا! اشترك اولا:*", parse_mode="Markdown", reply_markup=force_sub_markup(not_joined)); return
    bal = get_balance(msg.chat.id)
    welcome = f"👑 *أهلا بيك في PrimeX Store - King of Numbers* 👑\n━━━━━━━━━━━━━━━━\n💰 *رصيدك:* `${round(bal,2)}`\n⚡ *أسرع متجر أرقام في الوطن العربي*\n━━━━━━━━━━━━━━━━\n👇 *اختار من تحت:*"
    bot.send_message(msg.chat.id, welcome, parse_mode="Markdown", reply_markup=main_menu(msg.chat.id))

@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    if call.message.chat.id!= ADMIN_ID:
        ok, not_joined = check_force_sub(call.message.chat.id)
        if not ok and call.data!= "check_sub":
            bot.answer_callback_query(call.id, "اشترك اولا!"); return

    if call.data == "check_sub":
        ok, not_joined = check_force_sub(call.message.chat.id)
        if not ok: bot.answer_callback_query(call.id, "لسه مشتركتش!"); return
        bot.answer_callback_query(call.id, "تم ✅")
        bot.send_message(call.message.chat.id, f"💰 رصيدك: ${round(get_balance(call.message.chat.id),2)}", reply_markup=main_menu(call.message.chat.id)); return

    if call.data.startswith("admin_"):
        if call.message.chat.id!= ADMIN_ID: return
        if call.data == "admin_stats":
            stock = get_stock(); total_nums = sum(len(v) for v in stock.values()); orders = get_orders(); total_sales = sum(o.get("price",0) for o in orders); bals = get_balances(); total_bal = sum(float(v) for v in bals.values())
            txt = f"📊 الاحصائيات:\n📦 مخزون: {total_nums}\n⏳ معلقة: {len(pending_orders)}\n✅ مكتملة: {len(orders)}\n💰 مبيعات: ${round(total_sales,2)}\n💳 ارصدة: ${round(total_bal,2)}\n👥 عملاء: {len(bals)}"
            bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=admin_main_menu())
        elif call.data == "admin_stock":
            stock = get_stock(); txt="📦 المخزون:\n\n"
            for k,v in stock.items(): txt+=f"• {k}: {len(v)}\n"
            if not stock: txt+="فاضي"
            bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=admin_main_menu())
        elif call.data == "admin_add_info": bot.edit_message_text("➕ /add telegram_clean india +201234\n/add whatsapp indonesia +62...", call.message.chat.id, call.message.message_id, reply_markup=admin_main_menu())
        elif call.data == "admin_add_balance_info": bot.edit_message_text("💳 /addbalance USER_ID AMOUNT\nمثال: /addbalance 123456 5", call.message.chat.id, call.message.message_id, reply_markup=admin_main_menu())
        elif call.data == "admin_clear_stock":
            m = types.InlineKeyboardMarkup(); m.add(types.InlineKeyboardButton("✅ نعم", callback_data="admin_confirm_clear"), types.InlineKeyboardButton("❌ لا", callback_data="admin_cancel"))
            bot.edit_message_text("⚠️ مسح كل المخزون؟", call.message.chat.id, call.message.message_id, reply_markup=m)
        elif call.data == "admin_confirm_clear": save_stock({}); bot.edit_message_text("✅ تم المسح", call.message.chat.id, call.message.message_id, reply_markup=admin_main_menu())
        elif call.data == "admin_cancel": bot.edit_message_text("تم الالغاء", call.message.chat.id, call.message.message_id, reply_markup=admin_main_menu())
        elif call.data == "admin_view_as_user": bot.send_message(call.message.chat.id, "وضع العميل:", reply_markup=main_menu(call.message.chat.id))
        return

    if call.data == "my_balance":
        bal = get_balance(call.message.chat.id)
        m = types.InlineKeyboardMarkup(row_width=1); m.add(types.InlineKeyboardButton("💳 الشحن", callback_data="recharge")); m.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_main"))
        bot.edit_message_text(f"💰 رصيدك: ${round(bal,2)}\n\nالحد الأدنى للشحن {MIN_RECHARGE}$", call.message.chat.id, call.message.message_id, reply_markup=m)
    elif call.data == "recharge":
        txt = f"💳 *مركز شحن الرصيد - PrimeX Store* 💳\n━━━━━━━━━━━━\n💰 رصيدك: `${round(get_balance(call.message.chat.id),2)}`\n━━━━━━━━━━━━\n👇 *اختر طريقة الشحن:*\n⚠️ الحد الأدنى `{MIN_RECHARGE}$`"
        bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=recharge_menu())
    elif call.data.startswith("pay_"):
        method = call.data.replace("pay_","",1); info = PAYMENT_METHODS.get(method)
        pending_recharge[call.message.chat.id] = {"method": method}
        txt = f"{info['name']}\n━━━━━━━━━━━━\n{info['info']}\n━━━━━━━━━━━━\n\n📸 بعد التحويل ابعت سكرين + المبلغ\nمثال: `حولت 1$` + صورة\n⏳ يتم خلال 5-10 دقائق"
        bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="recharge")))
    elif call.data == "back_main": bot.edit_message_text(f"💰 رصيدك: ${round(get_balance(call.message.chat.id),2)}\nاختر الخدمة:", call.message.chat.id, call.message.message_id, reply_markup=main_menu(call.message.chat.id))
    elif call.data == "buy_numbers": bot.edit_message_text("🛒 *متجر الأرقام* 🛒\nاختر النوع:", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=categories_menu())
    elif call.data == "cat_telegram": bot.edit_message_text("📩 تليجرام - اختر النوع:", call.message.chat.id, call.message.message_id, reply_markup=telegram_type_menu())
    elif call.data == "cat_whatsapp": bot.edit_message_text("💚 واتساب:", call.message.chat.id, call.message.message_id, reply_markup=menu_from_dict(WHATSAPP, "buy_whatsapp"))
    elif call.data == "cat_insta": bot.edit_message_text("📸 انستا:", call.message.chat.id, call.message.message_id, reply_markup=menu_from_dict(INSTA, "buy_insta"))
    elif call.data == "cat_tiktok": bot.edit_message_text("🎵 تيك توك:", call.message.chat.id, call.message.message_id, reply_markup=menu_from_dict(TIKTOK, "buy_tiktok"))
    elif call.data == "cat_facebook": bot.edit_message_text("👤 فيسبوك:", call.message.chat.id, call.message.message_id, reply_markup=menu_from_dict(FACEBOOK, "buy_facebook"))
    elif call.data.startswith("type_telegram_"):
        t = call.data.split("_")[2]; d = CLEAN if t=="clean" else SPAM
        bot.edit_message_text(f"تليجرام - {t}:", call.message.chat.id, call.message.message_id, reply_markup=menu_from_dict(d, f"buy_telegram_{t}"))
    elif call.data.startswith("buy_"):
        parts = call.data.split("_")
        if parts[1]=="telegram": _,_,type_f,country = parts; d = CLEAN if type_f=="clean" else SPAM; info = d[country]; key = f"telegram_{type_f}_{country}"
        else: _,cat,country = parts; d = {"whatsapp":WHATSAPP,"insta":INSTA,"tiktok":TIKTOK,"facebook":FACEBOOK}[cat]; info = d[country]; key = f"{cat}_{country}"
        bot.edit_message_text(f"{info['name']} - ${info['price']}", call.message.chat.id, call.message.message_id, reply_markup=buy_item_markup(key))
    elif call.data.startswith("buynow_"):
        key = call.data.replace("buynow_","",1)
        if key.startswith("telegram_"): _,type_f,country = key.split("_"); d = CLEAN if type_f=="clean" else SPAM; info = d[country]
        else:
            cat,country = key.split("_"); d = {"whatsapp":WHATSAPP,"insta":INSTA,"tiktok":TIKTOK,"facebook":FACEBOOK}[cat]; info = d[country]
        bal = get_balance(call.message.chat.id)
        if bal < info["price"]:
            bot.edit_message_text(f"❌ *رصيدك لا يكفي*\n💰 رصيدك: ${round(bal,2)}\n💵 تحتاج: ${info['price']}\n\nروح اشحن الاول 👇", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=insufficient_balance_markup(info["price"]))
            return
        deduct_balance(call.message.chat.id, info["price"])
        pending_orders[call.message.chat.id] = {"key":key,"price":info["price"],"name":info["name"]}
        markup = types.InlineKeyboardMarkup(); markup.add(types.InlineKeyboardButton("✅ قبول", callback_data=f"accept_{call.message.chat.id}")); markup.add(types.InlineKeyboardButton("❌ رفض واسترجاع", callback_data=f"reject_refund_{call.message.chat.id}"))
        bot.send_message(ADMIN_ID, f"🔔 طلب رقم\n👤 {call.message.chat.id}\n📦 {info['name']} - ${info['price']}\n💳 تم الخصم", reply_markup=markup)
        bot.edit_message_text(f"✅ تم خصم ${info['price']}\n⏳ جاري التجهيز...", call.message.chat.id, call.message.message_id, reply_markup=main_menu(call.message.chat.id))
    elif call.data.startswith("accept_"):
        if call.message.chat.id!= ADMIN_ID: return
        cid = int(call.data.split("_")[1]); bot.send_message(call.message.chat.id, f"اكتب الرد للعميل {cid}:"); bot.register_next_step_handler(call.message, lambda m: do_send(m, cid))
    elif call.data.startswith("reject_refund_"):
        if call.message.chat.id!= ADMIN_ID: return
        cid = int(call.data.split("_")[1]); info = pending_orders.get(cid, {})
        if info: add_balance(cid, info.get("price",0)); bot.send_message(cid, f"❌ تم رفض طلبك واسترجاع ${info.get('price')}")
        if cid in pending_orders: del pending_orders[cid]
        bot.send_message(call.message.chat.id, "تم الرفض والاسترجاع")
    elif call.data == "buy_followers": bot.edit_message_text("👥 متجر المتابعين:", call.message.chat.id, call.message.message_id, reply_markup=followers_main_menu())
    elif call.data.startswith("follow_"):
        plat = call.data.replace("follow_","",1); bot.edit_message_text(f"{FOLLOWERS_PLATFORMS[plat]}\nاختر الكمية:", call.message.chat.id, call.message.message_id, reply_markup=qty_menu(plat))
    elif call.data.startswith("qty_"):
        _,plat,qty = call.data.split("_"); qty=int(qty); price=calc_price(qty); bal=get_balance(call.message.chat.id)
        if bal < price: bot.edit_message_text(f"❌ رصيدك لا يكفي - تحتاج ${price}", call.message.chat.id, call.message.message_id, reply_markup=insufficient_balance_markup(price)); return
        deduct_balance(call.message.chat.id, price); pending_orders[call.message.chat.id] = {"price":price,"name":f"{plat} {qty} متابع"}
        markup = types.InlineKeyboardMarkup(); markup.add(types.InlineKeyboardButton("✅ قبول", callback_data=f"accept_{call.message.chat.id}"))
        bot.send_message(ADMIN_ID, f"🔔 طلب متابعين\n👤 {call.message.chat.id}\n📦 {plat} {qty} - ${price}", reply_markup=markup)
        bot.send_message(call.message.chat.id, f"✅ تم خصم ${price} - جاري التنفيذ")
    elif call.data == "buy_stars": bot.edit_message_text("⭐ نجوم تليجرام:", call.message.chat.id, call.message.message_id, reply_markup=stars_menu())
    elif call.data.startswith("stars_"):
        key = call.data.replace("stars_","",1); info = STARS_GIFTS[key]; bal=get_balance(call.message.chat.id)
        if bal < info["price"]: bot.edit_message_text(f"❌ رصيدك لا يكفي - تحتاج ${info['price']}", call.message.chat.id, call.message.message_id, reply_markup=insufficient_balance_markup(info["price"])); return
        deduct_balance(call.message.chat.id, info["price"]); pending_orders[call.message.chat.id] = {"price":info["price"],"name":info["name"]}
        markup = types.InlineKeyboardMarkup(); markup.add(types.InlineKeyboardButton("✅ قبول", callback_data=f"accept_{call.message.chat.id}"))
        bot.send_message(ADMIN_ID, f"⭐ طلب نجوم\n👤 {call.message.chat.id}\n{info['name']} - ${info['price']}", reply_markup=markup)
        bot.send_message(call.message.chat.id, f"✅ تم خصم ${info['price']}")

def do_send(message, cid):
    txt = message.text; info = pending_orders.get(cid, {})
    save_order({"user_id":cid,"name":info.get("name"),"price":info.get("price"),"time":datetime.now().strftime("%Y-%m-%d %H:%M")})
    bot.send_message(cid, f"✅ تم التسليم:\n{info.get('name')} - ${info.get('price')}\nالتفاصيل: {txt}")
    bot.send_message(message.chat.id, f"تم الارسال للعميل {cid} ✅")
    try: bot.send_message(DELIVERY_CHANNEL_ID, f"✅ تسليم جديد\n👤 {cid}\n📦 {info.get('name')}\n💰 ${info.get('price')}\n📝 {txt}")
    except: pass
    if cid in pending_orders: del pending_orders[cid]

@bot.message_handler(content_types=['photo','document','text'])
def handler(message):
    if message.text and message.text.startswith("/"):
        if message.text.startswith("/addbalance"):
            if message.chat.id!= ADMIN_ID: return
            try:
                _, uid, amount = message.text.split()
                if float(amount) < MIN_RECHARGE: bot.send_message(message.chat.id, f"❌ الحد الأدنى {MIN_RECHARGE}$"); return
                new_bal = add_balance(int(uid), float(amount))
                bot.send_message(message.chat.id, f"✅ اضافة ${amount} للعميل {uid}\nرصيده: ${round(new_bal,2)}")
                bot.send_message(int(uid), f"✅ تم شحن رصيدك ${amount}$\n💰 رصيدك الحالي: ${round(new_bal,2)}")
            except Exception as e: bot.send_message(message.chat.id, f"خطأ: {e}\nالصح: /addbalance ID AMOUNT")
            return
        if message.text.startswith("/balance"):
            bot.send_message(message.chat.id, f"💰 رصيدك: ${round(get_balance(message.chat.id),2)}"); return
        return
    if message.chat.id in pending_recharge:
        m = re.search(r"(\d+\.?\d*)", message.text or "")
        if m and float(m.group(1)) < MIN_RECHARGE: bot.send_message(message.chat.id, f"❌ الحد الأدنى {MIN_RECHARGE}$"); return
        bot.send_message(message.chat.id, "✅ استلمت طلب الشحن، انتظار الادمن")
        try: bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        except: pass
        info = pending_recharge.get(message.chat.id)
        bot.send_message(ADMIN_ID, f"💳 طلب شحن\n👤 {message.chat.id}\nطريقة: {info.get('method')}\nرسالة: {message.text or 'صورة'}\n\n/addbalance {message.chat.id} المبلغ")
        return
    info = pending_orders.get(message.chat.id, {})
    if not info: return
    bot.send_message(message.chat.id, "✅ استلمت، انتظار الادمن")
    markup = types.InlineKeyboardMarkup(); markup.add(types.InlineKeyboardButton("✅ قبول", callback_data=f"accept_{message.chat.id}"))
    markup.add(types.InlineKeyboardButton("❌ رفض واسترجاع", callback_data=f"reject_refund_{message.chat.id}"))
    try: bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    except: pass
    bot.send_message(ADMIN_ID, f"🔔 طلب جديد (معلومات اضافية)\n{info.get('name')}\nعميل: {message.chat.id}", reply_markup=markup)

# ========== تشغيل 24/7 ==========
print("PrimeX Store V22 - 24/7 شغال...")
while True:
    try:
        bot.infinity_polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"خطأ: {e} - اعادة تشغيل بعد 5 ثواني")
        time.sleep(5)

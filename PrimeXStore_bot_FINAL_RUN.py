import telebot
from telebot import types
import json, os, time
from datetime import datetime

TOKEN = "8315190785:AAGY-gLTz8ZPXe9z4j-pTOhsNArJx6OwMu0"
ADMIN_ID = 8933825471
SUPPORT_USERNAME = "@PrimeXStore22"
ADS_USERNAME = "@adscahneel"
ADS_LINK = "https://t.me/adscahneel"
DELIVERY_CHANNEL_ID = -1004496209902
FORCE_CHANNELS = ["@PrimeXStore0", "@adscahneel", "@kingfreebots"]

bot = telebot.TeleBot(TOKEN)
pending_orders = {}
pending_recharge = {}
broadcast_mode = {}
admin_states = {}

# ===== NUMBERS =====
CLEAN = {
    "india": {"name": "🇮🇳 India Clean", "price": 0.3},
    "egypt": {"name": "🇪🇬 Egypt Clean", "price": 0.5},
    "vietnam": {"name": "🇻🇳 Vietnam Clean", "price": 0.9},
    "ksa": {"name": "🇸🇦 Saudi Arabia Clean", "price": 1.5},
    "pakistan": {"name": "🇵🇰 Pakistan Clean", "price": 0.7},
    "morocco": {"name": "🇲🇦 Morocco Clean", "price": 0.6},
    "myanmar": {"name": "🇲🇲 Myanmar Clean", "price": 0.3},
    "kenya": {"name": "🇰🇪 Kenya Clean", "price": 0.5},
    "indonesia": {"name": "🇮🇩 Indonesia Clean", "price": 0.6},
    "nigeria": {"name": "🇳🇬 Nigeria Clean", "price": 0.5},
}
SPAM = {
    "india_spam": {"name": "🇮🇳 India Spam", "price": 0.2},
    "random": {"name": "🌍 Random Spam", "price": 0.3},
    "random_rare": {"name": "🌍 Rare & Old Countries Spam", "price": 0.45},
    "usa": {"name": "🇺🇸 USA Spam", "price": 0.25},
    "myanmar_spam": {"name": "🇲🇲 Myanmar Spam", "price": 0.2},
}
WHATSAPP = {
    "indonesia": {"name": "💚 WhatsApp Indonesia", "price": 0.25},
}
TIKTOK_NUMS = {
    "germany": {"name": "🇩🇪 TikTok Germany", "price": 0.2},
    "sudan": {"name": "🇸🇩 TikTok Sudan", "price": 0.15},
}
FACEBOOK_NUMS = {
    "indonesia": {"name": "🇮🇩 Facebook Indonesia", "price": 0.1},
    "sudan": {"name": "🇸🇩 Facebook Sudan", "price": 0.1},
    "ghana": {"name": "🇬🇭 Facebook Ghana", "price": 0.15},
}
INSTAGRAM_NUMS = {
    "ghana": {"name": "🇬🇭 Instagram Ghana", "price": 0.15},
}
TINDER_NUMS = {
    "indonesia": {"name": "🇮🇩 Tinder Indonesia", "price": 0.07},
    "mozambique": {"name": "🇲🇿 Tinder Mozambique", "price": 0.09},
}

FOLLOWERS = {
    "tiktok": {"name": "🎵 TikTok Followers", "price": 3.5},
    "instagram": {"name": "📸 Instagram Followers", "price": 4.0},
    "facebook": {"name": "👤 Facebook Followers", "price": 3.0},
    "youtube": {"name": "▶️ YouTube Subscribers", "price": 5.0},
    "telegram": {"name": "📩 Telegram Members", "price": 2.5},
}
STARS = {
    "15": {"name": "🧸 Bear 15 Stars", "price": 0.18},
    "25": {"name": "🌹 Rose 25 Stars", "price": 0.29},
    "50": {"name": "🎂 Cake 50 Stars", "price": 0.57},
    "100": {"name": "💍 Ring 100 Stars", "price": 1.15},
}
# ===== ALL PAYMENT METHODS BACK =====
PAYMENTS = {
    "cwallet": {"name": "👛 C-Wallet", "info": "`61824874`"},
    "usdt_erc20": {"name": "💎 USDT ERC20", "info": "`0x8D7dDE7719e9d6D3e5175CE170Fae00372715493`"},
    "usdt_bep20": {"name": "💛 USDT BEP20", "info": "`0xA7fE0a5Ae6Adcd5b47df238F836449b4d0866155`"},
    "usdt_trc20": {"name": "❤️ USDT TRC20", "info": "`TRHUB8kuMpdCoDzST6c4AJ4cJdk6tToz97`"},
    "usdt_polygon": {"name": "💜 USDT POLYGON", "info": "`0xA7fE0a5Ae6Adcd5b47df238F836449b4d0866155`"},
    "faucetpay": {"name": "🚰 FaucetPay", "info": "`@primexstore22`"},
    "gram": {"name": "💎 GRAM TON", "info": "`UQBdPqUEG7TkF2TYWDOEclSYPDec4-HGOsN5ss0Zcnby1mCL`"},
}

BALANCE_FILE="balance.json"; USERS_FILE="users.json"; ORDERS_FILE="orders.json"; MODS_FILE="mods.json"
for f,d in [(BALANCE_FILE,"{}"),(USERS_FILE,"{}"),(ORDERS_FILE,"[]"),(MODS_FILE,"[]")]:
    if not os.path.exists(f): open(f,"w",encoding="utf-8").write(d)

def get_balances():
    try: return json.load(open(BALANCE_FILE,"r",encoding="utf-8"))
    except: return {}
def save_balances(b): json.dump(b, open(BALANCE_FILE,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
def get_balance(uid): return float(get_balances().get(str(uid),0))
def add_balance(uid,amount):
    b=get_balances(); b[str(uid)]=float(b.get(str(uid),0))+float(amount); save_balances(b); return b[str(uid)]
def deduct_balance(uid,amount):
    b=get_balances(); bal=float(b.get(str(uid),0))
    if bal<amount: return False
    b[str(uid)]=bal-amount; save_balances(b); return True
def get_mods():
    try: return json.load(open(MODS_FILE,"r",encoding="utf-8"))
    except: return []
def save_mods(m): json.dump(m, open(MODS_FILE,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
def is_admin(uid): return uid==ADMIN_ID or uid in get_mods()
def get_users():
    try: return json.load(open(USERS_FILE,"r",encoding="utf-8"))
    except: return {}
def save_users(u): json.dump(u, open(USERS_FILE,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

def check_force_sub(uid):
    nj=[]
    for ch in FORCE_CHANNELS:
        try:
            m=bot.get_chat_member(ch,uid)
            if m.status in ['left','kicked']: nj.append(ch)
        except: pass
    return len(nj)==0,nj
def force_sub_markup(nj):
    m=types.InlineKeyboardMarkup(row_width=1)
    for ch in nj: m.add(types.InlineKeyboardButton(f"📢 {ch}",url=f"https://t.me/{ch.replace('@','')}"))
    m.add(types.InlineKeyboardButton("✅ Done",callback_data="check_sub")); return m

def admin_main_menu():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("📊 احصائيات",callback_data="admin_stats"),types.InlineKeyboardButton("💰 اضافة رصيد",callback_data="admin_add_balance"))
    m.add(types.InlineKeyboardButton("📢 اذاعة",callback_data="admin_broadcast_info"),types.InlineKeyboardButton("👮 اضافة مشرف",callback_data="admin_add_mod"))
    m.add(types.InlineKeyboardButton("📋 المشرفين",callback_data="admin_list_mods"),types.InlineKeyboardButton("🗑️ حذف مشرف",callback_data="admin_del_mod"))
    m.add(types.InlineKeyboardButton("📦 المخزون",callback_data="admin_stock"),types.InlineKeyboardButton("👥 وضع العميل",callback_data="admin_view_as_user"))
    return m

def main_menu(uid=None):
    bal=get_balance(uid) if uid else 0
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton(f"💰 Balance: ${round(bal,2)}",callback_data="my_balance"),types.InlineKeyboardButton("🛒 Numbers",callback_data="buy_numbers"))
    m.add(types.InlineKeyboardButton("👥 Followers",callback_data="buy_followers"),types.InlineKeyboardButton("⭐ Stars Gifts",callback_data="buy_stars"))
    m.add(types.InlineKeyboardButton("💳 Recharge",callback_data="recharge"),types.InlineKeyboardButton(f"📢 {ADS_USERNAME}",url=ADS_LINK))
    m.add(types.InlineKeyboardButton(f"💬 Support {SUPPORT_USERNAME}",url=f"https://t.me/{SUPPORT_USERNAME.replace('@','')}"))
    return m

def recharge_menu():
    m=types.InlineKeyboardMarkup(row_width=2)
    for k,v in PAYMENTS.items(): m.add(types.InlineKeyboardButton(v['name'],callback_data=f"pay_{k}"))
    m.add(types.InlineKeyboardButton("⬅️ Back",callback_data="back_main")); return m

def numbers_menu():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("✨ Clean Numbers",callback_data="type_clean"),types.InlineKeyboardButton("🔥 Spam Numbers",callback_data="type_spam"))
    m.add(types.InlineKeyboardButton("💚 WhatsApp Numbers",callback_data="type_whatsapp"),types.InlineKeyboardButton("🎵 TikTok Numbers",callback_data="type_tiktok_nums"))
    m.add(types.InlineKeyboardButton("👤 Facebook Numbers",callback_data="type_facebook_nums"),types.InlineKeyboardButton("📸 Instagram Numbers",callback_data="type_insta_nums"))
    m.add(types.InlineKeyboardButton("🔥 Tinder Numbers",callback_data="type_tinder_nums"))
    m.add(types.InlineKeyboardButton("⬅️ Back",callback_data="back_main")); return m

def build_menu(data):
    m=types.InlineKeyboardMarkup(row_width=2)
    for k,v in data.items(): m.add(types.InlineKeyboardButton(f"{v['name']} ${v['price']}",callback_data=f"buy_{k}_{v['price']}"))
    return m

def simple_menu(data, prefix):
    m=types.InlineKeyboardMarkup(row_width=2)
    for k,v in data.items(): m.add(types.InlineKeyboardButton(f"{v['name']} ${v['price']}",callback_data=f"{prefix}_{k}"))
    m.add(types.InlineKeyboardButton("⬅️ Back",callback_data="buy_numbers")); return m

@bot.message_handler(commands=['start'])
def start(msg):
    users=get_users(); is_new=str(msg.chat.id) not in users
    users[str(msg.chat.id)]={"name":msg.chat.first_name,"username":msg.chat.username,"date":datetime.now().strftime("%Y-%m-%d %H:%M")}; save_users(users)
    if is_new and msg.chat.id!=ADMIN_ID:
        try:
            uname=f"@{msg.chat.username}" if msg.chat.username else "No username"
            bot.send_message(ADMIN_ID,f"🔔 New User Joined\n👤 {msg.chat.first_name}\n🆔 `{msg.chat.id}`\n🔗 {uname}",parse_mode="Markdown")
        except: pass
    if is_admin(msg.chat.id):
        bot.send_message(msg.chat.id,"👑 لوحة تحكم الملك - كل حاجة بالعربي هنا",reply_markup=admin_main_menu()); return
    ok,nj=check_force_sub(msg.chat.id)
    if not ok: bot.send_message(msg.chat.id,"⚠️ Please subscribe first:",reply_markup=force_sub_markup(nj)); return
    bot.send_message(msg.chat.id,f"👑 PrimeX Store\nWelcome! Your Balance: ${round(get_balance(msg.chat.id),2)}",reply_markup=main_menu(msg.chat.id))

@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    uid=call.message.chat.id
    if call.data=="check_sub":
        ok,_=check_force_sub(uid)
        if not ok: bot.answer_callback_query(call.id,"Not yet!"); return
        bot.send_message(uid,"✅ Done",reply_markup=main_menu(uid)); return
    if not is_admin(uid):
        ok,_=check_force_sub(uid)
        if not ok: bot.answer_callback_query(call.id,"Subscribe first!"); return

    if call.data=="admin_stats" and is_admin(uid):
        bals=get_balances(); total=sum(float(v) for v in bals.values()); users=get_users()
        bot.edit_message_text(f"📊 الاحصائيات\n💰 اجمالي الارصدة: ${round(total,2)}\n👥 العملاء: {len(users)}\n⏳ معلقة: {len(pending_orders)}\n👮 المشرفين: {len(get_mods())}",uid,call.message.message_id,reply_markup=admin_main_menu())
    elif call.data=="admin_add_balance" and is_admin(uid):
        admin_states[uid]={"step":"await_id"}; bot.edit_message_text("💰 اضافة رصيد\n\n📩 ابعت ايدي العميل:",uid,call.message.message_id,reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ الغاء",callback_data="admin_cancel")))
    elif call.data=="admin_broadcast_info" and is_admin(uid):
        broadcast_mode[uid]=True; bot.edit_message_text("📢 ابعت رسالة الاذاعة:\n/cancel للالغاء",uid,call.message.message_id,reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ الغاء",callback_data="admin_cancel")))
    elif call.data=="admin_add_mod" and uid==ADMIN_ID:
        admin_states[uid]={"step":"await_mod_id"}; bot.edit_message_text("👮 اضافة مشرف\n\n📩 ابعت ايدي المشرف:",uid,call.message.message_id,reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ الغاء",callback_data="admin_cancel")))
    elif call.data=="admin_list_mods" and is_admin(uid):
        mods=get_mods(); txt="📋 المشرفين:\n\n"+"\n".join([f"👮 `{m}`" for m in mods]) if mods else "لا يوجد مشرفين"
        bot.edit_message_text(txt,uid,call.message.message_id,parse_mode="Markdown",reply_markup=admin_main_menu())
    elif call.data=="admin_del_mod" and uid==ADMIN_ID:
        admin_states[uid]={"step":"await_del_mod"}; bot.edit_message_text("🗑️ حذف مشرف\n\n📩 ابعت ايدي المشرف:",uid,call.message.message_id,reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ الغاء",callback_data="admin_cancel")))
    elif call.data=="admin_cancel":
        if uid in broadcast_mode: del broadcast_mode[uid]
        if uid in admin_states: del admin_states[uid]
        bot.edit_message_text("تم الالغاء",uid,call.message.message_id,reply_markup=admin_main_menu() if is_admin(uid) else main_menu(uid))
    elif call.data=="admin_stock" and is_admin(uid):
        bot.edit_message_text("📦 المخزون\nClean 10 + Spam 5 + WhatsApp 1 + TikTok 2 + FB 3 + Insta 1 + Tinder 2 ✅",uid,call.message.message_id,reply_markup=admin_main_menu())
    elif call.data=="admin_view_as_user" and is_admin(uid):
        bot.send_message(uid,"User View:",reply_markup=main_menu(uid))
    elif call.data=="my_balance":
        bot.edit_message_text(f"💰 Your Balance: ${round(get_balance(uid),2)}",uid,call.message.message_id,reply_markup=main_menu(uid))
    elif call.data=="recharge":
        bot.edit_message_text(f"💳 Recharge - Balance: ${round(get_balance(uid),2)}\nChoose payment method:",uid,call.message.message_id,reply_markup=recharge_menu())
    elif call.data.startswith("pay_"):
        method=call.data.replace("pay_","",1); info=PAYMENTS.get(method); pending_recharge[uid]={"method":method}
        bot.edit_message_text(f"💳 {info['name']}\n\nAddress:\n{info['info']}\n\n📸 Send screenshot + amount",uid,call.message.message_id,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("⬅️ Back",callback_data="recharge")))
    elif call.data=="back_main":
        bot.edit_message_text(f"💰 Balance: ${round(get_balance(uid),2)}",uid,call.message.message_id,reply_markup=main_menu(uid))
    elif call.data=="buy_numbers":
        bot.edit_message_text("🛒 Choose Numbers Category:",uid,call.message.message_id,reply_markup=numbers_menu())
    elif call.data=="type_clean": bot.edit_message_text("✨ Clean Numbers:",uid,call.message.message_id,reply_markup=simple_menu(CLEAN,"clean"))
    elif call.data=="type_spam": bot.edit_message_text("🔥 Spam Numbers:",uid,call.message.message_id,reply_markup=simple_menu(SPAM,"spam"))
    elif call.data=="type_whatsapp": bot.edit_message_text("💚 WhatsApp Numbers:",uid,call.message.message_id,reply_markup=simple_menu(WHATSAPP,"wa"))
    elif call.data=="type_tiktok_nums": bot.edit_message_text("🎵 TikTok Numbers:",uid,call.message.message_id,reply_markup=simple_menu(TIKTOK_NUMS,"tiktokn"))
    elif call.data=="type_facebook_nums": bot.edit_message_text("👤 Facebook Numbers:",uid,call.message.message_id,reply_markup=simple_menu(FACEBOOK_NUMS,"fbn"))
    elif call.data=="type_insta_nums": bot.edit_message_text("📸 Instagram Numbers:",uid,call.message.message_id,reply_markup=simple_menu(INSTAGRAM_NUMS,"instan"))
    elif call.data=="type_tinder_nums": bot.edit_message_text("🔥 Tinder Numbers:",uid,call.message.message_id,reply_markup=simple_menu(TINDER_NUMS,"tindern"))
    elif call.data=="buy_followers":
        m=types.InlineKeyboardMarkup(row_width=2)
        for k,v in FOLLOWERS.items(): m.add(types.InlineKeyboardButton(f"{v['name']} ${v['price']}",callback_data=f"followers_{k}"))
        m.add(types.InlineKeyboardButton("⬅️ Back",callback_data="back_main"))
        bot.edit_message_text("👥 Buy Followers - Choose Platform:",uid,call.message.message_id,reply_markup=m)
    elif call.data=="buy_stars":
        m=types.InlineKeyboardMarkup(row_width=2)
        for k,v in STARS.items(): m.add(types.InlineKeyboardButton(f"{v['name']} ${v['price']}",callback_data=f"stars_{k}"))
        m.add(types.InlineKeyboardButton("⬅️ Back",callback_data="back_main"))
        bot.edit_message_text("⭐ Buy Telegram Stars Gifts:",uid,call.message.message_id,reply_markup=m)
    elif call.data.startswith(("clean_","spam_","wa_","tiktokn_","fbn_","instan_","tindern_","followers_","stars_")):
        price=0; name=""
        if call.data.startswith("clean_"): k=call.data.replace("clean_","",1); info=CLEAN[k]; price=info["price"]; name=info["name"]
        elif call.data.startswith("spam_"): k=call.data.replace("spam_","",1); info=SPAM[k]; price=info["price"]; name=info["name"]
        elif call.data.startswith("wa_"): k=call.data.replace("wa_","",1); info=WHATSAPP[k]; price=info["price"]; name=info["name"]
        elif call.data.startswith("tiktokn_"): k=call.data.replace("tiktokn_","",1); info=TIKTOK_NUMS[k]; price=info["price"]; name=info["name"]
        elif call.data.startswith("fbn_"): k=call.data.replace("fbn_","",1); info=FACEBOOK_NUMS[k]; price=info["price"]; name=info["name"]
        elif call.data.startswith("instan_"): k=call.data.replace("instan_","",1); info=INSTAGRAM_NUMS[k]; price=info["price"]; name=info["name"]
        elif call.data.startswith("tindern_"): k=call.data.replace("tindern_","",1); info=TINDER_NUMS[k]; price=info["price"]; name=info["name"]
        elif call.data.startswith("followers_"): k=call.data.replace("followers_","",1); info=FOLLOWERS[k]; price=info["price"]; name=info["name"]
        elif call.data.startswith("stars_"): k=call.data.replace("stars_","",1); info=STARS[k]; price=info["price"]; name=info["name"]
        if get_balance(uid)<price: bot.answer_callback_query(call.id,f"Need ${price}"); return
        deduct_balance(uid,price); pending_orders[uid]={"price":price,"name":name}
        markup=types.InlineKeyboardMarkup(row_width=2); markup.add(types.InlineKeyboardButton("✅ Accept",callback_data=f"accept_{uid}"),types.InlineKeyboardButton("❌ Reject+Refund",callback_data=f"reject_refund_{uid}"))
        bot.send_message(ADMIN_ID,f"🔔 New Order\n👤 {uid}\n📦 {name} - ${price}",reply_markup=markup)
        bot.edit_message_text(f"✅ Deducted ${price}\n⏳ Waiting for admin delivery\nPlease send your username if needed",uid,call.message.message_id,reply_markup=main_menu(uid))
    elif call.data.startswith("accept_"):
        if not is_admin(uid): return
        if call.data.startswith("accept_recharge_"):
            cid=int(call.data.replace("accept_recharge_","")); admin_states[uid]={"step":"await_amount","target":cid}; bot.send_message(uid,f"💰 Enter amount for {cid}:"); return
        cid=int(call.data.replace("accept_","")); bot.send_message(uid,f"✏️ Write reply for client {cid}:"); bot.register_next_step_handler(call.message, lambda m: do_send(m,cid))
    elif call.data.startswith("reject_"):
        if not is_admin(uid): return
        if call.data.startswith("reject_recharge_"):
            cid=int(call.data.replace("reject_recharge_","")); bot.send_message(cid,"❌ Recharge rejected");
            if cid in pending_recharge: del pending_recharge[cid]; bot.send_message(uid,"Rejected"); return
        if "refund" in call.data:
            cid=int(call.data.replace("reject_refund_","")); info=pending_orders.get(cid,{})
            if info: add_balance(cid,info.get("price",0)); bot.send_message(cid,f"❌ Order rejected & refunded ${info.get('price')}")
            if cid in pending_orders: del pending_orders[cid]; bot.send_message(uid,"Rejected & Refunded")

def do_send(message,cid):
    txt=message.text; info=pending_orders.get(cid,{})
    bot.send_message(cid,f"✅ Delivered:\n📦 {info.get('name')}\n💰 ${info.get('price')}\n\n{txt}"); bot.send_message(message.chat.id,f"✅ Sent to {cid}")
    if cid in pending_orders: del pending_orders[cid]

@bot.message_handler(content_types=['photo','document','text'])
def handler(message):
    uid=message.chat.id
    if uid in admin_states:
        st=admin_states[uid]
        if st["step"]=="await_id":
            try: target=int(message.text); admin_states[uid]={"step":"await_amount","target":target}; bot.send_message(uid,f"✅ ID {target}\n💰 Enter amount:"); return
            except: bot.send_message(uid,"❌ Send correct ID"); return
        elif st["step"]=="await_amount":
            try: amount=float(message.text); target=st["target"]; new_bal=add_balance(target,amount); bot.send_message(uid,f"✅ Added ${amount} to {target}\nBalance ${round(new_bal,2)}",reply_markup=admin_main_menu()); bot.send_message(target,f"✅ Your balance recharged ${amount}$\n💰 Balance: ${round(new_bal,2)}")
            except: bot.send_message(uid,"❌ Wrong amount")
            if target in pending_recharge: del pending_recharge[target]
            if uid in admin_states: del admin_states[uid]; return
        elif st["step"]=="await_mod_id":
            try: mid=int(message.text); mods=get_mods()
            if mid not in mods: mods.append(mid); save_mods(mods)
            bot.send_message(uid,f"✅ Added mod {mid}",reply_markup=admin_main_menu()); del admin_states[uid]; return
            except: bot.send_message(uid,"❌ Wrong ID"); return
        elif st["step"]=="await_del_mod":
            try: mid=int(message.text); mods=get_mods()
            if mid in mods: mods.remove(mid); save_mods(mods); bot.send_message(uid,f"✅ Deleted {mid}",reply_markup=admin_main_menu())
            else: bot.send_message(uid,"❌ Not found",reply_markup=admin_main_menu())
            del admin_states[uid]; return
            except: bot.send_message(uid,"❌ Wrong ID"); return
    if is_admin(uid) and broadcast_mode.get(uid):
        users=list(get_users().keys())+list(get_balances().keys()); users=list(set(users)); count=0
        bot.send_message(uid,f"📢 Broadcasting to {len(users)}...")
        for u in users:
            try: bot.copy_message(int(u),uid,message.message_id); count+=1; time.sleep(0.05)
            except: pass
        bot.send_message(uid,f"✅ Broadcast done to {count}",reply_markup=admin_main_menu()); del broadcast_mode[uid]; return
    if message.text and message.text.startswith("/addbalance"):
        if not is_admin(uid): return
        try: _,tid,amount=message.text.split(); add_balance(int(tid),float(amount)); bot.send_message(uid,f"✅ Added ${amount}"); bot.send_message(int(tid),f"✅ Balance recharged ${amount}$")
        except: bot.send_message(uid,"/addbalance ID AMOUNT"); return
    if message.text=="/cancel" and is_admin(uid):
        if uid in broadcast_mode: del broadcast_mode[uid]
        if uid in admin_states: del admin_states[uid]
        bot.send_message(uid,"تم الالغاء",reply_markup=admin_main_menu()); return
    if uid in pending_recharge:
        markup=types.InlineKeyboardMarkup(row_width=2); markup.add(types.InlineKeyboardButton("✅ Accept",callback_data=f"accept_recharge_{uid}"),types.InlineKeyboardButton("❌ Reject",callback_data=f"reject_recharge_{uid}"))
        try: bot.forward_message(ADMIN_ID,uid,message.message_id)
        except: pass
        bot.send_message(ADMIN_ID,f"💳 Recharge Request\n👤 {uid}\nMethod: {pending_recharge[uid]['method']}",reply_markup=markup)
        bot.send_message(uid,"✅ Received, waiting admin approval"); return
    if uid in pending_orders and not is_admin(uid):
        try: bot.forward_message(ADMIN_ID,uid,message.message_id)
        except: pass

print("PrimeX V32 - English Services + Arabic Admin + All Payments...")
bot.remove_webhook(); time.sleep(1)
while True:
    try: bot.infinity_polling(none_stop=True, timeout=20)
    except Exception as e: print(e); time.sleep(5)

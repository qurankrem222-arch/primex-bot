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

FOLLOWERS_PLATFORMS = {"tiktok":{"name":"🎵 تيك توك","price":3.5},"instagram":{"name":"📸 انستا","price":4.0},"facebook":{"name":"👤 فيسبوك","price":3.0},"youtube":{"name":"▶️ يوتيوب","price":5.0},"telegram":{"name":"📩 تليجرام","price":2.5}}
STARS_GIFTS = {"15":{"name":"🧸 دب 15⭐","price":0.18},"25":{"name":"🌹 وردة 25⭐","price":0.29},"50":{"name":"🎂 كيكة 50⭐","price":0.57},"100":{"name":"💍 خاتم 100⭐","price":1.15}}
PAYMENT_METHODS = {"cwallet":{"name":"👛 C-Wallet","info":"61824874"},"usdt_trc20":{"name":"❤️ USDT TRC20","info":"TRHUB8kuMpdCoDzST6c4AJ4cJdk6tToz97"},"usdt_bep20":{"name":"💛 USDT BEP20","info":"0xA7fE0a5Ae6Adcd5b47df238F836449b4d0866155"}}

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
    m.add(types.InlineKeyboardButton("✅ تحققت",callback_data="check_sub")); return m

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
    m.add(types.InlineKeyboardButton(f"💰 ${round(bal,2)}",callback_data="my_balance"),types.InlineKeyboardButton("🛒 ارقام",callback_data="buy_numbers"))
    m.add(types.InlineKeyboardButton("👥 متابعين",callback_data="buy_followers"),types.InlineKeyboardButton("⭐ نجوم",callback_data="buy_stars"))
    m.add(types.InlineKeyboardButton("💳 الشحن",callback_data="recharge"),types.InlineKeyboardButton(f"📢 {ADS_USERNAME}",url=ADS_LINK))
    m.add(types.InlineKeyboardButton(f"💬 {SUPPORT_USERNAME}",url=f"https://t.me/{SUPPORT_USERNAME.replace('@','')}"))
    return m

def recharge_menu():
    m=types.InlineKeyboardMarkup(row_width=2)
    for k,v in PAYMENT_METHODS.items(): m.add(types.InlineKeyboardButton(v['name'],callback_data=f"pay_{k}"))
    m.add(types.InlineKeyboardButton("⬅️ رجوع",callback_data="back_main")); return m

def numbers_menu():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("🇮🇳 سليم $0.3",callback_data="num_india_clean"),types.InlineKeyboardButton("🇪🇬 سليم $0.5",callback_data="num_egypt_clean"))
    m.add(types.InlineKeyboardButton("🇮🇳 عادي $0.2",callback_data="num_india_spam"),types.InlineKeyboardButton("🌍 عشوائي $0.3",callback_data="num_random_spam"))
    m.add(types.InlineKeyboardButton("⬅️ رجوع",callback_data="back_main")); return m

def followers_menu():
    m=types.InlineKeyboardMarkup(row_width=2)
    for k,v in FOLLOWERS_PLATFORMS.items(): m.add(types.InlineKeyboardButton(f"{v['name']} ${v['price']}",callback_data=f"followers_{k}"))
    m.add(types.InlineKeyboardButton("⬅️ رجوع",callback_data="back_main")); return m

def stars_menu():
    m=types.InlineKeyboardMarkup(row_width=2)
    for k,v in STARS_GIFTS.items(): m.add(types.InlineKeyboardButton(f"{v['name']} ${v['price']}",callback_data=f"stars_{k}"))
    m.add(types.InlineKeyboardButton("⬅️ رجوع",callback_data="back_main")); return m

@bot.message_handler(commands=['start'])
def start(msg):
    users=get_users(); is_new=str(msg.chat.id) not in users
    users[str(msg.chat.id)]={"name":msg.chat.first_name,"username":msg.chat.username,"date":datetime.now().strftime("%Y-%m-%d %H:%M")}; save_users(users)
    if is_new and msg.chat.id!=ADMIN_ID:
        try:
            uname=f"@{msg.chat.username}" if msg.chat.username else "بدون يوزر"
            bot.send_message(ADMIN_ID,f"🔔 عضو جديد 🔔\n👤 {msg.chat.first_name}\n🆔 `{msg.chat.id}`\n🔗 {uname}\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n👥 الاجمالي: {len(users)}",parse_mode="Markdown")
        except: pass
    if is_admin(msg.chat.id):
        bot.send_message(msg.chat.id,"👑 لوحة تحكم الملك 👑",reply_markup=admin_main_menu()); return
    ok,nj=check_force_sub(msg.chat.id)
    if not ok:
        bot.send_message(msg.chat.id,"⚠️ اشترك اولا:",reply_markup=force_sub_markup(nj)); return
    bot.send_message(msg.chat.id,f"👑 PrimeX Store\n💰 رصيدك: ${round(get_balance(msg.chat.id),2)}",reply_markup=main_menu(msg.chat.id))

@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    uid=call.message.chat.id
    if call.data=="check_sub":
        ok,_=check_force_sub(uid)
        if not ok: bot.answer_callback_query(call.id,"لسه!"); return
        bot.send_message(uid,"✅ تم",reply_markup=main_menu(uid)); return
    if uid!=ADMIN_ID:
        ok,_=check_force_sub(uid)
        if not ok and not call.data.startswith("check"): bot.answer_callback_query(call.id,"اشترك اولا!"); return

    if call.data=="admin_stats" and is_admin(uid):
        bals=get_balances(); total=sum(float(v) for v in bals.values()); users=get_users()
        bot.edit_message_text(f"📊 الاحصائيات\n💰 الارصدة: ${round(total,2)}\n👥 عملاء: {len(users)}\n⏳ معلقة: {len(pending_orders)}\n👮 مشرفين: {len(get_mods())}",uid,call.message.message_id,reply_markup=admin_main_menu())
    elif call.data=="admin_add_balance" and is_admin(uid):
        admin_states[uid]={"step":"await_id"}; bot.edit_message_text("💰 اضافة رصيد\n\n📩 ابعت ايدي العميل:",uid,call.message.message_id,reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ الغاء",callback_data="admin_cancel")))
    elif call.data=="admin_broadcast_info" and is_admin(uid):
        broadcast_mode[uid]=True; bot.edit_message_text("📢 ابعت رسالة الاذاعة:\n/cancel للالغاء",uid,call.message.message_id,reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ الغاء",callback_data="admin_cancel")))
    elif call.data=="admin_add_mod" and uid==ADMIN_ID:
        admin_states[uid]={"step":"await_mod_id"}; bot.edit_message_text("👮 اضافة مشرف\n\n📩 ابعت ايدي المشرف الجديد:",uid,call.message.message_id,reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("❌ الغاء",callback_data="admin_cancel")))
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
        bot.edit_message_text("📦 المخزون تمام",uid,call.message.message_id,reply_markup=admin_main_menu())
    elif call.data=="admin_view_as_user" and is_admin(uid):
        bot.send_message(uid,"👥 وضع العميل:",reply_markup=main_menu(uid))
    elif call.data=="my_balance":
        bot.edit_message_text(f"💰 رصيدك: ${round(get_balance(uid),2)}",uid,call.message.message_id,reply_markup=main_menu(uid))
    elif call.data=="recharge":
        bot.edit_message_text(f"💳 الشحن - رصيدك ${round(get_balance(uid),2)}",uid,call.message.message_id,reply_markup=recharge_menu())
    elif call.data.startswith("pay_"):
        method=call.data.replace("pay_","",1); info=PAYMENT_METHODS.get(method); pending_recharge[uid]={"method":method}
        bot.edit_message_text(f"{info['name']}\n{info['info']}\n\n📸 ابعت سكرين + المبلغ",uid,call.message.message_id,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("⬅️ رجوع",callback_data="recharge")))
    elif call.data=="back_main":
        bot.edit_message_text(f"💰 رصيدك: ${round(get_balance(uid),2)}",uid,call.message.message_id,reply_markup=main_menu(uid))
    elif call.data=="buy_numbers":
        bot.edit_message_text("🛒 اختر الرقم:",uid,call.message.message_id,reply_markup=numbers_menu())
    elif call.data=="buy_followers":
        bot.edit_message_text("👥 اختر المنصة:",uid,call.message.message_id,reply_markup=followers_menu())
    elif call.data=="buy_stars":
        bot.edit_message_text("⭐ اختر الهدية:",uid,call.message.message_id,reply_markup=stars_menu())
    elif call.data.startswith("num_"):
        price=0.3 if "india" in call.data else 0.5
        if "spam" in call.data: price=0.2
        if get_balance(uid)<price: bot.answer_callback_query(call.id,f"رصيدك لا يكفي تحتاج ${price}"); return
        deduct_balance(uid,price); pending_orders[uid]={"price":price,"name":call.data}
        markup=types.InlineKeyboardMarkup(row_width=2); markup.add(types.InlineKeyboardButton("✅ موافقة",callback_data=f"accept_{uid}"),types.InlineKeyboardButton("❌ رفض+استرجاع",callback_data=f"reject_refund_{uid}"))
        bot.send_message(ADMIN_ID,f"🔔 طلب رقم\n👤 {uid}\n📦 {call.data} - ${price}",reply_markup=markup)
        bot.edit_message_text(f"✅ خصم ${price}\n⏳ انتظار الادمن",uid,call.message.message_id,reply_markup=main_menu(uid))
    elif call.data.startswith("followers_"):
        plat=call.data.replace("followers_","",1); price=FOLLOWERS_PLATFORMS[plat]["price"]; name=FOLLOWERS_PLATFORMS[plat]["name"]
        if get_balance(uid)<price: bot.answer_callback_query(call.id,f"تحتاج ${price}"); return
        deduct_balance(uid,price); pending_orders[uid]={"price":price,"name":name}
        markup=types.InlineKeyboardMarkup(row_width=2); markup.add(types.InlineKeyboardButton("✅ موافقة",callback_data=f"accept_{uid}"),types.InlineKeyboardButton("❌ رفض+استرجاع",callback_data=f"reject_refund_{uid}"))
        bot.send_message(ADMIN_ID,f"🔔 طلب متابعين\n👤 {uid}\n📦 {name} - ${price}",reply_markup=markup)
        bot.edit_message_text(f"✅ خصم ${price}\n📩 ابعت يوزرك",uid,call.message.message_id,reply_markup=main_menu(uid))
    elif call.data.startswith("stars_"):
        sid=call.data.replace("stars_","",1); price=STARS_GIFTS[sid]["price"]; name=STARS_GIFTS[sid]["name"]
        if get_balance(uid)<price: bot.answer_callback_query(call.id,f"تحتاج ${price}"); return
        deduct_balance(uid,price); pending_orders[uid]={"price":price,"name":name}
        markup=types.InlineKeyboardMarkup(row_width=2); markup.add(types.InlineKeyboardButton("✅ موافقة",callback_data=f"accept_{uid}"),types.InlineKeyboardButton("❌ رفض+استرجاع",callback_data=f"reject_refund_{uid}"))
        bot.send_message(ADMIN_ID,f"⭐ طلب نجوم\n👤 {uid}\n📦 {name} - ${price}",reply_markup=markup)
        bot.edit_message_text(f"✅ خصم ${price}\n📩 ابعت يوزرك",uid,call.message.message_id,reply_markup=main_menu(uid))
    elif call.data.startswith("accept_"):
        if not is_admin(uid): return
        if call.data.startswith("accept_recharge_"):
            cid=int(call.data.replace("accept_recharge_","")); admin_states[uid]={"step":"await_amount","target":cid}; bot.send_message(uid,f"💰 ادخل المبلغ للعميل {cid}:"); return
        cid=int(call.data.replace("accept_","")); bot.send_message(uid,f"✏️ اكتب الرد للعميل {cid}:"); bot.register_next_step_handler(call.message, lambda m: do_send(m,cid))
    elif call.data.startswith("reject_"):
        if not is_admin(uid): return
        if call.data.startswith("reject_recharge_"):
            cid=int(call.data.replace("reject_recharge_","")); bot.send_message(cid,"❌ تم رفض الشحن");
            if cid in pending_recharge: del pending_recharge[cid]; bot.send_message(uid,"تم الرفض"); return
        if "refund" in call.data:
            cid=int(call.data.replace("reject_refund_","")); info=pending_orders.get(cid,{})
            if info: add_balance(cid,info.get("price",0)); bot.send_message(cid,f"❌ تم الرفض واسترجاع ${info.get('price')}")
            if cid in pending_orders: del pending_orders[cid]; bot.send_message(uid,"تم الرفض والاسترجاع")

def do_send(message,cid):
    txt=message.text; info=pending_orders.get(cid,{}); bot.send_message(cid,f"✅ تم التسليم:\n📦 {info.get('name')}\n💰 ${info.get('price')}\n\n{txt}"); bot.send_message(message.chat.id,f"✅ تم الارسال {cid}");
    if cid in pending_orders: del pending_orders[cid]

@bot.message_handler(content_types=['photo','document','text'])
def handler(message):
    uid=message.chat.id
    if uid in admin_states:
        state=admin_states[uid]
        if state["step"]=="await_id":
            try:
                target=int(message.text); admin_states[uid]={"step":"await_amount","target":target}; bot.send_message(uid,f"✅ ايدي {target}\n\n💰 ادخل المبلغ:"); return
            except: bot.send_message(uid,"❌ ابعت ايدي صحيح ارقام فقط"); return
        elif state["step"]=="await_amount":
            try:
                amount=float(message.text); target=state["target"]; new_bal=add_balance(target,amount)
                bot.send_message(uid,f"✅ تم شحن ${amount} للعميل {target}\nرصيده ${round(new_bal,2)}",reply_markup=admin_main_menu())
                bot.send_message(target,f"✅ تم شحن رصيدك ${amount}$\n💰 رصيدك الحالي: ${round(new_bal,2)}")
                if target in pending_recharge: del pending_recharge[target]
                del admin_states[uid]; return
            except: bot.send_message(uid,"❌ ابعت مبلغ صحيح"); return
        elif state["step"]=="await_mod_id":
            try:
                mid=int(message.text); mods=get_mods()
                if mid not in mods: mods.append(mid); save_mods(mods)
                bot.send_message(uid,f"✅ تم اضافة المشرف {mid}",reply_markup=admin_main_menu()); del admin_states[uid]; return
            except: bot.send_message(uid,"❌ ابعت ايدي صحيح"); return
        elif state["step"]=="await_del_mod":
            try:
                mid=int(message.text); mods=get_mods()
                if mid in mods: mods.remove(mid); save_mods(mods); bot.send_message(uid,f"✅ تم حذف المشرف {mid}",reply_markup=admin_main_menu())
                else: bot.send_message(uid,"❌ المشرف مش موجود",reply_markup=admin_main_menu())
                del admin_states[uid]; return
            except: bot.send_message(uid,"❌ ابعت ايدي صحيح"); return

    if uid==ADMIN_ID or uid in get_mods():
        if broadcast_mode.get(uid):
            users=list(get_users().keys())+list(get_balances().keys()); users=list(set(users)); count=0
            bot.send_message(uid,f"📢 بدء الاذاعة لـ {len(users)}...")
            for u in users:
                try: bot.copy_message(int(u),uid,message.message_id); count+=1; time.sleep(0.05)
                except: pass
            bot.send_message(uid,f"✅ تمت الاذاعة لـ {count}",reply_markup=admin_main_menu()); del broadcast_mode[uid]; return

    if message.text and message.text.startswith("/addbalance"):
        if not is_admin(uid): return
        try:
            _, tid, amount = message.text.split(); new_bal=add_balance(int(tid),float(amount))
            bot.send_message(uid,f"✅ تم شحن ${amount} للعميل {tid}\nرصيده ${round(new_bal,2)}")
            bot.send_message(int(tid),f"✅ تم شحن رصيدك ${amount}$\n💰 رصيدك: ${round(new_bal,2)}")
            if int(tid) in pending_recharge: del pending_recharge[int(tid)]
        except Exception as e: bot.send_message(uid,f"خطأ: {e}"); return
    if message.text=="/cancel" and is_admin(uid):
        if uid in broadcast_mode: del broadcast_mode[uid]
        if uid in admin_states: del admin_states[uid]
        bot.send_message(uid,"تم الالغاء",reply_markup=admin_main_menu()); return

    if uid in pending_recharge:
        markup=types.InlineKeyboardMarkup(row_width=2); markup.add(types.InlineKeyboardButton("✅ قبول",callback_data=f"accept_recharge_{uid}"),types.InlineKeyboardButton("❌ رفض",callback_data=f"reject_recharge_{uid}"))
        try: bot.forward_message(ADMIN_ID,uid,message.message_id)
        except: pass
        bot.send_message(ADMIN_ID,f"💳 طلب شحن\n👤 {uid}\nطريقة: {pending_recharge[uid]['method']}",reply_markup=markup)
        bot.send_message(uid,"✅ استلمت، انتظار موافقة الادمن"); return
    if uid in pending_orders and not is_admin(uid):
        try: bot.forward_message(ADMIN_ID,uid,message.message_id)
        except: pass

print("PrimeX V26 - شغال صفين + اشعارات...")
bot.remove_webhook(); time.sleep(1)
while True:
    try: bot.infinity_polling(none_stop=True, timeout=20)
    except Exception as e: print(e); time.sleep(5)

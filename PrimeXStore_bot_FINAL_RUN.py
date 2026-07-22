import telebot
from telebot import types
import json, os, time

TOKEN = "8410968304:AAFSy73954G3O7HDY7S0EyPmH84dTfVA98M"
ADMIN_ID = 8933825471
BOT_USERNAME = "SocialSMSbot"
FORCE_CHANNELS = ["@SocialSMS1", "@SocialSMS2"]
NOTIFY_CHANNEL = "@SocialSMS2"
SUPPORT = "@SocialSMSSUPPORT"
REF_REWARD = 0.003
MIN_DEPOSIT = 0.1

bot = telebot.TeleBot(TOKEN, threaded=False)

balance_cache, users_cache = {}, {}
pending_orders = {}
pending_recharge = {}
broadcast_mode, admin_states = {}, {}
admins_list = [ADMIN_ID]
banned_users = []
referrals = {}

for f, var in [("balance.json", "balance_cache"), ("users.json", "users_cache"), ("admins.json", "admins_list"), ("banned.json", "banned_users"), ("referrals.json", "referrals")]:
    if os.path.exists(f):
        try: globals()[var] = json.load(open(f,"r",encoding="utf-8"))
        except: pass

def save_json(file, data):
    try: json.dump(data, open(file,"w",encoding="utf-8"))
    except: pass

def is_admin(uid): return uid in admins_list
def is_banned(uid): return uid in banned_users
def get_balance(uid): return float(balance_cache.get(str(uid),0))
def add_balance(uid,amt):
    balance_cache[str(uid)]=float(balance_cache.get(str(uid),0))+float(amt)
    save_json("balance.json", balance_cache)
    return balance_cache[str(uid)]
def deduct_balance(uid,amt):
    bal=float(balance_cache.get(str(uid),0))
    if bal<amt: return False
    balance_cache[str(uid)]=bal-amt
    save_json("balance.json", balance_cache)
    return True

def check_sub(uid):
    for ch in FORCE_CHANNELS:
        try:
            m=bot.get_chat_member(ch,uid)
            if m.status in ['left','kicked']: return False, []
        except: pass
    return True, []

# ===== الارقام الجديدة =====
FLAGS = {
    "myanmar":"🇲🇲 Myanmar",
    "syria":"🇸🇾 Syria",
    "morocco":"🇲🇦 Morocco",
    "usa":"🇺🇸 USA",
    "india":"🇮🇳 India",
    "ksa":"🇸🇦 KSA",
    "egypt":"🇪🇬 Egypt"
}

CLEAN = {
    "myanmar": 0.2, # ⭐20
    "syria": 0.8, # ⭐80
    "morocco": 0.6, # ⭐60
    "usa": 0.3, # ⭐30
    "india": 0.25, # ⭐25
    "ksa": 1.3, # ⭐130
    "egypt": 0.7 # ⭐70
}

SPAM = {
    "myanmar": 0.15, # ⭐15
    "usa": 0.2, # ⭐20
    "india": 0.2 # ⭐20
}

TELEGRAM_NUMS = {}

PAYMENTS = {
    "trc20":("🔸 USDT TRC20","TRHUB8kuMpdCoDzST6c4AJ4cJdk6tToz97"),
    "ton":("💠 GRAM TON","UQBdPqUEG7TkF2TYWDOEclSYPDec4-HGOsN5ss0Zcnby1mCL"),
    "faucetpay":("🚰 FaucetPay","@primexstore22"),
    "polygon":("💜 POLYGON","0xA7fE0a5Ae6Adcd5b47df238F836449b4d0866155"),
    "erc20":("💎 USDT ERC20","0x8D7dDE7719e9d6D3e5175CE170Fae00372715493"),
    "bep20":("💛 USDT BEP20","0xA7fE0a5Ae6Adcd5b47df238F836449b4d0866155"),
    "cwallet":("👛 C-Wallet","61824874"),
    "stars":("⭐ Telegram Stars","@SocialSMSSUPPORT")
}

def admin_menu():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("📊 Stats",callback_data="admin_stats"),types.InlineKeyboardButton("💰 Add Balance",callback_data="admin_add"))
    m.add(types.InlineKeyboardButton("🚫 Ban",callback_data="admin_ban"),types.InlineKeyboardButton("🔓 Unban",callback_data="admin_unban"))
    m.add(types.InlineKeyboardButton("📋 Banned",callback_data="admin_banned_list"),types.InlineKeyboardButton("📢 Broadcast",callback_data="admin_bc"))
    m.add(types.InlineKeyboardButton("👤 User Mode",callback_data="admin_user"))
    return m

def main_menu(uid):
    bal = get_balance(uid)
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton(f"💎 رصيدك: ${bal:.3f} 💎", callback_data="bal"))
    m.add(
        types.InlineKeyboardButton("👤💎 شراء حسابات", callback_data="buy_numbers_main"),
        types.InlineKeyboardButton("💰🚀 شحن رصيد", callback_data="recharge")
    )
    m.add(
        types.InlineKeyboardButton("🔗🎁 دعوة واربح", callback_data="invite"),
        types.InlineKeyboardButton("💬👑 الدعم الفني", url="https://t.me/SocialSMSSUPPORT")
    )
    m.add(types.InlineKeyboardButton("📢📣 قناتنا", url="https://t.me/SocialSMS1"))
    m.add(types.InlineKeyboardButton("🌟 تقييم البوت ⭐⭐⭐⭐⭐", callback_data="rate"))
    return m

def buy_numbers_main_menu():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton("✨💎 ارقام سليمة",callback_data="clean"),
        types.InlineKeyboardButton("🔥⚡ ارقام اسبام",callback_data="spam")
    )
    m.add(types.InlineKeyboardButton("🔙🏠 رجوع رئيسية",callback_data="back"))
    return m

def build_nums(data,prefix):
    m=types.InlineKeyboardMarkup(row_width=1)
    if not data:
        m.add(types.InlineKeyboardButton("⚠️ لا يوجد ارقام حاليا",callback_data="none"))
    else:
        for k,price in data.items():
            label=FLAGS.get(k,k)
            stars = int(price*100)
            m.add(types.InlineKeyboardButton(f"{label} • ${price} (⭐{stars})",callback_data=f"buy_{prefix}_{k}"))
    m.add(types.InlineKeyboardButton("🔙 رجوع",callback_data="buy_numbers_main"))
    return m

WELCOME = """╔══════════════════╗
   🔥👑 Social SMS 👑🔥
╚══════════════════╝

💎 مرحباً بك يا ملك 💎
💰 رصيدك: ${bal}
🆔 ايديك: {uid}

✨ اختر خدمتك 👇"""

@bot.message_handler(commands=['start'])
def start(msg):
    uid=msg.chat.id
    args=msg.text.split(); ref_id=None
    if len(args)>1:
        try: ref_id=int(args[1])
        except: pass
    if is_banned(uid): bot.send_message(uid,"🚫 Banned"); return
    is_new=str(uid) not in users_cache
    users_cache[str(uid)]={"name":msg.from_user.first_name,"username":msg.from_user.username}
    save_json("users.json", users_cache)

    if is_new:
        try:
            first_name = msg.from_user.first_name
            username = f"@{msg.from_user.username}" if msg.from_user.username else "No username"
            for admin_id in admins_list:
                try: bot.send_message(admin_id, f"👤 New User Joined!\n\nName: {first_name}\nUsername: {username}\n🆔 ID: {uid}\n📊 Total: {len(users_cache)}")
                except: pass
            try: bot.send_message(NOTIFY_CHANNEL, f"👤 NEW USER\n\nName: {first_name}\n{username}\n🆔 {uid}\n📊 Total: {len(users_cache)}")
            except: pass
            if ref_id and ref_id!=uid and str(ref_id) in users_cache:
                if str(uid) not in referrals.get(str(ref_id),[]):
                    add_balance(ref_id,REF_REWARD)
                    referrals.setdefault(str(ref_id),[]).append(str(uid))
                    save_json("referrals.json",referrals)
                    try: bot.send_message(ref_id,f"🎉 Earned ${REF_REWARD} from invite!")
                    except: pass
        except: pass

    if is_admin(uid): bot.send_message(uid,"👑 Admin Panel",reply_markup=admin_menu()); return
    ok,_=check_sub(uid)
    if not ok:
        m=types.InlineKeyboardMarkup(row_width=1)
        m.add(types.InlineKeyboardButton("📢 SocialSMS1",url="https://t.me/SocialSMS1"))
        m.add(types.InlineKeyboardButton("📢 SocialSMS2",url="https://t.me/SocialSMS2"))
        m.add(types.InlineKeyboardButton("✅ Joined",callback_data="check"))
        bot.send_message(uid,"⚠️ اشترك في القنوات الاول @SocialSMS1 @SocialSMS2",reply_markup=m); return
    bot.send_message(uid,WELCOME.format(bal=round(get_balance(uid),3),uid=uid),reply_markup=main_menu(uid))

@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    uid=call.message.chat.id; d=call.data
    if d=="check":
        ok,_=check_sub(uid)
        if not ok: bot.answer_callback_query(call.id,"❌ لم تشترك بعد!",show_alert=True); return
        bot.edit_message_text(WELCOME.format(bal=round(get_balance(uid),3),uid=uid),uid,call.message.message_id,reply_markup=main_menu(uid)); return
    if is_admin(uid) and d.startswith("admin_"):
        if d=="admin_stats":
            total=sum(float(v) for v in balance_cache.values())
            bot.edit_message_text(f"📊 Stats\n💰 Total: ${total:.3f}\n👥 Users: {len(users_cache)}",uid,call.message.message_id,reply_markup=admin_menu())
        elif d=="admin_add": admin_states[uid]="await_id"; bot.send_message(uid,"💰 Send User ID:")
        elif d=="admin_ban": admin_states[uid]="await_ban"; bot.send_message(uid,"🚫 Send ID to Ban:")
        elif d=="admin_unban": admin_states[uid]="await_unban"; bot.send_message(uid,"🔓 Send ID to Unban:")
        elif d=="admin_banned_list":
            txt="🚫 Banned:\n" + "\n".join([f"`{x}`" for x in banned_users]) if banned_users else "✅ No banned"
            bot.send_message(uid,txt,parse_mode="Markdown",reply_markup=admin_menu())
        elif d=="admin_bc": broadcast_mode[uid]=True; bot.send_message(uid,"📢 Send Broadcast\n/cancel to cancel")
        elif d=="admin_user": bot.send_message(uid,WELCOME.format(bal=round(get_balance(uid),3),uid=uid),reply_markup=main_menu(uid))
        elif d.startswith("accept_re_"):
            cid=int(d.replace("accept_re_","")); info=pending_recharge.get(cid)
            if not info: bot.send_message(uid,"Not found"); return
            try: amt=float(info.get("amount",0)); add_balance(cid,amt); bot.send_message(cid,f"✅ تم قبول شحنك ${amt}"); bot.send_message(uid,f"✅ Approved ${amt} to {cid}",reply_markup=admin_menu()); pending_recharge.pop(cid,None)
            except: bot.send_message(uid,"❌ Error")
            return
        elif d.startswith("reject_re_"):
            cid=int(d.replace("reject_re_","")); bot.send_message(cid,"❌ تم رفض الشحن"); pending_recharge.pop(cid,None); bot.send_message(uid,"Rejected"); return
        elif d.startswith("accept_num_"):
            target=int(d.split("_")[2]); admin_states[uid]=f"await_number_{target}"; bot.send_message(uid,f"📱 ابعت الرقم لـ {target}:"); return
        elif d.startswith("accept_code_"):
            target=int(d.split("_")[2]); admin_states[uid]=f"await_code_{target}"; bot.send_message(uid,f"🔑 ابعت الكود لـ {target}:"); return
        elif d.startswith("reject_"):
            cid=int(d.split("_")[-1]); info=pending_orders.get(cid)
            if info: add_balance(cid,info['price']); bot.send_message(cid,f"❌ تم الرفض - رجعلك ${info['price']}")
            pending_orders.pop(cid,None); bot.send_message(uid,"Rejected & Refunded"); return
        return

    if d=="bal": bot.answer_callback_query(call.id,f"رصيدك: ${round(get_balance(uid),3)}"); return
    if d=="back": bot.edit_message_text(WELCOME.format(bal=round(get_balance(uid),3),uid=uid),uid,call.message.message_id,reply_markup=main_menu(uid)); return
    if d=="buy_numbers_main": bot.edit_message_text("📱 اختر النوع:",uid,call.message.message_id,reply_markup=buy_numbers_main_menu()); return
    if d=="clean": bot.edit_message_text("✨ ارقام سليمة:",uid,call.message.message_id,reply_markup=build_nums(CLEAN,"clean")); return
    if d=="spam": bot.edit_message_text("🔥 ارقام اسبام:",uid,call.message.message_id,reply_markup=build_nums(SPAM,"spam")); return
    if d=="invite":
        count=len(referrals.get(str(uid),[])); link=f"https://t.me/{BOT_USERNAME}?start={uid}"
        bot.edit_message_text(f"🔗 رابط الدعوة:\n`{link}`\n\n👥 {count} - ربحت ${count*REF_REWARD:.3f}",uid,call.message.message_id,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع",callback_data="back"))); return
    if d=="recharge":
        m=types.InlineKeyboardMarkup(row_width=2)
        for k,(name,addr) in PAYMENTS.items(): m.add(types.InlineKeyboardButton(f"{name}",callback_data=f"pay_{k}"))
        m.add(types.InlineKeyboardButton("🔙 رجوع",callback_data="back"))
        bot.edit_message_text(f"💰 الشحن - اقل مبلغ ${MIN_DEPOSIT}\nرصيدك: ${round(get_balance(uid),3)}\nاختر طريقة:",uid,call.message.message_id,reply_markup=m); return
    if d.startswith("pay_"):
        k=d.replace("pay_",""); name,addr=PAYMENTS[k]
        pending_recharge[uid]={"method":k,"name":name,"address":addr,"step":"waiting_screenshot"}
        txt=f"{name}\n\nالعنوان:\n`{addr}`\n\nاقل مبلغ: ${MIN_DEPOSIT}\n\nبعد التحويل ابعت سكرين شوت 👇"
        bot.edit_message_text(txt,uid,call.message.message_id,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع",callback_data="recharge")))
        return
    if d.startswith("buy_"):
        try:
            parts=d.split("_")
            mp={"clean":CLEAN,"spam":SPAM}; price=mp[parts[1]][parts[2]]; service_type=f"{parts[1]} {parts[2]}"
            if get_balance(uid) < price:
                m=types.InlineKeyboardMarkup(row_width=1)
                m.add(types.InlineKeyboardButton("💰 اشحن الان",callback_data="recharge"))
                m.add(types.InlineKeyboardButton("🔙 رجوع",callback_data="buy_numbers_main"))
                bot.edit_message_text(f"❌ رصيدك لا يكفي!\nرصيدك: ${round(get_balance(uid),3)}\nمطلوب: ${price}\nاشحن الاول - اقل مبلغ ${MIN_DEPOSIT}",uid,call.message.message_id,reply_markup=m); return
            deduct_balance(uid,price)
            pending_orders[uid]={"price":price,"service_type":service_type,"status":"waiting_number"}
            m=types.InlineKeyboardMarkup(row_width=2)
            m.add(types.InlineKeyboardButton("✅ ارسال رقم",callback_data=f"accept_num_{uid}"),types.InlineKeyboardButton("❌ رفض",callback_data=f"reject_{uid}"))
            for admin_id in admins_list:
                try: bot.send_message(admin_id,f"🔔 طلب جديد {uid} {service_type} ${price}",reply_markup=m)
                except: pass
            bot.edit_message_text(f"✅ تم الطلب: {service_type} ${price} في انتظار الادمن...",uid,call.message.message_id,reply_markup=main_menu(uid))
        except Exception as e: print(e)

@bot.message_handler(content_types=['photo','document','text'])
def all_msg(msg):
    uid=msg.chat.id; txt=msg.text or ""
    if is_admin(uid) and uid in admin_states:
        state=admin_states[uid]
        if state.startswith("await_amount_"):
            try: target=int(state.split("_")[-1]); amt=float(txt); add_balance(target,amt); bot.send_message(uid,f"✅ Added ${amt} to {target}",reply_markup=admin_menu()); bot.send_message(target,f"✅ تم شحن ${amt}"); pending_recharge.pop(target,None); del admin_states[uid]
            except: bot.send_message(uid,"❌ مبلغ غلط"); return
        if state.startswith("await_number_"):
            target=int(state.split("_")[-1]); pending_orders[target]["number"]=txt; pending_orders[target]["status"]="waiting_code"
            bot.send_message(target,f"📱 رقمك:\n`{txt}`\nفي انتظار الكود...",parse_mode="Markdown")
            m=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔑 ارسال الكود",callback_data=f"accept_code_{target}"))
            bot.send_message(uid,f"✅ الرقم اتبعت لـ {target} ابعت الكود دلوقتي:",reply_markup=m); admin_states[uid]=f"await_code_{target}"; return
        if state.startswith("await_code_"):
            target=int(state.split("_")[-1]); number=pending_orders.get(target,{}).get("number","N/A"); service=pending_orders.get(target,{}).get("service_type","N/A"); price=pending_orders.get(target,{}).get("price",0)
            bot.send_message(target,f"🔑 كودك:\n`{txt}`\nالرقم: {number}",parse_mode="Markdown",reply_markup=main_menu(target))
            bot.send_message(uid,f"✅ الكود اتبعت لـ {target}",reply_markup=admin_menu())
            try: bot.send_message(NOTIFY_CHANNEL,f"✅ DELIVERED\n🆔 {target}\n📱 {number}\n🔑 {txt}\n📦 {service} - ${price}")
            except: pass
            pending_orders.pop(target,None); del admin_states[uid]; return
        if state=="await_id":
            try: target=int(txt); admin_states[uid]=f"await_amount_{target}"; bot.send_message(uid,f"المبلغ لـ {target}:")
            except: bot.send_message(uid,"❌ ID غلط"); return
        if state=="await_ban":
            try: target=int(txt); banned_users.append(target); save_json("banned.json",banned_users); bot.send_message(uid,f"✅ Banned {target}",reply_markup=admin_menu()); del admin_states[uid]
            except: bot.send_message(uid,"❌ ID غلط"); return
        if state=="await_unban":
            try: target=int(txt); banned_users.remove(target); save_json("banned.json",banned_users); bot.send_message(uid,f"✅ Unbanned {target}",reply_markup=admin_menu()); del admin_states[uid]
            except: bot.send_message(uid,"❌ ID غلط"); return
    if is_admin(uid) and uid in broadcast_mode:
        if txt=="/cancel": del broadcast_mode[uid]; bot.send_message(uid,"Cancelled",reply_markup=admin_menu()); return
        for u in list(users_cache.keys()):
            try: bot.copy_message(int(u),uid,msg.message_id)
            except: pass
        bot.send_message(uid,f"Broadcast done",reply_markup=admin_menu()); del broadcast_mode[uid]; return

    if uid in pending_recharge:
        info=pending_recharge[uid]
        if info.get("step")=="waiting_screenshot":
            if msg.content_type in ['photo','document']:
                pending_recharge[uid]["screenshot_msg_id"]=msg.message_id
                pending_recharge[uid]["step"]="waiting_amount"
                bot.send_message(uid,"✅ تم استلام السكرين!\n\n💰 ابعت المبلغ اللي شحنته:\nمثال: 1.5")
                return
            else: bot.send_message(uid,"⚠️ ابعت سكرين شوت الاول 👆"); return
        if info.get("step")=="waiting_amount":
            try:
                amt=float(txt)
                if amt < MIN_DEPOSIT: bot.send_message(uid,f"❌ اقل مبلغ ${MIN_DEPOSIT}"); return
                pending_recharge[uid]["amount"]=amt
                pending_recharge[uid]["step"]="pending_admin"
                m=types.InlineKeyboardMarkup(row_width=2)
                m.add(types.InlineKeyboardButton("✅ قبول",callback_data=f"accept_re_{uid}"),types.InlineKeyboardButton("❌ رفض",callback_data=f"reject_re_{uid}"))
                for admin_id in admins_list:
                    try:
                        try: bot.forward_message(admin_id,uid,info["screenshot_msg_id"])
                        except: pass
                        bot.send_message(admin_id,f"💰 شحن جديد\n🆔 {uid}\n💳 {info['name']}\n💰 ${amt}\n{info['address']}",reply_markup=m)
                    except: pass
                bot.send_message(uid,f"✅ طلبك اتبعت! {info['name']} ${amt} في انتظار الموافقة ⏳",reply_markup=main_menu(uid))
            except: bot.send_message(uid,"❌ مبلغ غلط! مثال: 0.5")
            return

print("V70 FINAL - Ready")
bot.delete_webhook(drop_pending_updates=True)
time.sleep(1)
bot.infinity_polling(none_stop=True, timeout=20, long_polling_timeout=20, skip_pending=True)

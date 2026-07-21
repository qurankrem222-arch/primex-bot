import telebot
from telebot import types
import json, os, time

TOKEN = "8315190785:AAFNCBRiF1eimUpePthW2Om1s2F2eC_f8kg"
ADMIN_ID = 8933825471
BOT_USERNAME = "PrimeXStore00bot"
FORCE_CHANNELS = ["@PrimeXStore0", "@PrimeXStore00", "@kingfreebots"]
FACEBOOK_PAGE = "https://www.facebook.com/profile.php?id=61592294575700"

bot = telebot.TeleBot(TOKEN, threaded=False)

balance_cache, users_cache, sub_cache = {}, {}, {}
pending_orders, pending_recharge = {}, {}
broadcast_mode, admin_states, last_added = {}, {}, {}
admins_list = [ADMIN_ID]
banned_users = []

if os.path.exists("balance.json"):
    try: balance_cache = json.load(open("balance.json","r",encoding="utf-8"))
    except: pass
if os.path.exists("users.json"):
    try: users_cache = json.load(open("users.json","r",encoding="utf-8"))
    except: pass
if os.path.exists("admins.json"):
    try: admins_list = json.load(open("admins.json","r",encoding="utf-8"))
    except: admins_list = [ADMIN_ID]
if os.path.exists("banned.json"):
    try: banned_users = json.load(open("banned.json","r",encoding="utf-8"))
    except: banned_users = []

def save_bal(): json.dump(balance_cache, open("balance.json","w",encoding="utf-8"))
def save_users(): json.dump(users_cache, open("users.json","w",encoding="utf-8"))
def save_admins(): json.dump(admins_list, open("admins.json","w",encoding="utf-8"))
def save_banned(): json.dump(banned_users, open("banned.json","w",encoding="utf-8"))

def is_admin(uid): return uid in admins_list
def is_banned(uid): return uid in banned_users
def get_balance(uid): return float(balance_cache.get(str(uid),0))

def add_balance(uid,amt):
    k=f"{uid}_{amt}_{int(time.time()//3)}"
    if k in last_added: return float(balance_cache.get(str(uid),0))
    last_added[k]=True
    balance_cache[str(uid)]=float(balance_cache.get(str(uid),0))+float(amt)
    save_bal()
    return balance_cache[str(uid)]

def deduct_balance(uid,amt):
    bal=float(balance_cache.get(str(uid),0))
    if bal<amt: return False
    balance_cache[str(uid)]=bal-amt
    save_bal()
    return True

def check_sub(uid):
    if uid in sub_cache:
        t,ok = sub_cache[uid]
        if time.time()-t < 300: return ok,[]
    nj=[]
    for ch in FORCE_CHANNELS:
        try:
            m=bot.get_chat_member(ch,uid)
            if m.status in ['left','kicked']: nj.append(ch)
        except: pass
    ok=len(nj)==0
    sub_cache[uid]=(time.time(),ok)
    return ok,nj

FLAGS = {"india":"🇮🇳 India","egypt":"🇪🇬 Egypt","vietnam":"🇻🇳 Vietnam","ksa":"🇸🇦 KSA","pakistan":"🇵🇰 Pakistan","morocco":"🇲🇦 Morocco","myanmar":"🇲🇲 Myanmar","kenya":"🇰🇪 Kenya","indonesia":"🇮🇩 Indonesia","nigeria":"🇳🇬 Nigeria","usa":"🇺🇸 USA","ghana":"🇬🇭 Ghana","sudan":"🇸🇩 Sudan","germany":"🇩🇪 Germany","mozambique":"🇲🇿 Mozambique","random":"🌍 Random","rare":"💎 Rare"}
CLEAN = {"india":0.3,"egypt":0.5,"vietnam":0.9,"ksa":1.5,"pakistan":0.7,"morocco":0.6,"myanmar":0.3,"kenya":0.5,"indonesia":0.6,"nigeria":0.5}
SPAM = {"india":0.2,"random":0.3,"rare":0.45,"usa":0.25,"myanmar":0.2}
FOLLOWER_COUNTS = {"10":0.09,"20":0.18,"50":0.45,"100":0.9,"200":1.8,"300":2.7,"400":3.6,"500":4.5}
STARS = {"15":0.18,"25":0.29,"50":0.57,"100":1.15}
PAYMENTS = {"cwallet":("C-Wallet","61824874"),"trc20":("TRC20","TRHUB8kuMpdCoDzST6c4AJ4cJdk6tToz97")}

def admin_menu():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("Stats",callback_data="admin_stats"),types.InlineKeyboardButton("Add Bal",callback_data="admin_add"))
    m.add(types.InlineKeyboardButton("Add Mod 👑",callback_data="admin_addmod"),types.InlineKeyboardButton("Ban User 🚫",callback_data="admin_ban"))
    m.add(types.InlineKeyboardButton("Unban 🔓",callback_data="admin_unban"),types.InlineKeyboardButton("Mods List",callback_data="admin_mods"))
    m.add(types.InlineKeyboardButton("Broadcast",callback_data="admin_bc"),types.InlineKeyboardButton("User Mode",callback_data="admin_user"))
    return m

def main_menu(uid):
    bal=get_balance(uid)
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton(f"${bal:.2f}",callback_data="bal"),types.InlineKeyboardButton("Numbers 📱",callback_data="nums"))
    m.add(types.InlineKeyboardButton("Followers 👥",callback_data="followers_main"),types.InlineKeyboardButton("Stars ⭐",callback_data="stars"))
    m.add(types.InlineKeyboardButton("Recharge 💳",callback_data="recharge"),types.InlineKeyboardButton("Invite 🔗",callback_data="invite"))
    return m

@bot.message_handler(commands=['start'])
def start(msg):
    uid=msg.chat.id
    if is_banned(uid):
        bot.send_message(uid,"🚫 You are banned")
        return
    if str(uid) not in users_cache and uid!= ADMIN_ID:
        for admin_id in admins_list:
            try: bot.send_message(admin_id, f"🔔 New user: {msg.from_user.first_name}\nID: {uid}\n@{msg.from_user.username}\nTotal: {len(users_cache)+1}")
            except: pass
    users_cache[str(uid)]={"name":msg.from_user.first_name,"username":msg.from_user.username}
    save_users()
    if is_admin(uid):
        bot.send_message(uid,"Admin Panel 👑\nLight Version V49",reply_markup=admin_menu())
        return
    ok,nj=check_sub(uid)
    if not ok:
        m=types.InlineKeyboardMarkup()
        for ch in nj: m.add(types.InlineKeyboardButton(f"{ch}",url=f"https://t.me/{ch.replace('@','')}"))
        m.add(types.InlineKeyboardButton("Facebook",url=FACEBOOK_PAGE))
        m.add(types.InlineKeyboardButton("Done ✅",callback_data="check"))
        bot.send_message(uid,"Please subscribe first 👇",reply_markup=m)
        return
    bot.send_message(uid,f"Welcome King 👑\nBalance: ${round(get_balance(uid),2)}\nID: {uid}",reply_markup=main_menu(uid))

@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    uid=call.message.chat.id
    d=call.data
    if d=="check":
        sub_cache.pop(uid,None)
        ok,nj=check_sub(uid)
        if not ok:
            bot.answer_callback_query(call.id,"Not subscribed yet!")
            return
        bot.edit_message_text(f"Welcome King 👑\nBalance: ${round(get_balance(uid),2)}\nID: {uid}",uid,call.message.message_id,reply_markup=main_menu(uid))
        return
    if is_admin(uid):
        if d=="admin_stats":
            total=sum(float(v) for v in balance_cache.values())
            bot.edit_message_text(f"Stats:\nTotal: ${round(total,2)}\nUsers: {len(users_cache)}\nMods: {len(admins_list)}\nBanned: {len(banned_users)}",uid,call.message.message_id,reply_markup=admin_menu())
        elif d=="admin_add":
            admin_states[uid]="await_id"
            bot.send_message(uid,"Send user ID:")
        elif d=="admin_addmod":
            if uid!= ADMIN_ID:
                bot.answer_callback_query(call.id,"Only main admin!")
                return
            admin_states[uid]="await_mod"
            bot.send_message(uid,"Send mod ID:")
        elif d=="admin_ban":
            admin_states[uid]="await_ban"
            bot.send_message(uid,"Send ID to ban:")
        elif d=="admin_unban":
            admin_states[uid]="await_unban"
            bot.send_message(uid,"Send ID to unban:")
        elif d=="admin_mods":
            txt="Mods:\n"
            for mod in admins_list: txt+=f"{mod} {'(main)' if mod==ADMIN_ID else ''}\n"
            bot.send_message(uid,txt)
        elif d=="admin_bc":
            broadcast_mode[uid]=True
            bot.send_message(uid,"Send broadcast msg /cancel to abort")
        elif d=="admin_user":
            bot.send_message(uid,f"User mode\nBalance: ${round(get_balance(uid),2)}",reply_markup=main_menu(uid))
        return
    if d=="bal":
        bot.answer_callback_query(call.id,f"${round(get_balance(uid),2)}")
    elif d=="invite":
        link=f"https://t.me/{BOT_USERNAME}?start={uid}"
        bot.send_message(uid,f"Your invite link:\n{link}")
    elif d=="nums":
        m=types.InlineKeyboardMarkup(row_width=1)
        for k,price in CLEAN.items(): m.add(types.InlineKeyboardButton(f"{FLAGS.get(k,k)} - ${price}",callback_data=f"buy_clean_{k}"))
        m.add(types.InlineKeyboardButton("Back",callback_data="back"))
        bot.edit_message_text("Numbers:",uid,call.message.message_id,reply_markup=m)
    elif d=="followers_main":
        m=types.InlineKeyboardMarkup(row_width=2)
        for count,price in FOLLOWER_COUNTS.items(): m.add(types.InlineKeyboardButton(f"{count} - ${price}",callback_data=f"buy_followers_tiktok_{count}"))
        m.add(types.InlineKeyboardButton("Back",callback_data="back"))
        bot.edit_message_text("Followers:",uid,call.message.message_id,reply_markup=m)
    elif d=="stars":
        m=types.InlineKeyboardMarkup(row_width=2)
        for k,price in STARS.items(): m.add(types.InlineKeyboardButton(f"{k} - ${price}",callback_data=f"buy_stars_{k}"))
        m.add(types.InlineKeyboardButton("Back",callback_data="back"))
        bot.edit_message_text("Stars:",uid,call.message.message_id,reply_markup=m)
    elif d=="back":
        bot.edit_message_text(f"Welcome King 👑\nBalance: ${round(get_balance(uid),2)}\nID: {uid}",uid,call.message.message_id,reply_markup=main_menu(uid))

@bot.message_handler(content_types=['text'])
def text_handler(msg):
    uid=msg.chat.id
    txt=msg.text
    if is_admin(uid) and uid in admin_states:
        state=admin_states[uid]
        if state=="await_mod":
            try:
                target=int(txt)
                if target not in admins_list:
                    admins_list.append(target)
                    save_admins()
                    bot.send_message(uid,f"Added mod {target}",reply_markup=admin_menu())
                del admin_states[uid]
            except: bot.send_message(uid,"Wrong ID")
            return
        if state=="await_ban":
            try:
                target=int(txt)
                if target!=ADMIN_ID and target not in banned_users:
                    banned_users.append(target)
                    save_banned()
                    bot.send_message(uid,f"Banned {target}",reply_markup=admin_menu())
                del admin_states[uid]
            except: bot.send_message(uid,"Wrong ID")
            return
        if state=="await_unban":
            try:
                target=int(txt)
                if target in banned_users:
                    banned_users.remove(target)
                    save_banned()
                    bot.send_message(uid,f"Unbanned {target}",reply_markup=admin_menu())
                del admin_states[uid]
            except: bot.send_message(uid,"Wrong ID")
            return
        if state=="await_id":
            try:
                target=int(txt)
                admin_states[uid]=f"await_amount_{target}"
                bot.send_message(uid,f"ID {target} - send amount:")
            except: bot.send_message(uid,"Wrong ID")
            return
        if state.startswith("await_amount_"):
            try:
                target=int(state.split("_")[-1])
                amt=float(txt)
                add_balance(target,amt)
                bot.send_message(uid,f"Added ${amt} to {target}",reply_markup=admin_menu())
                del admin_states[uid]
            except: bot.send_message(uid,"Wrong amount")
            return

print("V49 LIGHT running")
bot.delete_webhook(drop_pending_updates=True)
bot.infinity_polling()

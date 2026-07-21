import telebot
from telebot import types
import json, os, time

TOKEN = "8315190785:AAFNCBRiF1eimUpePthW2Om1s2F2eC_f8kg"
ADMIN_ID = 8933825471
FORCE_CHANNELS = ["@PrimeXStore0", "@PrimeXStore00", "@kingfreebots"]
SUPPORT = "@PrimeXStore22"
FACEBOOK_PAGE = "https://www.facebook.com/profile.php?id=61592294575700"

bot = telebot.TeleBot(TOKEN, threaded=False)

balance_cache = {}
users_cache = {}
sub_cache = {}
pending_orders = {}
pending_recharge = {}
broadcast_mode = {}
admin_states = {}
last_added = {}

if os.path.exists("balance.json"):
    try: balance_cache = json.load(open("balance.json","r",encoding="utf-8"))
    except: balance_cache = {}
if os.path.exists("users.json"):
    try: users_cache = json.load(open("users.json","r",encoding="utf-8"))
    except: users_cache = {}

def save_bal():
    try: json.dump(balance_cache, open("balance.json","w",encoding="utf-8"))
    except: pass
def save_users():
    try: json.dump(users_cache, open("users.json","w",encoding="utf-8"))
    except: pass
def get_balance(uid): return float(balance_cache.get(str(uid),0))

def add_balance(uid,amt):
    key = f"{uid}_{amt}_{int(time.time()//3)}"
    if key in last_added:
        return float(balance_cache.get(str(uid),0))
    last_added[key]=True
    balance_cache[str(uid)] = float(balance_cache.get(str(uid),0))+float(amt)
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

CLEAN = {"india":0.3,"egypt":0.5,"vietnam":0.9,"ksa":1.5,"pakistan":0.7,"morocco":0.6,"myanmar":0.3,"kenya":0.5,"indonesia":0.6,"nigeria":0.5}
SPAM = {"india":0.2,"random":0.3,"rare":0.45,"usa":0.25,"myanmar":0.2}
WHATSAPP = {"indonesia":0.25}
TIKTOK = {"germany":0.2,"sudan":0.15}
FACEBOOK = {"indonesia":0.1,"sudan":0.1,"ghana":0.15}
INSTA = {"ghana":0.15}
TINDER = {"indonesia":0.07,"mozambique":0.09}
FOLLOWER_COUNTS = {"10":0.09,"20":0.18,"50":0.45,"100":0.9,"200":1.8,"300":2.7,"400":3.6,"500":4.5}
ACCOUNTS = {
    "tiktok_1300": {"name": "TikTok 1300 Followers", "price": 1.5},
    "tiktok_2200": {"name": "TikTok 2200 Followers", "price": 2.0},
}
STARS = {"15":0.18,"25":0.29,"50":0.57,"100":1.15}
PAYMENTS = {
    "cwallet": ("C-Wallet","61824874"),
    "trc20": ("USDT TRC20","TRHUB8kuMpdCoDzST6c4AJ4cJdk6tToz97"),
    "bep20": ("USDT BEP20","0xA7fE0a5Ae6Adcd5b47df238F836449b4d0866155"),
    "erc20": ("USDT ERC20","0x8D7dDE7719e9d6D3e5175CE170Fae00372715493"),
    "polygon": ("POLYGON","0xA7fE0a5Ae6Adcd5b47df238F836449b4d0866155"),
    "faucetpay": ("FaucetPay","@primexstore22"),
    "gram": ("GRAM TON","UQBdPqUEG7TkF2TYWDOEclSYPDec4-HGOsN5ss0Zcnby1mCL"),
}

def admin_menu():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("احصائيات",callback_data="admin_stats"),types.InlineKeyboardButton("اضافة رصيد",callback_data="admin_add"))
    m.add(types.InlineKeyboardButton("اذاعة",callback_data="admin_bc"),types.InlineKeyboardButton("وضع العميل",callback_data="admin_user"))
    return m

def main_menu(uid):
    bal=get_balance(uid)
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton(f"💰 ${round(bal,2)}",callback_data="bal"),types.InlineKeyboardButton("Numbers",callback_data="nums"))
    m.add(types.InlineKeyboardButton("Followers",callback_data="followers_main"),types.InlineKeyboardButton("Accounts",callback_data="accounts_main"))
    m.add(types.InlineKeyboardButton("Stars",callback_data="stars"),types.InlineKeyboardButton("Recharge",callback_data="recharge"))
    m.add(types.InlineKeyboardButton("Facebook 👍 Like & Follow",url=FACEBOOK_PAGE))
    m.add(types.InlineKeyboardButton(f"{SUPPORT}",url=f"https://t.me/{SUPPORT.replace('@','')}"))
    return m

def nums_menu():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("Clean",callback_data="clean"),types.InlineKeyboardButton("Spam",callback_data="spam"))
    m.add(types.InlineKeyboardButton("WhatsApp",callback_data="wa"),types.InlineKeyboardButton("TikTok",callback_data="tiktok"))
    m.add(types.InlineKeyboardButton("Facebook",callback_data="fb"),types.InlineKeyboardButton("Instagram",callback_data="insta"))
    m.add(types.InlineKeyboardButton("Tinder",callback_data="tinder"))
    m.add(types.InlineKeyboardButton("Back",callback_data="back"))
    return m

def build_nums(data, prefix):
    m=types.InlineKeyboardMarkup(row_width=2)
    for k,price in data.items():
        m.add(types.InlineKeyboardButton(f"{k} ${price}",callback_data=f"buy_{prefix}_{k}"))
    m.add(types.InlineKeyboardButton("Back",callback_data="nums"))
    return m

def followers_platforms_menu():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("TikTok",callback_data="fp_tiktok"),types.InlineKeyboardButton("Instagram",callback_data="fp_instagram"))
    m.add(types.InlineKeyboardButton("Facebook",callback_data="fp_facebook"),types.InlineKeyboardButton("YouTube",callback_data="fp_youtube"))
    m.add(types.InlineKeyboardButton("Telegram",callback_data="fp_telegram"))
    m.add(types.InlineKeyboardButton("Back",callback_data="back"))
    return m

def followers_counts_menu(platform):
    m=types.InlineKeyboardMarkup(row_width=2)
    for count,price in FOLLOWER_COUNTS.items():
        m.add(types.InlineKeyboardButton(f"{count} = ${price}",callback_data=f"buy_followers_{platform}_{count}"))
    m.add(types.InlineKeyboardButton("Back",callback_data="followers_main"))
    return m

def accounts_menu():
    m=types.InlineKeyboardMarkup(row_width=1)
    for k,v in ACCOUNTS.items():
        m.add(types.InlineKeyboardButton(f"{v['name']} - ${v['price']}",callback_data=f"buy_accounts_{k}"))
    m.add(types.InlineKeyboardButton("Back",callback_data="back"))
    return m

@bot.message_handler(commands=['start'])
def start(msg):
    uid=msg.chat.id
    users_cache[str(uid)]={"name":msg.chat.first_name,"username":msg.chat.username}
    save_users()
    if uid==ADMIN_ID:
        bot.send_message(uid,"Admin - Facebook 61592294575700 Added ✅",reply_markup=admin_menu())
        return
    ok,nj=check_sub(uid)
    if not ok:
        m=types.InlineKeyboardMarkup(row_width=1)
        for ch in nj: m.add(types.InlineKeyboardButton(f"{ch}",url=f"https://t.me/{ch.replace('@','')}"))
        m.add(types.InlineKeyboardButton("Facebook Page 👍 Like",url=FACEBOOK_PAGE))
        m.add(types.InlineKeyboardButton("Done ✅",callback_data="check"))
        bot.send_message(uid,f"Welcome to PrimeX Store\n\n📢 Subscribe to channels\n👍 Like Facebook Page:\n{FACEBOOK_PAGE}\n\nThen press Done",reply_markup=m)
        return
    bot.send_message(uid,f"PrimeX Store\nBalance: ${round(get_balance(uid),2)}\n\nFollow us: {FACEBOOK_PAGE}",reply_markup=main_menu(uid))

@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    uid=call.message.chat.id
    d=call.data
    if d=="check":
        sub_cache.pop(uid,None)
        ok,nj=check_sub(uid)
        if not ok:
            bot.answer_callback_query(call.id,"Please subscribe all!")
            return
        bot.edit_message_text(f"Balance: ${round(get_balance(uid),2)}\n\nFacebook: {FACEBOOK_PAGE}",uid,call.message.message_id,reply_markup=main_menu(uid))
        return
    if uid==ADMIN_ID:
        if d=="admin_stats":
            total=sum(float(v) for v in balance_cache.values())
            bot.edit_message_text(f"Stats\nTotal: ${round(total,2)}\nUsers: {len(users_cache)}",uid,call.message.message_id,reply_markup=admin_menu())
        elif d=="admin_add":
            admin_states[uid]="await_id"
            bot.send_message(uid,"Send user ID:")
        elif d=="admin_bc":
            broadcast_mode[uid]=True
            bot.send_message(uid,"Send broadcast:\n/cancel")
        elif d=="admin_user":
            bot.send_message(uid,"User mode:",reply_markup=main_menu(uid))
        elif d.startswith("accept_"):
            if d.startswith("accept_re_"):
                cid=int(d.replace("accept_re_",""))
                admin_states[uid]=f"await_amount_{cid}"
                bot.send_message(uid,f"Amount for {cid}:")
                return
            cid=int(d.replace("accept_",""))
            admin_states[uid]=f"await_reply_{cid}"
            bot.send_message(uid,f"Reply for {cid}:")
        elif d.startswith("reject_"):
            if d.startswith("reject_re_"):
                cid=int(d.replace("reject_re_",""))
                bot.send_message(cid,"Recharge rejected")
                pending_recharge.pop(cid,None)
                bot.send_message(uid,"Rejected")
                return
            cid=int(d.replace("reject_",""))
            info=pending_orders.get(cid)
            if info:
                add_balance(cid,info['price'])
                bot.send_message(cid,f"Rejected & refunded ${info['price']}")
            pending_orders.pop(cid,None)
            bot.send_message(uid,"Rejected & refunded")
        return

    if d=="bal": bot.answer_callback_query(call.id,f"${round(get_balance(uid),2)}"); return
    if d=="back":
        bot.edit_message_text(f"Balance: ${round(get_balance(uid),2)}",uid,call.message.message_id,reply_markup=main_menu(uid))
        return
    if d=="nums": bot.edit_message_text("Choose category:",uid,call.message.message_id,reply_markup=nums_menu()); return
    if d=="clean": bot.edit_message_text("Clean:",uid,call.message.message_id,reply_markup=build_nums(CLEAN,"clean")); return
    if d=="spam": bot.edit_message_text("Spam:",uid,call.message.message_id,reply_markup=build_nums(SPAM,"spam")); return
    if d=="wa": bot.edit_message_text("WhatsApp:",uid,call.message.message_id,reply_markup=build_nums(WHATSAPP,"wa")); return
    if d=="tiktok": bot.edit_message_text("TikTok Numbers:",uid,call.message.message_id,reply_markup=build_nums(TIKTOK,"tiktok")); return
    if d=="fb": bot.edit_message_text("Facebook Numbers:",uid,call.message.message_id,reply_markup=build_nums(FACEBOOK,"fb")); return
    if d=="insta": bot.edit_message_text("Instagram:",uid,call.message.message_id,reply_markup=build_nums(INSTA,"insta")); return
    if d=="tinder": bot.edit_message_text("Tinder:",uid,call.message.message_id,reply_markup=build_nums(TINDER,"tinder")); return
    if d=="followers_main": bot.edit_message_text("Choose Platform:\n10 Followers = $0.09",uid,call.message.message_id,reply_markup=followers_platforms_menu()); return
    if d.startswith("fp_"):
        platform=d.replace("fp_","")
        bot.edit_message_text(f"{platform} - Choose count:",uid,call.message.message_id,reply_markup=followers_counts_menu(platform))
        return
    if d=="accounts_main": bot.edit_message_text("Accounts:\nTikTok 1300 = $1.5\nTikTok 2200 = $2",uid,call.message.message_id,reply_markup=accounts_menu()); return
    if d=="stars":
        m=types.InlineKeyboardMarkup(row_width=2)
        for k,price in STARS.items(): m.add(types.InlineKeyboardButton(f"{k} Stars ${price}",callback_data=f"buy_stars_{k}"))
        m.add(types.InlineKeyboardButton("Back",callback_data="back"))
        bot.edit_message_text("Stars:",uid,call.message.message_id,reply_markup=m); return
    if d=="recharge":
        m=types.InlineKeyboardMarkup(row_width=2)
        for k,(name,addr) in PAYMENTS.items(): m.add(types.InlineKeyboardButton(name,callback_data=f"pay_{k}"))
        m.add(types.InlineKeyboardButton("Back",callback_data="back"))
        bot.edit_message_text(f"Recharge - ${round(get_balance(uid),2)}",uid,call.message.message_id,reply_markup=m); return
    if d.startswith("pay_"):
        k=d.replace("pay_","")
        name,addr=PAYMENTS[k]
        pending_recharge[uid]=k
        bot.edit_message_text(f"{name}\n\n`{addr}`\n\nSend screenshot",uid,call.message.message_id,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Back",callback_data="recharge"))); return
    if d.startswith("buy_"):
        try:
            parts=d.split("_")
            if parts[1]=="followers":
                _,_,platform,count = parts
                price=FOLLOWER_COUNTS[count]
                name=f"{platform} {count} Followers"
            elif parts[1]=="accounts":
                key="_".join(parts[2:])
                v=ACCOUNTS[key]
                price=v['price']
                name=v['name']
            elif parts[1]=="stars":
                count=parts[2]
                price=STARS[count]
                name=f"{count} Stars"
            else:
                cat=parts[1]
                country=parts[2]
                if cat=="clean": price=CLEAN[country]
                elif cat=="spam": price=SPAM[country]
                elif cat=="wa": price=WHATSAPP[country]
                elif cat=="tiktok": price=TIKTOK[country]
                elif cat=="fb": price=FACEBOOK[country]
                elif cat=="insta": price=INSTA[country]
                elif cat=="tinder": price=TINDER[country]
                name=f"{cat} {country}"
            if get_balance(uid)<price: bot.answer_callback_query(call.id,f"Need ${price}"); return
            deduct_balance(uid,price)
            pending_orders[uid]={"price":price,"name":name}
            m=types.InlineKeyboardMarkup(row_width=2)
            m.add(types.InlineKeyboardButton("Accept",callback_data=f"accept_{uid}"),types.InlineKeyboardButton("Reject+Refund",callback_data=f"reject_{uid}"))
            bot.send_message(ADMIN_ID,f"Order\nUser {uid}\n{name} ${price}",reply_markup=m)
            bot.answer_callback_query(call.id,"Sent!")
            bot.edit_message_text(f"Deducted ${price}\nWaiting admin\n{name}",uid,call.message.message_id,reply_markup=main_menu(uid))
        except Exception as e: print(e)
        return

@bot.message_handler(content_types=['photo','document','text'])
def all_msg(msg):
    uid=msg.chat.id
    txt=msg.text or ""
    if uid==ADMIN_ID and uid in admin_states:
        state=admin_states[uid]
        if state=="await_id":
            try:
                target=int(txt)
                admin_states[uid]=f"await_amount_{target}"
                bot.send_message(uid,f"ID {target}\nAmount:")
            except: bot.send_message(uid,"Wrong ID")
            return
        if state.startswith("await_amount_"):
            try:
                target=int(state.split("_")[-1])
                amt=float(txt)
                new_bal=add_balance(target,amt)
                bot.send_message(uid,f"Added ${amt} to {target}\n${round(new_bal,2)}",reply_markup=admin_menu())
                bot.send_message(target,f"Recharged ${amt}\nBalance ${round(new_bal,2)}")
                pending_recharge.pop(target,None)
                del admin_states[uid]
            except: bot.send_message(uid,"Wrong amount")
            return
        if state.startswith("await_reply_"):
            try:
                target=int(state.split("_")[-1])
                info=pending_orders.get(target,{})
                bot.send_message(target,f"Delivered:\n{info.get('name')} ${info.get('price')}\n\n{txt}")
                bot.send_message(uid,f"Sent to {target}",reply_markup=admin_menu())
                pending_orders.pop(target,None)
                del admin_states[uid]
            except: pass
            return
    if uid==ADMIN_ID and uid in broadcast_mode:
        if txt=="/cancel":
            del broadcast_mode[uid]
            bot.send_message(uid,"Cancelled",reply_markup=admin_menu())
            return
        count=0
        for u in list(users_cache.keys()):
            try: bot.copy_message(int(u),uid,msg.message_id); count+=1
            except: pass
        bot.send_message(uid,f"Broadcast to {count}",reply_markup=admin_menu())
        del broadcast_mode[uid]
        return
    if uid in pending_recharge:
        m=types.InlineKeyboardMarkup(row_width=2)
        m.add(types.InlineKeyboardButton("Accept",callback_data=f"accept_re_{uid}"),types.InlineKeyboardButton("Reject",callback_data=f"reject_re_{uid}"))
        try: bot.forward_message(ADMIN_ID,uid,msg.message_id)
        except: pass
        bot.send_message(ADMIN_ID,f"Recharge\nUser {uid}\n{pending_recharge[uid]}",reply_markup=m)
        bot.send_message(uid,"Received, waiting admin")
        return
    if uid in pending_orders and uid!=ADMIN_ID:
        try: bot.forward_message(ADMIN_ID,uid,msg.message_id)
        except: pass
        return

print("V41 - Facebook Page Added running...")
bot.delete_webhook(drop_pending_updates=True)
time.sleep(1)
bot.infinity_polling(none_stop=True, timeout=20, long_polling_timeout=20, skip_pending=True)

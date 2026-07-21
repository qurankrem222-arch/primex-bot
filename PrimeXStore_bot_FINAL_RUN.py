import telebot
from telebot import types
import json, os, time

TOKEN = "8315190785:AAFNCBRiF1eimUpePthW2Om1s2F2eC_f8kg"
ADMIN_ID = 8933825471
BOT_USERNAME = "PrimeXStore00bot"
FORCE_CHANNELS = ["@PrimeXStore0", "@PrimeXStore00", "@kingfreebots", "@badel22"]
NOTIFY_CHANNEL = "@PrimeXStore0"
FACEBOOK_PAGE = "https://www.facebook.com/profile.php?id=61592294575700"
SUPPORT = "@PrimeXStore22"

bot = telebot.TeleBot(TOKEN, threaded=False)

balance_cache, users_cache, sub_cache = {}, {}, {}
pending_orders, pending_recharge = {}, {}
broadcast_mode, admin_states, last_added = {}, {}, {}
admins_list = [ADMIN_ID]
banned_users = []

if os.path.exists("balance.json"):
    try: balance_cache = json.load(open("balance.json","r",encoding="utf-8"))
    except: balance_cache = {}
if os.path.exists("users.json"):
    try: users_cache = json.load(open("users.json","r",encoding="utf-8"))
    except: users_cache = {}
if os.path.exists("admins.json"):
    try: admins_list = json.load(open("admins.json","r",encoding="utf-8"))
    except: admins_list = [ADMIN_ID]
if os.path.exists("banned.json"):
    try: banned_users = json.load(open("banned.json","r",encoding="utf-8"))
    except: banned_users = []

def save_bal():
    try: json.dump(balance_cache, open("balance.json","w",encoding="utf-8"))
    except: pass
def save_users():
    try: json.dump(users_cache, open("users.json","w",encoding="utf-8"))
    except: pass
def save_admins():
    try: json.dump(admins_list, open("admins.json","w",encoding="utf-8"))
    except: pass
def save_banned():
    try: json.dump(banned_users, open("banned.json","w",encoding="utf-8"))
    except: pass

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

def send_channel_notify(text):
    try: bot.send_message(NOTIFY_CHANNEL, text, parse_mode="Markdown")
    except:
        try: bot.send_message("@PrimeXStore00", text, parse_mode="Markdown")
        except: pass

FLAGS = {"india":"🇮🇳 India","egypt":"🇪🇬 Egypt","vietnam":"🇻🇳 Vietnam","ksa":"🇸🇦 KSA","pakistan":"🇵🇰 Pakistan","morocco":"🇲🇦 Morocco","myanmar":"🇲🇲 Myanmar","kenya":"🇰🇪 Kenya","indonesia":"🇮🇩 Indonesia","nigeria":"🇳🇬 Nigeria","usa":"🇺🇸 USA","ghana":"🇬🇭 Ghana","sudan":"🇸🇩 Sudan","germany":"🇩🇪 Germany","mozambique":"🇲🇿 Mozambique","random":"🌍 Random","rare":"💎 Rare"}

CLEAN = {"india":0.3,"egypt":0.5,"vietnam":0.9,"ksa":1.5,"pakistan":0.7,"morocco":0.6,"myanmar":0.3,"kenya":0.5,"indonesia":0.6,"nigeria":0.5}
SPAM = {"india":0.2,"random":0.3,"rare":0.45,"usa":0.25,"myanmar":0.2}
TIKTOK = {"germany":0.2,"sudan":0.15}
FACEBOOK = {"indonesia":0.1,"sudan":0.1,"ghana":0.15}
INSTA = {"ghana":0.15}
TINDER = {"indonesia":0.07,"mozambique":0.09}

BOOSTS = {"5": 0.25, "10": 0.50, "25": 1.25, "50": 2.50, "100": 5.00}

FOLLOWER_COUNTS = {"10":0.09,"20":0.18,"50":0.45,"100":0.9,"200":1.8,"300":2.7,"400":3.6,"500":4.5}
ACCOUNTS = {"tiktok_1300":{"name":"TikTok 1300 Followers","price":1.5},"tiktok_2200":{"name":"TikTok 2200 Followers","price":2.0}}
STARS = {"15":0.18,"25":0.29,"50":0.57,"100":1.15}

PAYMENTS = {
    "cwallet":("👛 C-Wallet","61824874"),
    "trc20":("🔸 USDT TRC20","TRHUB8kuMpdCoDzST6c4AJ4cJdk6tToz97"),
    "bep20":("💛 USDT BEP20","0xA7fE0a5Ae6Adcd5b47df238F836449b4d0866155"),
    "erc20":("💎 USDT ERC20","0x8D7dDE7719e9d6D3e5175CE170Fae00372715493"),
    "polygon":("💜 POLYGON","0xA7fE0a5Ae6Adcd5b47df238F836449b4d0866155"),
    "faucetpay":("🚰 FaucetPay","@primexstore22"),
    "gram":("💠 GRAM TON","UQBdPqUEG7TkF2TYWDOEclSYPDec4-HGOsN5ss0Zcnby1mCL"),
}

def admin_menu():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("📊 Stats",callback_data="admin_stats"),types.InlineKeyboardButton("💰 Add Bal",callback_data="admin_add"))
    m.add(types.InlineKeyboardButton("👑 Add Mod",callback_data="admin_addmod"),types.InlineKeyboardButton("🚫 Ban User",callback_data="admin_ban"))
    m.add(types.InlineKeyboardButton("🔓 Unban",callback_data="admin_unban"),types.InlineKeyboardButton("👥 Mods List",callback_data="admin_mods"))
    m.add(types.InlineKeyboardButton("📢 Broadcast",callback_data="admin_bc"),types.InlineKeyboardButton("👤 User Mode",callback_data="admin_user"))
    return m

def main_menu(uid):
    bal=get_balance(uid)
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton(f"💰 ${bal:.2f}",callback_data="bal"),types.InlineKeyboardButton("📱 Numbers",callback_data="nums"))
    m.add(types.InlineKeyboardButton("👥 Followers",callback_data="followers_main"),types.InlineKeyboardButton("🚀 Boosts",callback_data="boosts_main"))
    m.add(types.InlineKeyboardButton("👤 Accounts",callback_data="accounts_main"),types.InlineKeyboardButton("⭐ Stars",callback_data="stars"))
    m.add(types.InlineKeyboardButton("💳 Recharge",callback_data="recharge"),types.InlineKeyboardButton("💬 Support",url=f"https://t.me/{SUPPORT.replace('@','')}"))
    return m

def nums_menu():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("✨ Clean SMS",callback_data="clean"),types.InlineKeyboardButton("🔥 Spam SMS",callback_data="spam"))
    m.add(types.InlineKeyboardButton("🎵 TikTok Numbers",callback_data="tiktok"),types.InlineKeyboardButton("👤 Facebook",callback_data="fb"))
    m.add(types.InlineKeyboardButton("📸 Instagram",callback_data="insta"),types.InlineKeyboardButton("🔥 Tinder",callback_data="tinder"))
    m.add(types.InlineKeyboardButton("⬅️ Back",callback_data="back"))
    return m

def build_nums(data,prefix):
    m=types.InlineKeyboardMarkup(row_width=1)
    for k,price in data.items():
        label=FLAGS.get(k,f"🌍 {k.upper()}")
        m.add(types.InlineKeyboardButton(f"{label} • ${price}",callback_data=f"buy_{prefix}_{k}"))
    m.add(types.InlineKeyboardButton("⬅️ Back",callback_data="nums"))
    return m

def followers_platforms_menu():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("🎵 TikTok",callback_data="fp_tiktok"),types.InlineKeyboardButton("📸 Instagram",callback_data="fp_instagram"))
    m.add(types.InlineKeyboardButton("👤 Facebook",callback_data="fp_facebook"),types.InlineKeyboardButton("✈️ Telegram",callback_data="fp_telegram"))
    m.add(types.InlineKeyboardButton("⬅️ Back",callback_data="back"))
    return m

def followers_counts_menu(platform):
    m=types.InlineKeyboardMarkup(row_width=2)
    for count,price in FOLLOWER_COUNTS.items():
        m.add(types.InlineKeyboardButton(f"👥 {count} • ${price}",callback_data=f"buy_followers_{platform}_{count}"))
    m.add(types.InlineKeyboardButton("⬅️ Back",callback_data="followers_main"))
    return m

def boosts_menu():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton(f"🚀 5 Boosts • $0.25",callback_data="buy_boosts_5"))
    m.add(types.InlineKeyboardButton(f"🚀 10 Boosts • $0.50",callback_data="buy_boosts_10"))
    m.add(types.InlineKeyboardButton(f"🚀 25 Boosts • $1.25",callback_data="buy_boosts_25"))
    m.add(types.InlineKeyboardButton(f"🚀 50 Boosts • $2.50",callback_data="buy_boosts_50"))
    m.add(types.InlineKeyboardButton(f"🚀 100 Boosts • $5.00",callback_data="buy_boosts_100"))
    m.add(types.InlineKeyboardButton("⬅️ Back",callback_data="back"))
    return m

def accounts_menu():
    m=types.InlineKeyboardMarkup(row_width=1)
    for k,v in ACCOUNTS.items():
        m.add(types.InlineKeyboardButton(f"🔥 {v['name']} • ${v['price']}",callback_data=f"buy_accounts_{k}"))
    m.add(types.InlineKeyboardButton("⬅️ Back",callback_data="back"))
    return m

WELCOME = """
🔥🔥🔥 PrimeX Store KING 🔥🔥🔥
👑🔥💎 WELCOME TO THE FIRE STORE 💎🔥👑

💥🔥 الخدمة الأقوى في الشرق الأوسط 🔥💥

💰 رصيدك: ${bal} 💸
🆔 آيديك: {uid}
👑 حالتك: ملك متوج 🔥

━━━━━━━━━━━━━━━━━━
🚀🔥 خدماتنا النارية 🔥🚀
📱 أرقام نارية
👥 رشق متابعين بـ نار 🔥
🚀 تعزيزات - 5 = $0.25 🔥

👇🔥 اختار خدمتك النارية يا ملك 🔥👇
"""

@bot.message_handler(commands=['start'])
def start(msg):
    uid=msg.chat.id
    if is_banned(uid):
        bot.send_message(uid,"🚫 You are banned ❌")
        return
    is_new = str(uid) not in users_cache
    if is_new and uid!= ADMIN_ID:
        for admin_id in admins_list:
            try:
                bot.send_message(admin_id, f"🔔 New User Joined 🔥\n👤 {msg.from_user.first_name}\n🆔 {uid}\n@{msg.from_user.username}\nTotal: {len(users_cache)+1}", parse_mode="Markdown")
            except: pass
    users_cache[str(uid)]={"name":msg.from_user.first_name,"username":msg.from_user.username}
    save_users()
    if is_admin(uid):
        bot.send_message(uid,"👑 Admin Panel V56 FINAL FULL 🔥",reply_markup=admin_menu())
        return
    ok,nj=check_sub(uid)
    if not ok:
        m=types.InlineKeyboardMarkup(row_width=1)
        for ch in nj: m.add(types.InlineKeyboardButton(f"📢 {ch}",url=f"https://t.me/{ch.replace('@','')}"))
        m.add(types.InlineKeyboardButton("📘 Facebook Page",url=FACEBOOK_PAGE))
        m.add(types.InlineKeyboardButton("✅ Done 🔥",callback_data="check"))
        bot.send_message(uid,"⚠️🔥 Must Subscribe First 👇\n\nJoin all channels to continue:",reply_markup=m)
        return
    bot.send_message(uid,WELCOME.format(bal=round(get_balance(uid),2),uid=uid),reply_markup=main_menu(uid))

@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    uid=call.message.chat.id
    d=call.data
    if d=="check":
        sub_cache.pop(uid,None)
        ok,nj=check_sub(uid)
        if not ok:
            bot.answer_callback_query(call.id,"❌ لسه مشتركتش!",show_alert=True)
            return
        bot.edit_message_text(WELCOME.format(bal=round(get_balance(uid),2),uid=uid),uid,call.message.message_id,reply_markup=main_menu(uid))
        return
    if is_admin(uid):
        if d=="admin_stats":
            total=sum(float(v) for v in balance_cache.values())
            bot.edit_message_text(f"📊 Stats 🔥\n💰 Total: ${round(total,2)}\n👥 Users: {len(users_cache)}",uid,call.message.message_id,reply_markup=admin_menu())
        elif d=="admin_add":
            admin_states[uid]="await_id"
            bot.send_message(uid,"💰 Send user ID:")
        elif d=="admin_addmod":
            admin_states[uid]="await_mod"
            bot.send_message(uid,"👑 Send mod ID:")
        elif d=="admin_ban":
            admin_states[uid]="await_ban"
            bot.send_message(uid,"🚫 Send ID to ban:")
        elif d=="admin_unban":
            admin_states[uid]="await_unban"
            bot.send_message(uid,"🔓 Send ID to unban:")
        elif d=="admin_mods":
            txt="👑 Mods:\n"
            for mod in admins_list: txt+=f"`{mod}`\n"
            bot.send_message(uid,txt,parse_mode="Markdown",reply_markup=admin_menu())
        elif d=="admin_bc":
            broadcast_mode[uid]=True
            bot.send_message(uid,"📢 Send broadcast:\n/cancel to abort")
        elif d=="admin_user":
            bot.send_message(uid,WELCOME.format(bal=round(get_balance(uid),2),uid=uid),reply_markup=main_menu(uid))
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
                bot.send_message(cid,"❌ Rejected")
                pending_recharge.pop(cid,None)
                bot.send_message(uid,"Rejected")
                return
            cid=int(d.replace("reject_",""))
            info=pending_orders.get(cid)
            if info: add_balance(cid,info['price']); bot.send_message(cid,f"❌ Rejected & refunded ${info['price']}")
            pending_orders.pop(cid,None)
            bot.send_message(uid,"Rejected & Refunded")
        return

    if d=="bal": bot.answer_callback_query(call.id,f"${round(get_balance(uid),2)}"); return
    if d=="back": bot.edit_message_text(WELCOME.format(bal=round(get_balance(uid),2),uid=uid),uid,call.message.message_id,reply_markup=main_menu(uid)); return
    if d=="nums": bot.edit_message_text("📱 Numbers - Categories: 🔥",uid,call.message.message_id,reply_markup=nums_menu()); return
    if d=="clean": bot.edit_message_text("✨ Clean SMS:",uid,call.message.message_id,reply_markup=build_nums(CLEAN,"clean")); return
    if d=="spam": bot.edit_message_text("🔥 Spam SMS:",uid,call.message.message_id,reply_markup=build_nums(SPAM,"spam")); return
    if d=="tiktok": bot.edit_message_text("🎵 TikTok Numbers:",uid,call.message.message_id,reply_markup=build_nums(TIKTOK,"tiktok")); return
    if d=="fb": bot.edit_message_text("👤 Facebook Numbers:",uid,call.message.message_id,reply_markup=build_nums(FACEBOOK,"fb")); return
    if d=="insta": bot.edit_message_text("📸 Instagram Numbers:",uid,call.message.message_id,reply_markup=build_nums(INSTA,"insta")); return
    if d=="tinder": bot.edit_message_text("🔥 Tinder Numbers:",uid,call.message.message_id,reply_markup=build_nums(TINDER,"tinder")); return
    if d=="followers_main": bot.edit_message_text("👥 Followers - Platforms: 🔥",uid,call.message.message_id,reply_markup=followers_platforms_menu()); return
    if d.startswith("fp_"):
        platform=d.replace("fp_","")
        bot.edit_message_text(f"👥 {platform.upper()} - Counts: 🔥",uid,call.message.message_id,reply_markup=followers_counts_menu(platform))
        return
    if d=="boosts_main":
        bot.edit_message_text("🚀🔥 Channel Boosts 🔥🚀\n💎 5 Boosts = $0.25",uid,call.message.message_id,reply_markup=boosts_menu())
        return
    if d=="accounts_main": bot.edit_message_text("👤 Accounts: 🔥",uid,call.message.message_id,reply_markup=accounts_menu()); return
    if d=="stars":
        m=types.InlineKeyboardMarkup(row_width=2)
        for k,price in STARS.items(): m.add(types.InlineKeyboardButton(f"⭐ {k} - ${price}",callback_data=f"buy_stars_{k}"))
        m.add(types.InlineKeyboardButton("⬅️ Back",callback_data="back"))
        bot.edit_message_text("⭐ Stars: 🔥",uid,call.message.message_id,reply_markup=m); return
    if d=="recharge":
        m=types.InlineKeyboardMarkup(row_width=2)
        for k,(name,addr) in PAYMENTS.items(): m.add(types.InlineKeyboardButton(f"{name}",callback_data=f"pay_{k}"))
        m.add(types.InlineKeyboardButton("⬅️ Back",callback_data="back"))
        bot.edit_message_text(f"💳 Recharge 🔥\nBalance: ${round(get_balance(uid),2)}",uid,call.message.message_id,reply_markup=m); return
    if d.startswith("pay_"):
        k=d.replace("pay_","")
        name,addr=PAYMENTS[k]
        pending_recharge[uid]=k
        bot.edit_message_text(f"{name}\n`{addr}`\n\nSend screenshot",uid,call.message.message_id,parse_mode="Markdown",reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Back",callback_data="recharge")))
        return
    if d.startswith("buy_"):
        try:
            parts=d.split("_")
            if parts[1]=="followers":
                price=FOLLOWER_COUNTS[parts[3]]
                name=f"{parts[2]} {parts[3]} Followers"
                service_type = f"{parts[2]} {parts[3]}"
            elif parts[1]=="accounts":
                v=ACCOUNTS["_".join(parts[2:])]
                price=v['price']; name=v['name']
                service_type = f"{v['name']}"
            elif parts[1]=="stars":
                price=STARS[parts[2]]; name=f"{parts[2]} Stars"
                service_type = f"{parts[2]} Stars"
            elif parts[1]=="boosts":
                count=parts[2]; price=BOOSTS[count]
                name=f"{count} Boosts"
                service_type = f"{count} Boosts"
            else:
                mp={"clean":CLEAN,"spam":SPAM,"tiktok":TIKTOK,"fb":FACEBOOK,"insta":INSTA,"tinder":TINDER}
                price=mp[parts[1]][parts[2]]; name=f"{parts[1]} {parts[2]}"
                service_type = f"{parts[1]} {parts[2]}"
            if get_balance(uid)<price:
                bot.answer_callback_query(call.id,f"Need ${price}",show_alert=True); return
            deduct_balance(uid,price)
            pending_orders[uid]={"price":price,"name":name, "service_type": service_type}
            user_info = users_cache.get(str(uid), {})
            username = user_info.get("username", "No username")
            first_name = user_info.get("name", "Unknown")
            # إشعار القناة - الشكل 3 الاحترافي بدون رصيد
            channel_msg = f"💳 NEW ORDER\n━━━━━━━━━━━━━━\n👤 Customer: {first_name}\n🆔 ID: {uid}\n📦 Service: {service_type}\n💰 Price: ${price}\n🤖 Bot: @{BOT_USERNAME}\n━━━━━━━━━━━━━━"
            send_channel_notify(channel_msg)
            m=types.InlineKeyboardMarkup(row_width=2)
            m.add(types.InlineKeyboardButton("✅ Accept",callback_data=f"accept_{uid}"),types.InlineKeyboardButton("❌ Reject",callback_data=f"reject_{uid}"))
            for admin_id in admins_list:
                try: bot.send_message(admin_id,f"🔔 New Order 🔥\n👤 {uid} @{username}\n📦 {service_type} - ${price}",reply_markup=m)
                except: pass
            bot.edit_message_text(f"✅🔥 Order: {service_type} ${price}",uid,call.message.message_id,reply_markup=main_menu(uid))
        except Exception as e: print(e)

@bot.message_handler(content_types=['photo','document','text'])
def all_msg(msg):
    uid=msg.chat.id
    txt=msg.text or ""
    if is_admin(uid) and uid in admin_states:
        state=admin_states[uid]
        if state=="await_mod":
            try:
                target=int(txt)
                if target not in admins_list:
                    admins_list.append(target); save_admins()
                del admin_states[uid]
            except: bot.send_message(uid,"Wrong ID")
            return
        if state=="await_ban":
            try:
                target=int(txt)
                if target not in banned_users:
                    banned_users.append(target); save_banned()
                del admin_states[uid]
            except: bot.send_message(uid,"Wrong ID")
            return
        if state=="await_unban":
            try:
                target=int(txt)
                if target in banned_users:
                    banned_users.remove(target); save_banned()
                del admin_states[uid]
            except: bot.send_message(uid,"Wrong ID")
            return
        if state=="await_id":
            try:
                target=int(txt)
                admin_states[uid]=f"await_amount_{target}"
                bot.send_message(uid,f"ID {target} - amount:")
            except: bot.send_message(uid,"Wrong ID")
            return
        if state.startswith("await_amount_"):
            try:
                target=int(state.split("_")[-1]); amt=float(txt)
                new_bal=add_balance(target,amt)
                bot.send_message(uid,f"Added ${amt} to {target}",reply_markup=admin_menu())
                try: bot.send_message(target,f"✅ Recharged ${amt}")
                except: pass
                pending_recharge.pop(target,None); del admin_states[uid]
            except: bot.send_message(uid,"Wrong amount")
            return
        if state.startswith("await_reply_"):
            try:
                target=int(state.split("_")[-1]); info=pending_orders.get(target,{})
                bot.send_message(target,f"✅ Delivered {info.get('name')}\n\n{txt}")
                bot.send_message(uid,f"Sent to {target}",reply_markup=admin_menu())
                pending_orders.pop(target,None); del admin_states[uid]
            except: pass
            return
    if is_admin(uid) and uid in broadcast_mode:
        if txt=="/cancel":
            del broadcast_mode[uid]
            bot.send_message(uid,"Cancelled",reply_markup=admin_menu()); return
        c=0
        for u in list(users_cache.keys()):
            try: bot.copy_message(int(u),uid,msg.message_id); c+=1
            except: pass
        bot.send_message(uid,f"Broadcast to {c}",reply_markup=admin_menu())
        del broadcast_mode[uid]; return
    if uid in pending_recharge:
        m=types.InlineKeyboardMarkup(row_width=2)
        m.add(types.InlineKeyboardButton("✅ Accept",callback_data=f"accept_re_{uid}"),types.InlineKeyboardButton("❌ Reject",callback_data=f"reject_re_{uid}"))
        for admin_id in admins_list:
            try: bot.forward_message(admin_id,uid,msg.message_id); bot.send_message(admin_id,f"Recharge {uid}",reply_markup=m)
            except: pass
        bot.send_message(uid,"✅ Received - Waiting admin"); return
    if uid in pending_orders and not is_admin(uid):
        for admin_id in admins_list:
            try: bot.forward_message(admin_id,uid,msg.message_id)
            except: pass

print("V56 FULL FINAL - 4 Channels + FB + New User Notify + Order Notify Style 3 + Boosts 0.25$ 🔥")
bot.delete_webhook(drop_pending_updates=True)
time.sleep(1)
bot.infinity_polling(none_stop=True, timeout=20, long_polling_timeout=20, skip_pending=True)

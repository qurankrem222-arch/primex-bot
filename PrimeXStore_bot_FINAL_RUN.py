import telebot
from telebot import types
import json, os, time

TOKEN = "8315190785:AAFNCBRiF1eimUpePthW2Om1s2F2eC_f8kg"
ADMIN_ID = 8933825471
BOT_USERNAME = "PrimeXStore00bot"
FORCE_CHANNELS = ["@PrimeXStore0", "@PrimeXStore00", "@kingfreebots"]
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
PAYMENTS = {"cwallet":("👛 C-Wallet","61824874"),"trc20":("🔸 TRC20","TRHUB8kuMpdCoDzST6c4AJ4cJdk6tToz97"),"bep20":("💛 BEP20","0xA7fE0a5Ae6Adcd5b47df238F836449b4d0866155")}

def admin_menu():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("📊 Stats",callback_data="admin_stats"),types.InlineKeyboardButton("💰 Add Balance",callback_data="admin_add"))
    m.add(types.InlineKeyboardButton("👑 اضافة مشرف",callback_data="admin_addmod"),types.InlineKeyboardButton("🚫 حظر مستخدم",callback_data="admin_ban"))
    m.add(types.InlineKeyboardButton("🔓 فك الحظر",callback_data="admin_unban"),types.InlineKeyboardButton("👥 قائمة المشرفين",callback_data="admin_mods"))
    m.add(types.InlineKeyboardButton("📢 اذاعة",callback_data="admin_bc"),types.InlineKeyboardButton("👤 وضع المستخدم",callback_data="admin_user"))
    return m

def main_menu(uid):
    bal=get_balance(uid)
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton(f"💰 ${bal:.2f}",callback_data="bal"),types.InlineKeyboardButton("📱 ارقام",callback_data="nums"))
    m.add(types.InlineKeyboardButton("👥 متابعين",callback_data="followers_main"),types.InlineKeyboardButton("⭐ نجوم",callback_data="stars"))
    m.add(types.InlineKeyboardButton("💳 شحن",callback_data="recharge"),types.InlineKeyboardButton("🔗 رابط الدعوة",callback_data="invite"))
    return m

WELCOME = "👑 *PrimeX Store* 👑\n\n💰 `${bal}`\n🆔 `{uid}`\n\n👇 اختار 👇"

@bot.message_handler(commands=['start'])
def start(msg):
    uid=msg.chat.id
    if is_banned(uid):
        bot.send_message(uid,"🚫 انت محظور من البوت")
        return
    # اشعار دخول جديد
    if str(uid) not in users_cache and uid!= ADMIN_ID:
        for admin_id in admins_list:
            try:
                bot.send_message(admin_id, f"🔔 *عضو جديد دخل!*\n\n👤 {msg.from_user.first_name}\n🆔 `{uid}`\n🔗 @{msg.from_user.username if msg.from_user.username else 'لا يوجد'}\n\n📊 الاجمالي: {len(users_cache)+1}", parse_mode="Markdown")
            except: pass

    users_cache[str(uid)]={"name":msg.from_user.first_name,"username":msg.from_user.username}
    save_users()

    if is_admin(uid):
        bot.send_message(uid,"👑 *لوحة الادمن* 👑\n\n🔥 الازرار الجديدة:\n👑 اضافة مشرف\n🚫 حظر مستخدم",parse_mode="Markdown",reply_markup=admin_menu())
        return
    ok,nj=check_sub(uid)
    if not ok:
        m=types.InlineKeyboardMarkup()
        for ch in nj: m.add(types.InlineKeyboardButton(f"📢 {ch}",url=f"https://t.me/{ch.replace('@','')}"))
        m.add(types.InlineKeyboardButton("📘 Facebook",url=FACEBOOK_PAGE))
        m.add(types.InlineKeyboardButton("✅ تم",callback_data="check"))
        bot.send_message(uid,"⚠️ اشترك اولا",reply_markup=m)
        return
    bot.send_message(uid,WELCOME.format(bal=round(get_balance(uid),2),uid=uid),parse_mode="Markdown",reply_markup=main_menu(uid))

@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    uid=call.message.chat.id
    d=call.data
    if d=="check":
        sub_cache.pop(uid,None)
        ok,nj=check_sub(uid)
        if not ok:
            bot.answer_callback_query(call.id,"❌ لسه مشتركتش",show_alert=True)
            return
        bot.edit_message_text(WELCOME.format(bal=round(get_balance(uid),2),uid=uid),uid,call.message.message_id,parse_mode="Markdown",reply_markup=main_menu(uid))
        return
    if is_admin(uid):
        if d=="admin_stats":
            total=sum(float(v) for v in balance_cache.values())
            bot.edit_message_text(f"📊 الاحصائيات:\n💰 الاجمالي: ${round(total,2)}\n👥 المستخدمين: {len(users_cache)}\n👑 المشرفين: {len(admins_list)}\n🚫 المحظورين: {len(banned_users)}",uid,call.message.message_id,reply_markup=admin_menu())
        elif d=="admin_add":
            admin_states[uid]="await_id"
            bot.send_message(uid,"💰 ابعت ID المستخدم:")
        elif d=="admin_addmod":
            if uid!= ADMIN_ID:
                bot.answer_callback_query(call.id,"❌ بس المالك يقدر يضيف مشرفين",show_alert=True)
                return
            admin_states[uid]="await_mod"
            bot.send_message(uid,"👑 *اضافة مشرف*\n\nابعت ID المشرف الجديد:")
        elif d=="admin_ban":
            admin_states[uid]="await_ban"
            bot.send_message(uid,"🚫 *حظر مستخدم*\n\nابعت ID المستخدم اللي عايز تحظره:")
        elif d=="admin_unban":
            admin_states[uid]="await_unban"
            bot.send_message(uid,"🔓 ابعت ID لفك الحظر:")
        elif d=="admin_mods":
            txt="👑 *قائمة المشرفين:*\n\n"
            for mod in admins_list:
                txt+=f"• `{mod}` {'(المالك)' if mod==ADMIN_ID else ''}\n"
            txt+=f"\n🚫 المحظورين: {len(banned_users)}"
            bot.send_message(uid,txt,parse_mode="Markdown")
        elif d=="admin_bc":
            broadcast_mode[uid]=True
            bot.send_message(uid,"📢 ابعت رسالة الاذاعة:\n/cancel للالغاء")
        elif d=="admin_user":
            bot.send_message(uid,WELCOME.format(bal=round(get_balance(uid),2),uid=uid),parse_mode="Markdown",reply_markup=main_menu(uid))
        return
    if d=="invite":
        link=f"https://t.me/{BOT_USERNAME}?start={uid}"
        bot.send_message(uid,f"🔗 رابط دعوتك:\n`{link}`\n\n📤 انشره!",parse_mode="Markdown")
    if d=="back":
        bot.edit_message_text(WELCOME.format(bal=round(get_balance(uid),2),uid=uid),uid,call.message.message_id,parse_mode="Markdown",reply_markup=main_menu(uid))

@bot.message_handler(content_types=['photo','document','text'])
def all_msg(msg):
    uid=msg.chat.id
    txt=msg.text or ""
    if is_admin(uid) and uid in admin_states:
        state=admin_states[uid]
        if state=="await_id":
            try:
                target=int(txt)
                admin_states[uid]=f"await_amount_{target}"
                bot.send_message(uid,f"✅ ID {target}\n💰 ابعت المبلغ:")
            except: bot.send_message(uid,"❌ ID غلط")
            return
        if state=="await_mod":
            try:
                target=int(txt)
                if target not in admins_list:
                    admins_list.append(target)
                    save_admins()
                    bot.send_message(uid,f"✅ تم اضافة مشرف\n👑 `{target}`",parse_mode="Markdown",reply_markup=admin_menu())
                    try: bot.send_message(target,"👑 مبروك! بقيت مشرف في البوت 👑")
                    except: pass
                else: bot.send_message(uid,"⚠️ ده مشرف already")
                del admin_states[uid]
            except: bot.send_message(uid,"❌ ID غلط")
            return
        if state=="await_ban":
            try:
                target=int(txt)
                if target==ADMIN_ID:
                    bot.send_message(uid,"❌ مينفعش تحظر المالك")
                    del admin_states[uid]
                    return
                if target not in banned_users:
                    banned_users.append(target)
                    save_banned()
                    bot.send_message(uid,f"🚫 تم حظر المستخدم\n🆔 `{target}`",parse_mode="Markdown",reply_markup=admin_menu())
                    try: bot.send_message(target,"🚫 تم حظرك من البوت")
                    except: pass
                else: bot.send_message(uid,"⚠️ محظور already")
                del admin_states[uid]
            except: bot.send_message(uid,"❌ ID غلط")
            return
        if state=="await_unban":
            try:
                target=int(txt)
                if target in banned_users:
                    banned_users.remove(target)
                    save_banned()
                    bot.send_message(uid,f"🔓 تم فك الحظر\n🆔 `{target}`",parse_mode="Markdown",reply_markup=admin_menu())
                else: bot.send_message(uid,"⚠️ مش محظور اصلا")
                del admin_states[uid]
            except: bot.send_message(uid,"❌ ID غلط")
            return
        if state.startswith("await_amount_"):
            try:
                target=int(state.split("_")[-1])
                amt=float(txt)
                new_bal=add_balance(target,amt)
                bot.send_message(uid,f"✅ تم اضافة ${amt} لـ {target}\nالرصيد الجديد: ${round(new_bal,2)}",reply_markup=admin_menu())
                try: bot.send_message(target,f"✅ تم شحن رصيدك ${amt}\n💳 الجديد: ${round(new_bal,2)}")
                except: pass
                del admin_states[uid]
            except: bot.send_message(uid,"❌ مبلغ غلط")
            return
    if is_admin(uid) and uid in broadcast_mode:
        if txt=="/cancel":
            del broadcast_mode[uid]
            bot.send_message(uid,"❌ اتلغت",reply_markup=admin_menu())
            return
        c=0
        for u in list(users_cache.keys()):
            try: bot.copy_message(int(u),uid,msg.message_id); c+=1
            except: pass
        bot.send_message(uid,f"✅ تم الارسال لـ {c}",reply_markup=admin_menu())
        del broadcast_mode[uid]

print("V48 - Add Mod & Ban & Notifications ON")
bot.delete_webhook(drop_pending_updates=True)
bot.infinity_polling()

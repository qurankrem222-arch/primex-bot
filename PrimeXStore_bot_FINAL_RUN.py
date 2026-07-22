import telebot
from telebot import types
import json, os, time

TOKEN = os.getenv("TOKEN", "PUT NEW TOKEN HERE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8933825471"))
BOT_USERNAME = "SocialSMSbot"
FORCE_CHANNELS = ["@SocialSMS1", "@SocialSMS2"]
SUPPORT = "@SocialSMSSUPPORT"
REF_REWARD = 0.003
MIN_DEPOSIT = 0.1

bot = telebot.TeleBot(TOKEN, threaded=False)

balance_cache, users_cache = {}, {}
pending_orders = {}
pending_recharge = {}
pending_rating = {}
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

def is_admin(uid): return uid in admins_list or str(uid) in [str(x) for x in admins_list]
def is_banned(uid): return uid in banned_users or str(uid) in banned_users
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

FLAGS = {"myanmar":"🇲🇲 Myanmar","syria":"🇸🇾 Syria","morocco":"🇲🇦 Morocco","usa":"🇺🇸 USA","india":"🇮🇳 India","ksa":"🇸🇦 KSA","egypt":"🇪🇬 Egypt"}
CLEAN = {"myanmar":0.2,"syria":0.8,"morocco":0.6,"usa":0.3,"india":0.25,"ksa":1.3,"egypt":0.7}
SPAM = {"myanmar":0.15,"usa":0.2,"india":0.2}

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
    m.add(types.InlineKeyboardButton("👤💎 شراء حسابات", callback_data="buy_numbers_main"), types.InlineKeyboardButton("💰🚀 شحن رصيد", callback_data="recharge"))
    m.add(types.InlineKeyboardButton("🔗🎁 دعوة واربح", callback_data="invite"), types.InlineKeyboardButton("💬👑 الدعم الفني", url="https://t.me/SocialSMSSUPPORT"))
    m.add(types.InlineKeyboardButton("📢📣 قناتنا", url="https://t.me/SocialSMS1"))
    m.add(types.InlineKeyboardButton("🌟 تقييم البوت ⭐", callback_data="rate"))
    return m

def buy_numbers_main_menu():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("✨💎 ارقام سليمة",callback_data="clean"), types.InlineKeyboardButton("🔥⚡ ارقام اسبام",callback_data="spam"))
    m.add(types.InlineKeyboardButton("🔙🏠 رجوع رئيسية",callback_data="back"))
    return m

def build_nums(data,prefix):
    m=types.InlineKeyboardMarkup(row_width=1)
    for k,price in data.items():
        label=FLAGS.get(k,k); stars=int(price*100)
        m.add(types.InlineKeyboardButton(f"{label} • ${price} (⭐{stars})",callback_data=f"buy_{prefix}_{k}"))
    m.add(types.InlineKeyboardButton("🔙 رجوع",callback_data="buy_numbers_main"))
    return m

WELCOME = """╔═══════════════════════╗
   🔥👑 𝗦𝗢𝗖𝗜𝗔𝗟 𝗦𝗠𝗦 👑🔥
   🌟 افضل بوت ارقام في التيليجرام 🌟

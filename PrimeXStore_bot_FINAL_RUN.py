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

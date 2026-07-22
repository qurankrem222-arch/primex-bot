import asyncio
import logging
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, LabeledPrice
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# ============ الاعدادات ============
BOT_TOKEN = "8410968304:AAEwoOxU4stdUEK_JSefuLGov3nMD1iQT6s"
ADMIN_ID = 8811384711
ORDERS_CHANNEL_ID = -1004466989868
FORCE_JOIN_CHANNELS = ["@SocialSMS2", "@SocialSMS1"]
SUPPORT_USERNAME = "@SocialSMSSUPPORT"
REFERRAL_REWARD_STARS = 0.0003

# الاسعار بالنجوم والدولار
CLEAN_NUMBERS = {
    "🇲🇲 ميانمار": {"stars": 20, "usd": 0.2},
    "🇸🇾 سوريا": {"stars": 80, "usd": 0.8},
    "🇲🇦 المغرب": {"stars": 60, "usd": 0.6},
    "🇺🇸 امريكا": {"stars": 30, "usd": 0.3},
    "🇮🇳 الهند": {"stars": 25, "usd": 0.25},
    "🇸🇦 السعودية": {"stars": 130, "usd": 1.3},
    "🇪🇬 مصر": {"stars": 70, "usd": 0.7},
}

SPAM_NUMBERS = {
    "🇲🇲 ميانمار": {"stars": 15, "usd": 0.15},
    "🇺🇸 امريكا": {"stars": 20, "usd": 0.2},
    "🇮🇳 الهند": {"stars": 20, "usd": 0.2},
}

CURRENCY_WALLETS = {
    "🆔 Cwallet ID": "61824874",
    "💵 USDT BEP20": "0x3dcF20c18f03F0016BeB5dE3A2979cF65e5DE596",
    "💵 USDT TRC20": "TRmkCedsJP9MongBrvy4gwdfBX5v8nSsqL",
    "💵 USDT ERC20": "0x5623f438C721D284e9257d2815a82a267b7F4d51",
    "💵 USDT POL": "0x5D14363342328D49C9094b61822608aB285Db59a",
    "🪙 LTC": "ltc1qk7gs0gt4zt0e0ztsv8g65sgq6h0s79ucfyl6ld",
    "🟡 BNB BEP20": "0x3dcF20c18f03F0016BeB5dE3A2979cF65e5DE596",
    "💲 USDC SOL": "Dw27gnVFsjQRTG3HpsVwawBPfzx1RPpRDsJtdKGNop2p",
    "💎 GRAM": "EQD14kgmngE0fNYVs7_9dw78V3rPhNt7_Ee-7X3ykDORQvMp",
    "🚰 FaucetPay": "primexstore22",
    "💳 فودافون كاش": "راسل الدعم @SocialSMSSUPPORT لمعرفة الرقم",
}
CURRENCIES = list(CURRENCY_WALLETS.keys())

STAR_PACKAGES = {
    "15": {"stars": 15, "price_usd": 0.12},
    "25": {"stars": 25, "price_usd": 0.22},
    "50": {"stars": 50, "price_usd": 0.42},
    "100": {"stars": 100, "price_usd": 0.90},
}

DB_FILE = "database.json"
def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "orders": {}, "order_counter": 0, "banned": [], "deposits": {}, "deposit_counter": 0}
    with open(DB_FILE, "r", encoding="utf-8") as ff:
        data = json.load(ff)
        if "banned" not in data: data["banned"] = []
        if "users" not in data: data["users"] = {}
        if "orders" not in data: data["orders"] = {}
        if "order_counter" not in data: data["order_counter"] = 0
        if "deposits" not in data: data["deposits"] = {}
        if "deposit_counter" not in data: data["deposit_counter"] = 0
        return data

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(f, data, ensure_ascii=False, indent=2)

db = load_db()

class DeliverState(StatesGroup):
    waiting_order_id = State()
    waiting_number = State()
    waiting_add_balance_id = State()
    waiting_add_balance_amount = State()
    waiting_ban_id = State()
    waiting_unban_id = State()
    waiting_broadcast = State()
    waiting_deposit_currency = State()
    waiting_deposit_amount = State()
    waiting_deposit_screenshot = State()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

def main_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛒 شراء حسابات")],
        [KeyboardButton(text="👥 دعوة اصدقاء"), KeyboardButton(text="👤 حسابي")],
        [KeyboardButton(text="⭐ شحن بالنجوم"), KeyboardButton(text="💳 شحن رصيد")],
        [KeyboardButton(text="📞 الدعم")]
    ], resize_keyboard=True)

def category_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ الأرقام السليمة", callback_data="cat_clean")],
        [InlineKeyboardButton(text="⚠️ أرقام سبام (محظورة)", callback_data="cat_spam")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="back_main")]
    ])

def get_price_info(item):
    if isinstance(item, dict):
        return item.get("stars", 0), item.get("usd", 0)
    return item, round(item * 0.009, 2)

def countries_keyboard(cat):
    data = CLEAN_NUMBERS if cat == "clean" else SPAM_NUMBERS
    buttons = []
    for name, price_data in data.items():
        stars, usd = get_price_info(price_data)
        buttons.append([InlineKeyboardButton(text=f"{name} - {stars} ⭐ (${usd})", callback_data=f"buy_{cat}_{name}_{stars}")])
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="cat_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def check_join(user_id):
    for ch in FORCE_JOIN_CHANNELS:
        try:
            member = await bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except: continue
    return True

@dp.message(Command("start"))
async def start_cmd(message: types.Message, command: CommandObject):
    if str(message.from_user.id) in db.get("banned", []) or message.from_user.id in db.get("banned", []):
        await message.answer("🚫 انت محظور من استخدام البوت\nراسل الدعم: " + SUPPORT_USERNAME)
        return
    user_id = str(message.from_user.id)
    args = command.args
    is_new = user_id not in db["users"]
    if is_new:
        db["users"][user_id] = {"balance": 0, "invites": 0, "username": message.from_user.username or "بدون", "first_name": message.from_user.first_name or "", "joined": message.date.isoformat() if hasattr(message, 'date') else ""}
        if args and args!= user_id and args in db["users"]:
            db["users"][args]["balance"] += REFERRAL_REWARD_STARS
            db["users"][args]["invites"] += 1
            try:
                await bot.send_message(int(args), f"🎉 شخص جديد دخل بدعوتك! كسبت {REFERRAL_REWARD_STARS} ⭐")
            except: pass
        save_db(db)
        try:
            new_user_text = f"👤 **مستخدم جديد دخل البوت**\n\n🆔 الايدي: `{message.from_user.id}`\n👤 الاسم: {message.from_user.first_name}\n🔗 اليوزر: @{message.from_user.username or 'بدون'}\n📥 جاي من دعوة: {args if args else 'دخول مباشر'}\n👥 اجمالي المستخدمين: {len(db['users'])}"
            kb_new = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👤 معلوماته", callback_data=f"dep_info_{message.from_user.id}"), InlineKeyboardButton(text="💳 اضافة رصيد", callback_data="admin_add_balance")],
                [InlineKeyboardButton(text="🚫 حظره", callback_data=f"ban_quick_{message.from_user.id}")]
            ])
            await bot.send_message(ADMIN_ID, new_user_text, parse_mode="Markdown", reply_markup=kb_new)
            await bot.send_message(ORDERS_CHANNEL_ID, f"👤 مستخدم جديد: @{message.from_user.username or 'بدون'} | `{message.from_user.id}` | {message.from_user.first_name}")
        except Exception as e:
            print(f"notify error: {e}")

    if not await check_join(message.from_user.id):
        txt = "⚠️ لازم تشترك في القنوات الاول:\n"
        kb = []
        for ch in FORCE_JOIN_CHANNELS:
            txt += f"👉 {ch}\n"
            kb.append([InlineKeyboardButton(text=f"اشترك في {ch}", url=f"https://t.me/{ch.replace('@','')}")])
        kb.append([InlineKeyboardButton(text="✅ تحققت - ابدأ", callback_data="check_join")])
        await message.answer(txt, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
        return

    welcome = f"""
✨ **شـراء حسـابـات** ✨

أهلا بيك يا {message.from_user.first_name} 👋
أكبر متجر لبيع أرقام تليجرام

✅ أرقام سليمة ونضيفة
⚠️ أرقام سبام رخيصة

اختر من القائمة تحت 👇
"""
    await message.answer(welcome, reply_markup=main_keyboard(), parse_mode="Markdown")
  @dp.message(F.text == "🛒 شراء حسابات")
async def buy_menu(message: types.Message):
    await message.answer("اختر نوع الأرقام 👇", reply_markup=category_keyboard())

@dp.callback_query(F.data.startswith("cat_"))
async def cat_handler(call: types.CallbackQuery):
    if call.data == "cat_clean":
        await call.message.edit_text("✅ **قسم الأرقام السليمة**\nاختر الدولة:", reply_markup=countries_keyboard("clean"), parse_mode="Markdown")
    elif call.data == "cat_spam":
        await call.message.edit_text("⚠️ **قسم أرقام السبام (محظورة)**\nسعر رخيص بس عليها حظر رسائل مؤقت:", reply_markup=countries_keyboard("spam"), parse_mode="Markdown")
    elif call.data == "cat_back":
        await call.message.edit_text("اختر نوع الأرقام 👇", reply_markup=category_keyboard())
    await call.answer()

@dp.callback_query(F.data.startswith("buy_"))
async def buy_country(call: types.CallbackQuery):
    _, cat, name, price = call.data.split("_", 3)
    price = int(price)
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title=f"شراء رقم {name}",
        description=f"نوع الرقم: {'سليم ✅' if cat=='clean' else 'سبام ⚠️'}\nالدولة: {name}",
        payload=f"order_{cat}_{name}_{price}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=f"{name}", amount=price)],
    )
    await call.answer()

@dp.pre_checkout_query()
async def pre_checkout(q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(q.id, ok=True)

@dp.message(F.successful_payment)
async def success_pay(message: types.Message):
    pay = message.successful_payment
    payload = pay.invoice_payload

    if payload.startswith("stars_pack_"):
        amount_key = payload.split("_")[-1]
        pack = STAR_PACKAGES.get(amount_key)
        stars_added = pack["stars"] if pack else pay.total_amount
        uid = str(message.from_user.id)
        if uid not in db["users"]:
            db["users"][uid] = {"balance": 0, "invites": 0, "username": message.from_user.username or "بدون"}
        db["users"][uid]["balance"] += stars_added
        save_db(db)
        await message.answer(f"✅ تم شحن {stars_added} ⭐ بنجاح!\n💳 رصيدك الحالي: {db['users'][uid]['balance']} ⭐")
        try:
            await bot.send_message(ORDERS_CHANNEL_ID, f"💸 **شحن نجوم جديد**\n👤: @{message.from_user.username or 'بدون'} | `{message.from_user.id}`\n⭐ الباقة: {stars_added} نجمة\n💰 دفع: {pay.total_amount} ⭐")
        except: pass
        return

    try:
        _, cat, name, price = payload.split("_", 3)
    except:
        cat, name, price = "clean", "غير معروف", pay.total_amount

    db["order_counter"] += 1
    order_id = db["order_counter"]
    order = {
        "id": order_id,
        "user_id": message.from_user.id,
        "username": message.from_user.username or "بدون",
        "type": "سليم ✅" if cat=="clean" else "سبام ⚠️",
        "country": name,
        "price": pay.total_amount,
        "status": "pending"
    }
    db["orders"][str(order_id)] = order
    save_db(db)

    await message.answer(f"✅ تم الدفع بنجاح!\n🆔 طلبك رقم #{order_id}\n📦 {name} - {order['type']}\n⏳ جاري تسليم الرقم، انتظر رسالة من الادمن...")

    try:
        await bot.send_message(ORDERS_CHANNEL_ID, f"🔔 **طلب جديد #{order_id}**\n👤: @{order['username']} | `{order['user_id']}`\n📦 النوع: {order['type']}\n🌍 الدولة: {name}\n💰 السعر: {pay.total_amount} ⭐", parse_mode="Markdown")
    except Exception as e:
        print(f"Channel error {e}")

@dp.message(F.text == "👥 دعوة اصدقاء")
async def invite(message: types.Message):
    uid = message.from_user.id
    link = f"https://t.me/{(await bot.get_me()).username}?start={uid}"
    invites = db["users"].get(str(uid), {}).get("invites", 0)
    await message.answer(f"👥 **نظام الدعوات**\n\n🔗 رابطك الخاص:\n`{link}`\n\n👤 دعوت: {invites} شخص\n💰 تربح {REFERRAL_REWARD_STARS} ⭐ على كل دعوة\n\nشارك الرابط واكسب نجوم!", parse_mode="Markdown")

@dp.message(F.text == "👤 حسابي")
async def my_account(message: types.Message):
    u = db["users"].get(str(message.from_user.id), {"balance":0, "invites":0})
    await message.answer(f"👤 **حسابك**\n\n🆔 ID: `{message.from_user.id}`\n💳 رصيدك: {u.get('balance',0)} ⭐\n👥 دعواتك: {u.get('invites',0)}\n👤 يوزرك: @{message.from_user.username or 'بدون'}", parse_mode="Markdown")

@dp.message(F.text == "📞 الدعم")
async def support(message: types.Message):
    await message.answer(f"📞 **الدعم الفني**\n\nكلم الادمن: {SUPPORT_USERNAME}\n\nلو عندك مشكلة في طلب ابعت رقم الطلب #")

@dp.message(F.text == "⭐ شحن بالنجوم")
async def charge_stars_menu(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="15 ⭐ - بـ 0.12$", callback_data="pack_15")],
        [InlineKeyboardButton(text="25 ⭐ - بـ 0.22$", callback_data="pack_25")],
        [InlineKeyboardButton(text="50 ⭐ - بـ 0.42$", callback_data="pack_50")],
        [InlineKeyboardButton(text="100 ⭐ - بـ 0.90$", callback_data="pack_100")],
    ])
    await message.answer("⭐ **شحن بالنجوم**\n\nاختر الباقة اللي عايزها:\n\n💎 15 نجمة = 0.12$\n💎 25 نجمة = 0.22$\n💎 50 نجمة = 0.42$\n💎 100 نجمة = 0.90$\n\nالدفع بالنجوم مباشرة من تليجرام", reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("pack_"))
async def buy_star_pack(call: types.CallbackQuery):
    amount = call.data.split("_")[1]
    pack = STAR_PACKAGES[amount]
    txt = f"""⭐ طلب شحن {pack['stars']} نجمة

💰 السعر: {pack['price_usd']}$

📩 لإكمال الإيداع راسل الدعم: {SUPPORT_USERNAME}

أرسل للدعم:
- اليوزر بتاعك: @{call.from_user.username or 'بدون'}
- ايديك: `{call.from_user.id}`
- الباقة: {pack['stars']} نجمة

بعد التحويل سيتم اضافة الرصيد لحسابك خلال دقائق ✅
"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 راسل الدعم", url=f"https://t.me/{SUPPORT_USERNAME.replace('@','')}")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="back_to_packs")]
    ])
    await call.message.edit_text(txt, reply_markup=kb, parse_mode="Markdown")
    try:
        await bot.send_message(ORDERS_CHANNEL_ID, f"💸 **طلب شحن نجوم جديد (يدوي)**\n👤: @{call.from_user.username or 'بدون'} | `{call.from_user.id}`\n⭐ الباقة: {pack['stars']} نجمة - {pack['price_usd']}$")
    except: pass
    await call.answer()

@dp.message(F.text == "💳 شحن رصيد")
async def charge(message: types.Message, state: FSMContext):
    if str(message.from_user.id) in db.get("banned", []):
        await message.answer("🚫 انت محظور")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=c, callback_data=f"curr_{c}")] for c in CURRENCIES
    ])
    await message.answer("💳 **اختر طريقة الدفع / العملة**\n\nاختر العملة اللي هتدفع بيها:", reply_markup=kb, parse_mode="Markdown")
    await state.set_state(DeliverState.waiting_deposit_currency)

@dp.callback_query(F.data.startswith("curr_"))
async def deposit_choose_currency(call: types.CallbackQuery, state: FSMContext):
    currency = call.data.replace("curr_", "")
    wallet = CURRENCY_WALLETS.get(currency, "راسل الدعم")
    await state.update_data(currency=currency)
    text = f"✅ اخترت: **{currency}**\n\n"
    if "فودافون" in currency:
        text += f"📱 {wallet}\n\n"
    elif "GRAM" in currency:
        text += f"📥 **عنوان المحفظة - اضغط للنسخ:**\n`EQD14kgmngE0fNYVs7_9dw78V3rPhNt7_Ee-7X3ykDORQvMp`\n\n"
        text += f"🏷️ **الميمو تاج - اضغط للنسخ لوحده:**\n`10051143`\n\n"
        text += "🚨🚨 **تحذييييير خطير جدا** 🚨🚨\n"
        text += "لو ما كتبتش الميمو تاج `10051143` وانت بتحول، فلوسك هتضيع ومش هتوصل ومش هنقدر نرجعها نهائيا ❌\n"
        text += "لازم تكتب الميمو تاج في خانة التعليق / Memo / Tag وانت بتحول\n\n"
    else:
        text += f"📥 **عنوان المحفظة - اضغط للنسخ:**\n`{wallet}`\n\n⚠️ انسخ العنوان بالضغط عليه\n\n"
        if "Cwallet" in currency:
            text += "في Cwallet اعمل تحويل داخلي بالـ ID\n\n"

    text += "💰 **الاسعار:**\n15 ⭐ = 0.12$\n25 ⭐ = 0.22$\n50 ⭐ = 0.42$\n100 ⭐ = 0.90$\n\n✍️ اكتب كمية النجوم اللي عايز تشحنها (مثال: 50)"

    await call.message.edit_text(text, parse_mode="Markdown")
    await state.set_state(DeliverState.waiting_deposit_amount)
    await call.answer()

@dp.message(DeliverState.waiting_deposit_amount)
async def deposit_get_amount(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
        if amount <=0: raise ValueError()
        await state.update_data(amount=amount)
        await message.answer("📸 **الخطوة الاخيرة**\n\nابعت صورة التحويل دلوقتي\n\n⚠️ لازم الصورة توضح المبلغ والتاريخ", parse_mode="Markdown")
        await state.set_state(DeliverState.waiting_deposit_screenshot)
    except:
        await message.answer("❌ اكتب رقم صحيح مثلا 15")

@dp.message(DeliverState.waiting_deposit_screenshot, F.photo)
async def deposit_get_screenshot(message: types.Message, state: FSMContext):
    data = await state.get_data()
    currency = data.get("currency")
    amount = data.get("amount")

    db["deposit_counter"] += 1
    dep_id = str(db["deposit_counter"])
    db["deposits"][dep_id] = {
        "id": dep_id,
        "user_id": message.from_user.id,
        "username": message.from_user.username or "بدون",
        "currency": currency,
        "amount": amount,
        "photo_id": message.photo[-1].file_id,
        "status": "pending"
    }
    save_db(db)

    await message.answer(f"✅ تم استلام طلبك #{dep_id}\n\n💳 العملة: {currency}\n⭐ الكمية: {amount} نجمة\n⏳ الحالة: قيد المراجعة\n\nسيتم مراجعته من الادمن خلال دقائق", parse_mode="Markdown")

    caption = f"💸 **طلب شحن جديد #{dep_id}**\n\n👤 العميل: @{message.from_user.username or 'بدون'} | `{message.from_user.id}`\n💳 العملة: {currency}\n⭐ الكمية: {amount} نجمة\n🆔 الطلب: #{dep_id}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ قبول واضافة الرصيد", callback_data=f"dep_ok_{dep_id}"),
         InlineKeyboardButton(text="❌ رفض", callback_data=f"dep_no_{dep_id}")],
        [InlineKeyboardButton(text="👤 معلومات العميل", callback_data=f"dep_info_{message.from_user.id}")]
    ])
    try:
        await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=caption, reply_markup=kb, parse_mode="Markdown")
        await bot.send_photo(chat_id=ORDERS_CHANNEL_ID, photo=message.photo[-1].file_id, caption=caption)
    except Exception as e:
        print(e)

    await state.clear()

@dp.callback_query(F.data.startswith("dep_ok_"))
async def deposit_accept(call: types.CallbackQuery):
    dep_id = call.data.replace("dep_ok_", "")
    dep = db["deposits"].get(dep_id)
    if not dep:
        await call.answer("الطلب مش موجود")
        return
    if dep["status"]!= "pending":
        await call.answer(f"الطلب ده {dep['status']} بالفعل")
        return

    uid = str(dep["user_id"])
    amount = dep["amount"]
    if uid not in db["users"]:
        db["users"][uid] = {"balance": 0, "invites": 0, "username": dep["username"]}
    db["users"][uid]["balance"] += amount
    dep["status"] = "accepted"
    save_db(db)

    await call.message.edit_caption(caption=call.message.caption + f"\n\n✅ **تم القبول** بواسطة الادمن", parse_mode="Markdown")
    await call.answer("تم قبول الطلب واضافة الرصيد")

    try:
        await bot.send_message(int(uid), f"✅ **تم قبول طلب الشحن #{dep_id}**\n\n💳 العملة: {dep['currency']}\n⭐ تم اضافة {amount} نجمة لرصيدك\n💰 رصيدك الحالي: {db['users'][uid]['balance']} ⭐\n\nشكرا لتعاملك معنا ❤️")
    except: pass

@dp.callback_query(F.data.startswith("dep_no_"))
async def deposit_reject(call: types.CallbackQuery):
    dep_id = call.data.replace("dep_no_", "")
    dep = db["deposits"].get(dep_id)
    if not dep:
        await call.answer("الطلب مش موجود")
        return
    if dep["status"]!= "pending":
        await call.answer(f"الطلب ده {dep['status']} بالفعل")
        return

    dep["status"] = "rejected"
    save_db(db)

    await call.message.edit_caption(caption=call.message.caption + f"\n\n❌ **تم الرفض** بواسطة الادمن", parse_mode="Markdown")
    await call.answer("تم رفض الطلب")

    try:
        await bot.send_message(int(dep["user_id"]), f"❌ **تم رفض طلب الشحن #{dep_id}**\n\n💳 العملة: {dep['currency']}\n⭐ الكمية: {dep['amount']} نجمة\n\nالسبب: السكرين غير واضح او المبلغ غير صحيح\nراسل الدعم: {SUPPORT_USERNAME}")
    except: pass

@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id!= ADMIN_ID: return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 الطلبات المعلقة", callback_data="admin_pending")],
        [InlineKeyboardButton(text="📦 تسليم رقم", callback_data="admin_deliver")],
        [InlineKeyboardButton(text="💳 اضافة رصيد", callback_data="admin_add_balance")],
        [InlineKeyboardButton(text="🚫 حظر مستخدم", callback_data="admin_ban")],
        [InlineKeyboardButton(text="✅ الغاء حظر مستخدم", callback_data="admin_unban")],
        [InlineKeyboardButton(text="📢 اذاعة للكل", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="📊 الاحصائيات", callback_data="admin_stats")],
    ])
    await message.answer("👑 **لوحة الادمن**", reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "admin_pending")
async def admin_pending(call: types.CallbackQuery):
    pending = [o for o in db["orders"].values() if o["status"]=="pending"]
    if not pending:
        await call.message.answer("لا يوجد طلبات معلقة ✅")
    else:
        txt = "📋 **الطلبات المعلقة:**\n\n"
        for o in pending[-10:]:
            txt += f"#{o['id']} - {o['country']} {o['type']} - @{o['username']} - {o['user_id']}\n"
        await call.message.answer(txt)
    await call.answer()

@dp.callback_query(F.data == "admin_deliver")
async def admin_deliver_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("ابعت رقم الطلب اللي عايز تسلمه (مثال: 5)")
    await state.set_state(DeliverState.waiting_order_id)
    await call.answer()

@dp.message(DeliverState.waiting_order_id)
async def deliver_get_id(message: types.Message, state: FSMContext):
    oid = message.text.strip()
    if oid not in db["orders"]:
        await message.answer("رقم الطلب مش موجود")
        return
    await state.update_data(order_id=oid)
    await message.answer(f"تمام طلب #{oid}\nدلوقتي ابعت الرقم اللي هتسلمه للعميل (مثال: +20123456789\nكود: 12345)")
    await state.set_state(DeliverState.waiting_number)

@dp.message(DeliverState.waiting_number)
async def deliver_get_number(message: types.Message, state: FSMContext):
    data = await state.get_data()
    oid = data["order_id"]
    number_text = message.text
    order = db["orders"][oid]
    order["status"] = "delivered"
    order["delivered_number"] = number_text
    save_db(db)
    try:
        await bot.send_message(order["user_id"], f"✅ **تم تسليم طلبك #{oid}**\n\n📦 {order['country']} - {order['type']}\n\n{number_text}\n\nشكرا لشرائك من متجرنا ❤️")
        await bot.send_message(ORDERS_CHANNEL_ID, f"✅ **تم تسليم طلب #{oid}**\n👤 للعميل: {order['user_id']}\n🌍 {order['country']}")
        await message.answer(f"تم التسليم للعميل {order['user_id']} بنجاح ✅")
    except Exception as e:
        await message.answer(f"حصل خطأ: {e}")
    await state.clear()

@dp.callback_query(F.data == "admin_add_balance")
async def admin_add_balance_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("💳 اضافة رصيد\n\nابعت ايدي العميل اللي عايز تضيفله رصيد (مثال: 123456789)")
    await state.set_state(DeliverState.waiting_add_balance_id)
    await call.answer()

@dp.message(DeliverState.waiting_add_balance_id)
async def add_balance_get_id(message: types.Message, state: FSMContext):
    uid = message.text.strip()
    await state.update_data(target_uid=uid)
    await message.answer(f"تمام العميل {uid}\nدلوقتي ابعت كمية النجوم اللي هتضيفها (مثال: 15)")
    await state.set_state(DeliverState.waiting_add_balance_amount)

@dp.message(DeliverState.waiting_add_balance_amount)
async def add_balance_get_amount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    uid = data["target_uid"]
    try:
        amount = float(message.text.strip())
        if uid not in db["users"]:
            db["users"][uid] = {"balance": 0, "invites": 0, "username": "غير معروف"}
        db["users"][uid]["balance"] += amount
        save_db(db)
        await message.answer(f"✅ تم اضافة {amount} ⭐ للعميل {uid}\nرصيده الحالي: {db['users'][uid]['balance']} ⭐")
        try:
            await bot.send_message(int(uid), f"✅ تم شحن رصيدك بـ {amount} ⭐ بنجاح!\n💳 رصيدك الحالي: {db['users'][uid]['balance']} ⭐\n\nتقدر تشتري دلوقتي من 🛒 شراء حسابات")
        except:
            await message.answer("مقدرتش ابعت رسالة للعميل بس الرصيد اتضاف")
    except Exception as e:
        await message.answer(f"خطأ: {e}")
    await state.clear()

@dp.callback_query(F.data == "admin_stats")
async def admin_stats(call: types.CallbackQuery):
    total_users = len(db["users"])
    total_orders = len(db["orders"])
    pending = len([o for o in db["orders"].values() if o["status"]=="pending"])
    banned_count = len(db.get("banned", []))
    total_balance = sum(u.get("balance",0) for u in db["users"].values())
    txt = f"📊 **احصائيات البوت**\n\n👥 المستخدمين: {total_users}\n📦 الطلبات: {total_orders}\n⏳ المعلقة: {pending}\n🚫 المحظورين: {banned_count}\n💰 اجمالي ارصدة العملاء: {total_balance} ⭐"
    await call.message.answer(txt, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(F.data == "admin_ban")
async def admin_ban_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("🚫 ابعت ايدي المستخدم اللي عايز تحظره")
    await state.set_state(DeliverState.waiting_ban_id)
    await call.answer()

@dp.message(DeliverState.waiting_ban_id)
async def admin_ban_do(message: types.Message, state: FSMContext):
    uid = message.text.strip()
    if uid not in db.get("banned", []):
        db["banned"].append(uid)
        save_db(db)
        await message.answer(f"✅ تم حظر {uid}")
        try:
            await bot.send_message(int(uid), "🚫 تم حظرك من استخدام البوت\nراسل الدعم: " + SUPPORT_USERNAME)
        except: pass
    else:
        await message.answer("المستخدم محظور بالفعل")
    await state.clear()

@dp.callback_query(F.data == "admin_unban")
async def admin_unban_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("✅ ابعت ايدي المستخدم اللي عايز تلغي حظره")
    await state.set_state(DeliverState.waiting_unban_id)
    await call.answer()

@dp.message(DeliverState.waiting_unban_id)
async def admin_unban_do(message: types.Message, state: FSMContext):
    uid = message.text.strip()
    if uid in db.get("banned", []):
        db["banned"].remove(uid)
        save_db(db)
        await message.answer(f"✅ تم الغاء حظر {uid}")
    else:
        await message.answer("المستخدم مش محظور")
    await state.clear()

@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("📢 ابعت رسالة الاذاعة (نص - صورة - فيديو) وهبعتها لكل المستخدمين\n\n⚠️ الرسالة الجاية هتتبعت للكل فورا")
    await state.set_state(DeliverState.waiting_broadcast)
    await call.answer()

@dp.message(DeliverState.waiting_broadcast)
async def admin_broadcast_do(message: types.Message, state: FSMContext):
    users = list(db["users"].keys())
    count = 0
    fail = 0
    await message.answer(f"⏳ جاري الاذاعة لـ {len(users)} مستخدم...")
    for uid in users:
        try:
            await bot.copy_message(chat_id=int(uid), from_chat_id=message.chat.id, message_id=message.message_id)
            count += 1
            await asyncio.sleep(0.05)
        except:
            fail += 1
    await message.answer(f"✅ تمت الاذاعة\n\n✅ وصلت لـ: {count}\n❌ فشلت لـ: {fail}")
    await state.clear()

@dp.callback_query(F.data.startswith("ban_quick_"))
async def ban_quick(call: types.CallbackQuery):
    if call.from_user.id!= ADMIN_ID: return
    uid = call.data.replace("ban_quick_", "")
    if uid not in db.get("banned", []):
        db["banned"].append(uid)
        save_db(db)
        await call.message.edit_text(call.message.text + f"\n\n🚫 تم حظره", parse_mode="Markdown")
        await call.answer("تم حظر المستخدم")
    else:
        await call.answer("محظور بالفعل")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

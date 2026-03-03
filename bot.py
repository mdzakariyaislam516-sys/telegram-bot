import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ================== CONFIG ==================
TOKEN = "8657812226:AAEMVD7GrSZSTuK91tr-zHAlz0vyGMcGuz0"
ADMIN_GROUP = -1003058363661

bot = telebot.TeleBot(TOKEN)

pending_amount = {}    # user → binance/bybit/bitget
user_amount = {}       # user → amount
user_rate = {}         # user → rate (122/123)
user_total = {}        # user → total


# ================== MAIN MENU ==================
def main_menu(chat_id):
    menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = KeyboardButton("💵 Dollar Buy/Sell")
    btn2 = KeyboardButton("🧑‍💻 Support")
    btn3 = KeyboardButton("📢 Support Channel")
    menu.add(btn1, btn2, btn3)
    bot.send_message(chat_id, "আপনি কী করতে চান? নিচের মেনু থেকে নির্বাচন করুন।", reply_markup=menu)


@bot.message_handler(commands=['start'])
def start(message):
    main_menu(message.chat.id)


# ================== BUY / SELL ==================
@bot.message_handler(func=lambda msg: msg.text == "💵 Dollar Buy/Sell")
def buy_sell_menu(message):
    menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    b1 = KeyboardButton("ডলার কিনতে চাই")
    b2 = KeyboardButton("ডলার বিক্রি করতে চাই")
    menu.add(b1, b2)
    bot.send_message(message.chat.id, "নিচের যেকোনো একটি অপশন নির্বাচন করুন:", reply_markup=menu)


@bot.message_handler(func=lambda msg: msg.text == "ডলার কিনতে চাই")
def buy_closed(message):
    menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    menu.add(KeyboardButton("🔙 Back"), KeyboardButton("🏠 Main Menu"))
    bot.send_message(
        message.chat.id,
        "বর্তমানে বট থেকে ডলার ক্রয় বন্ধ আছে 💔\nআপনি চাইলে ডলার বিক্রয় করতে পারেন।",
        reply_markup=menu
    )


@bot.message_handler(func=lambda msg: msg.text == "🔙 Back")
def back(message):
    buy_sell_menu(message)


@bot.message_handler(func=lambda msg: msg.text == "🏠 Main Menu")
def home(message):
    main_menu(message.chat.id)


# ================== SELL OPTIONS ==================
@bot.message_handler(func=lambda msg: msg.text == "ডলার বিক্রি করতে চাই")
def sell_options(message):

    # reply keyboard
    reply = ReplyKeyboardMarkup(resize_keyboard=True)
    reply.add(KeyboardButton("🔙 Back"))

    bot.send_message(message.chat.id, "আপনার ডলার কোথায় আছে সিলেক্ট করুন:", reply_markup=reply)

    inline = InlineKeyboardMarkup()
    inline.add(
        InlineKeyboardButton("Binance", callback_data="binance"),
        InlineKeyboardButton("Bybit", callback_data="bybit")
    )
    inline.add(
        InlineKeyboardButton("Bitget", callback_data="bitget"),
        InlineKeyboardButton("Xrocket", callback_data="xrocket")
    )

    bot.send_message(message.chat.id, "👇 নিচের অপশন থেকে নির্বাচন করুন:", reply_markup=inline)


# ================== INLINE HANDLER ==================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    cid = call.message.chat.id

    # ============= XROCKET =============
    if call.data == "xrocket":
        bot.send_message(cid, "Xrocket sell করার জন্য যোগাযোগ করুন:\n@Online_Jobs_24hours")
        return

    # ============= CHOOSE METHOD =============
    if call.data in ["binance", "bybit", "bitget"]:
        pending_amount[cid] = call.data

        reply = ReplyKeyboardMarkup(resize_keyboard=True)
        reply.add(KeyboardButton("🔙 Back"))

        bot.send_message(
            cid,
            "👉আপনার ডলারের সঠিক পরিমাণ লিখুন।যেমনঃ 0.3, 0.05, 1, 2 ইত্যাদি শুধুমাত্র সংখ্যা লিখবেন\n\n⚠️ 3.5 ডলারের নিচে যেকোনো এমাউন্ট 122 টাকা করে হিসাব হবে।\n⚠️ 3.5 এর বেশি হলে 123 টাকা করে হিসাব হবে।",
            reply_markup=reply
        )
        bot.register_next_step_handler_by_chat_id(cid, calculate_amount)
        return

    # ============= PAYMENT OPTIONS =============
    if call.data == "pm_bkash":
        bot.send_message(cid, "আপনার বিকাশ নাম্বারটি লিখুনঃ")
        bot.register_next_step_handler_by_chat_id(cid, save_bkash)

    elif call.data == "pm_nagad":
        bot.send_message(cid, "আপনার নগদ নাম্বারটি লিখুনঃ")
        bot.register_next_step_handler_by_chat_id(cid, save_nagad)

    elif call.data == "pm_roket":
        bot.send_message(cid, "আপনার রকেট নাম্বারটি লিখুনঃ")
        bot.register_next_step_handler_by_chat_id(cid, save_roket)


# ================== CALCULATE AMOUNT ==================
def calculate_amount(message):
    cid = message.chat.id

    # Back
    if message.text == "🔙 Back":
        sell_options(message)
        return

    try:
        amount = float(message.text)
    except:
        bot.send_message(cid, "সঠিক সংখ্যা লিখুন!")
        bot.register_next_step_handler_by_chat_id(cid, calculate_amount)
        return

    rate = 122 if amount < 3.5 else 123
    total = amount * rate

    # save
    user_amount[cid] = amount
    user_rate[cid] = rate
    user_total[cid] = total

    bot.send_message(cid, f"আপনার প্রাপ্ত টাকা হবে: **{total} টাকা**", parse_mode="Markdown")

    method = pending_amount.get(cid)

    if method == "binance":
        uid = "`774896980`"
    elif method == "bybit":
        uid = "`510385821`"
    elif method == "bitget":
        uid = "`4952119040`"
    else:
        uid = "`Unknown`"

    bot.send_message(
        cid,
        f"নিচের UID তে ডলার পাঠান:\n\n{uid}\n\nএরপর স্ক্রিনশট পাঠান।",
        parse_mode="Markdown"
    )

    reply = ReplyKeyboardMarkup(resize_keyboard=True)
    reply.add(KeyboardButton("🔙 Back"))

    bot.send_message(cid, "স্ক্রিনশট পাঠান:", reply_markup=reply)
    bot.register_next_step_handler_by_chat_id(cid, receive_screenshot)


# ================== RECEIVE SCREENSHOT ==================
def receive_screenshot(message):

    # BACK button
    if message.text == "🔙 Back":
        sell_options(message)
        return

    if message.content_type != "photo":
        bot.send_message(message.chat.id, "দয়া করে স্ক্রিনশট পাঠান অথবা 🔙 Back চাপুন")
        bot.register_next_step_handler_by_chat_id(message.chat.id, receive_screenshot)
        return

    cid = message.chat.id

    # Forward screenshot
    bot.forward_message(ADMIN_GROUP, cid, message.message_id)

    # Forward formula
    amount = user_amount.get(cid)
    rate = user_rate.get(cid)
    total = user_total.get(cid)

    if amount is not None:
        calc_text = f"{amount} * {rate} = {total}"
        bot.send_message(ADMIN_GROUP, f"📌 হিসাব:\n{calc_text}")

    # Payment options
    inline = InlineKeyboardMarkup()
    inline.add(
        InlineKeyboardButton("বিকাশ", callback_data="pm_bkash"),
        InlineKeyboardButton("নগদ", callback_data="pm_nagad"),
        InlineKeyboardButton("রকেট", callback_data="pm_roket")
    )

    bot.send_message(message.chat.id, "আপনি কিসের মাধ্যমে পেমেন্ট নিতে চান?", reply_markup=inline)


# ================== SAVE PAYMENT NUMBERS ==================
def save_bkash(message):
    bot.send_message(ADMIN_GROUP, f"📩 বিকাশ = {message.text}")
    confirm_done(message)


def save_nagad(message):
    bot.send_message(ADMIN_GROUP, f"📩 নগদ = {message.text}")
    confirm_done(message)


def save_roket(message):
    bot.send_message(ADMIN_GROUP, f"📩 রকেট = {message.text}")
    confirm_done(message)


# ================== FINAL CONFIRM ==================
def confirm_done(message):
    bot.send_message(
        message.chat.id,
        "আপনার রিকুয়েস্টটি সঠিকভাবে গ্রহণ করা হয়েছে।\nঅনুগ্রহ করে অপেক্ষা করুন।\n১০ মিনিটের মধ্যে পেমেন্ট না পেলে সাপোর্টে যোগাযোগ করুন।"
    )
    main_menu(message.chat.id)


# ================== ADMIN → USER REPLY ==================
@bot.message_handler(content_types=['text'], chat_types=['group', 'supergroup'])
def admin_reply(message):

    if message.reply_to_message and message.reply_to_message.forward_from:
        user_id = message.reply_to_message.forward_from.id

        bot.send_message(user_id, f"💬 Admin:\n{message.text}")


# ================== SUPPORT ==================
@bot.message_handler(func=lambda msg: msg.text == "🧑‍💻 Support")
def support(message):
    bot.send_message(message.chat.id, "যেকোনো প্রয়োজনে সাপোর্টে নক করুন। ধন্যবাদ🥀: @Online_Jobs_24hours")


@bot.message_handler(func=lambda msg: msg.text == "📢 Support Channel")
def channel(message):
    bot.send_message(message.chat.id, "আমাদের সাপোর্ট চ্যানেল🥰 জয়েন করতে ভুলবেন না। আশা করি সব সময় সাপোর্ট দিয়ে পাশে থাকবেন। ধন্যবাদ🥰🥀: https://t.me/Online_small_jobs")


# ================== RUN BOT ==================
bot.infinity_polling()

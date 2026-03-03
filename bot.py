import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ================== CONFIG ==================
TOKEN = "8657812226:AAEMVD7GrSZSTuK91tr-zHAlz0vyGMcGuz0"
ADMIN_GROUP = -1003058363661   # এখানে তোমার গ্রুপ ID বসবে

bot = telebot.TeleBot(TOKEN)


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
    bot.send_message(message.chat.id, "নিচের অপশন নির্বাচন করুন:", reply_markup=menu)


@bot.message_handler(func=lambda msg: msg.text == "ডলার কিনতে চাই")
def buy_closed(message):
    menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    menu.add(KeyboardButton("🔙 Back"), KeyboardButton("🏠 Main Menu"))

    bot.send_message(
        message.chat.id,
        "বর্তমানে ডলার ক্রয় বন্ধ আছে 💔\nআপনি চাইলে ডলার বিক্রয় করতে পারেন।",
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
    inline = InlineKeyboardMarkup()
    inline.add(
        InlineKeyboardButton("Binance", callback_data="binance"),
        InlineKeyboardButton("Bybit", callback_data="bybit")
    )
    inline.add(
        InlineKeyboardButton("Bitget", callback_data="bitget"),
        InlineKeyboardButton("xrocket", callback_data="xrocket")
    )

@bot.message_handler(func=lambda msg: msg.text == "ডলার বিক্রি করতে চাই")
def buy_closed(message):
    menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    menu.add(KeyboardButton("🔙 Back"))
  
    bot.send_message(message.chat.id, "আপনার ডলার কোথায় আছে সিলেক্ট করুন:", reply_markup=inline)

# ================== INLINE HANDLER ==================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id

    # ------- BINANCE -------
    if call.data == "binance":
        bot.send_message(
            chat_id,
            "নিম্নোক্ত Binance UID তে ডলার পাঠান:\n\n`Binance UID: 774896980`\n\nসেন্ড করে স্ক্রিনশট পাঠান।",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler_by_chat_id(chat_id, receive_screenshot)

    # ------- BYBIT -------
    elif call.data == "bybit":
        bot.send_message(
            chat_id,
            "Bybit UID:\n\n`510385821`\n\nসেন্ড করে স্ক্রিনশট পাঠান।",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler_by_chat_id(chat_id, receive_screenshot)

    # ------- BITGET -------
    elif call.data == "bitget":
        bot.send_message(
            chat_id,
            "Bitget UID:\n\n`4952119040`\n\nসেন্ড করে স্ক্রিনশট পাঠান।",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler_by_chat_id(chat_id, receive_screenshot)

    # ------- XROCKET -------
    elif call.data == "xrocket":
        bot.send_message(chat_id, "Xrocket sell করার জন্য যোগাযোগ করুন:\n@Online_Jobs_24hours")

    # ------- PAYMENT METHODS -------
    elif call.data == "pm_bkash":
        bot.send_message(chat_id, "আপনার বিকাশ নাম্বারটি লিখুনঃ")
        bot.register_next_step_handler_by_chat_id(chat_id, save_bkash)

    elif call.data == "pm_nagad":
        bot.send_message(chat_id, "আপনার নগদ নাম্বারটি লিখুনঃ")
        bot.register_next_step_handler_by_chat_id(chat_id, save_nagad)

    elif call.data == "pm_roket":
        bot.send_message(chat_id, "আপনার রকেট নাম্বারটি লিখুনঃ")
        bot.register_next_step_handler_by_chat_id(chat_id, save_roket)


# ================== RECEIVE SCREENSHOT ==================
def receive_screenshot(message):

    if message.content_type != "photo":
        bot.send_message(message.chat.id, "দয়া করে স্ক্রিনশট পাঠান।")
        bot.register_next_step_handler_by_chat_id(message.chat.id, receive_screenshot)
        return

    # Forward to admin group
    bot.forward_message(ADMIN_GROUP, message.chat.id, message.message_id)

    # Ask for payment method
    inline = InlineKeyboardMarkup()
    inline.add(
        InlineKeyboardButton("বিকাশ", callback_data="pm_bkash"),
        InlineKeyboardButton("নগদ", callback_data="pm_nagad"),
        InlineKeyboardButton("রকেট", callback_data="pm_roket")
    )

    bot.send_message(
        message.chat.id,
        "আপনি কিসে পেমেন্ট নিতে চান?",
        reply_markup=inline
    )


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
        "আপনার রিকুয়েস্টটি সঠিকভাবে গ্রহণ করা হয়েছে।\n"
        "অনুগ্রহ করে অপেক্ষা করুন।\n"
        "১০ মিনিটের মধ্যে পেমেন্ট না পেলে সাপোর্টে যোগাযোগ করুন।"
    )
    main_menu(message.chat.id)


# ================== ADMIN → USER REPLY ==================
@bot.message_handler(content_types=['text'], chat_types=['group', 'supergroup'])
def admin_reply(message):

    if message.reply_to_message and message.reply_to_message.forward_from:
        user_id = message.reply_to_message.forward_from.id

        bot.send_message(
            user_id,
            f"💬 Admin:\n{message.text}"
        )


# ================== SUPPORT BUTTONS ==================
@bot.message_handler(func=lambda msg: msg.text == "🧑‍💻 Support")
def support(message):
    bot.send_message(message.chat.id, "সাপোর্ট: @Online_Jobs_24hours")


@bot.message_handler(func=lambda msg: msg.text == "📢 Support Channel")
def channel(message):
    bot.send_message(message.chat.id, "চ্যানেল: https://t.me/Online_small_jobs")


# ================== RUN BOT ==================
bot.infinity_polling()

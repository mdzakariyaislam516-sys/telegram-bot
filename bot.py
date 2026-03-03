import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8657812226:AAEMVD7GrSZSTuK91tr-zHAlz0vyGMcGuz0"
ADMIN_GROUP = -1003058363661   # Screenshot যাবে এই গ্রুপে

bot = telebot.TeleBot(TOKEN)

# =========================== MAIN MENU ==============================

def main_menu(chat_id):
    menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = KeyboardButton("💵 Dollar Buy/Sell")
    btn2 = KeyboardButton("🧑‍💻 Support")
    btn3 = KeyboardButton("📢 Support Channel")
    menu.add(btn1, btn2, btn3)
    bot.send_message(chat_id, "আপনি কী করতে চান? মেনু থেকে সিলেক্ট করুন", reply_markup=menu)


@bot.message_handler(commands=['start'])
def start(message):
    main_menu(message.chat.id)

# ======================= BUY / SELL SECTION =========================

@bot.message_handler(func=lambda msg: msg.text == "💵 Dollar Buy/Sell")
def buy_sell_menu(message):
    menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    b1 = KeyboardButton("ডলার কিনতে চাই")
    b2 = KeyboardButton("ডলার বিক্রি করতে চাই")
    menu.add(b1, b2)
    bot.send_message(message.chat.id, "নিচের মেনু থেকে সঠিক তথ্য নির্বাচন করুন।", reply_markup=menu)

# -------------------- 1.A BUY NOT AVAILABLE -------------------------

@bot.message_handler(func=lambda msg: msg.text == "ডলার কিনতে চাই")
def buy_closed(message):
    menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    back = KeyboardButton("🔙 Back")
    home = KeyboardButton("🏠 Main Menu")
    menu.add(back, home)

    bot.send_message(
        message.chat.id,
        "বট থেকে বর্তমানে ডলার ক্রয় বন্ধ আছে।\nতবে আপনি চাইলে ডলার বিক্রয় করতে পারেন।",
        reply_markup=menu
    )

# -------------------- BACK / MAIN MENU ------------------------------

@bot.message_handler(func=lambda msg: msg.text == "🔙 Back")
def go_back(message):
    buy_sell_menu(message)

@bot.message_handler(func=lambda msg: msg.text == "🏠 Main Menu")
def go_home(message):
    main_menu(message.chat.id)

# -------------------- 1.B SELL SYSTEM -------------------------------

@bot.message_handler(func=lambda msg: msg.text == "ডলার বিক্রি করতে চাই")
def sell_options(message):

    inline = InlineKeyboardMarkup()
    b1 = InlineKeyboardButton("Binance", callback_data="binance")
    b2 = InlineKeyboardButton("Bybit", callback_data="bybit")
    b3 = InlineKeyboardButton("Bitget", callback_data="bitget")
    b4 = InlineKeyboardButton("Xrocket", callback_data="xrocket")
    inline.add(b1, b2)
    inline.add(b3, b4)

    bot.send_message(
        message.chat.id,
        "আপনার ডলার কিসে আছে সিলেক্ট করুন:",
        reply_markup=inline
    )

# ===================== INLINE BUTTON HANDLER ========================

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):

    chat_id = call.message.chat.id

    # ---------- BINANCE ----------
    if call.data == "binance":
        bot.send_message(
            chat_id,
            "নিম্নলিখিত Binance UID তে ডলার সেন্ড করুন:\n"
            "```\nBinance UID: 774896980\n```\n\n"
            "ডলার দেওয়ার আগে অবশ্যই রিয়্যাল আইডি চেক করে নিবেন ❤️‍🩹\n\n"
            "সেন্ড করা হয়ে গেলে স্ক্রিনশট পাঠান।",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler_by_chat_id(chat_id, receive_screenshot)

    # ---------- BYBIT ----------
    elif call.data == "bybit":
        bot.send_message(
            chat_id,
            "নিম্নলিখিত Bybit UID তে ডলার সেন্ড করুন:\n"
            "```\nBybit UID: 510385821\n```\n\n"
            "সেন্ড করা হয়ে গেলে স্ক্রিনশট পাঠান।",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler_by_chat_id(chat_id, receive_screenshot)

    # ---------- BITGET ----------
    elif call.data == "bitget":
        bot.send_message(
            chat_id,
            "নিম্নলিখিত Bitget UID তে ডলার সেন্ড করুন:\n"
            "```\nBitget UID: 4952119040\n```\n\n"
            "সেন্ড করা হয়ে গেলে স্ক্রিনশট পাঠান।",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler_by_chat_id(chat_id, receive_screenshot)

    # ---------- XROCKET ----------
    elif call.data == "xrocket":
        bot.send_message(
            chat_id,
            "Xrocket Dollar sell করার জন্য সরাসরি এডমিনের সাথে যোগাযোগ করুন:\n@Online_Jobs_24hours"
        )

# ===================== SCREENSHOT RECEIVE ===========================

def receive_screenshot(message):

    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "দয়া করে স্ক্রিনশট পাঠান।")
        bot.register_next_step_handler_by_chat_id(message.chat.id, receive_screenshot)
        return

    # Forward to admin group
    bot.forward_message(ADMIN_GROUP, message.chat.id, message.message_id)

    # Confirmation to user
    bot.send_message(
        message.chat.id,
        "আপনার রিকুয়েস্টটি সঠিকভাবে গ্রহণ করা হয়েছে।\n"
        "অনুগ্রহ করে অপেক্ষা করুন।\n"
        "১০ মিনিটের মধ্যে টাকা না পেলে সাপোর্টে যোগাযোগ করুন।"
    )

    # Back to main menu
    main_menu(message.chat.id)

# ===================== SUPPORT / SUPPORT CHANNEL ====================

@bot.message_handler(func=lambda msg: msg.text == "🧑‍💻 Support")
def support(message):
    bot.send_message(message.chat.id, "সাপোর্ট: @your_support")

@bot.message_handler(func=lambda msg: msg.text == "📢 Support Channel")
def channel(message):
    bot.send_message(message.chat.id, "চ্যানেল: https://t.me/your_channel")

# ===================== RUN BOT =====================================

bot.infinity_polling()

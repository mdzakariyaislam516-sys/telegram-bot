import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import datetime

# ================== CONFIG ==================
TOKEN = "8657812226:AAEMVD7GrSZSTuK91tr-zHAlz0vyGMcGuz0"
ADMIN_GROUP = -1003058363661

bot = telebot.TeleBot(TOKEN)

pending_amount = {}
user_amount = {}
user_rate = {}
user_total = {}
user_pending = {}
user_screenshot = {}
user_name = {}
user_method = {}
user_stage = {}
message_user_map = {}
orders = {}
stage_history = {}

def set_stage(cid, stage):

    if cid not in stage_history:
        stage_history[cid] = []

    # আগের stage save করো
    if cid in user_stage:
        stage_history[cid].append(user_stage[cid])

    user_stage[cid] = stage

# ================== MAIN MENU ==================
def main_menu(chat_id):

    set_stage(chat_id, "main_menu")

    menu = ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)

    btn1 = KeyboardButton("💵 Dollar Buy/Sell")
    btn2 = KeyboardButton("🧑‍💻 Support")
    btn3 = KeyboardButton("📢 Support Channel")
    btn4 = KeyboardButton("🌟বিকাশ নগদ পেমেন্ট রুলস")

    menu.add(btn1,btn2,btn3,btn4)

    bot.send_message(chat_id,"আপনি কী করতে চান? নিচের মেনু থেকে নির্বাচন করুন।\n\n অর্ডার করার আগে অবশ্যই বিকাশ নগদ পেমেন্ট রুলস দেখে নিবেন। ধন্যবাদ🥀",reply_markup=menu)

@bot.message_handler(commands=['start'])
def start(message):

    cid = message.chat.id

    # history reset
    stage_history[cid] = []

    main_menu(cid)

# ================== BUY SELL ==================
@bot.message_handler(func=lambda msg: msg.text == "💵 Dollar Buy/Sell")
def buy_sell_menu(message):

    set_stage(message.chat.id, "buy_sell")

    menu = ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)

    b1 = KeyboardButton("ডলার কিনতে চাই")
    b2 = KeyboardButton("ডলার বিক্রি করতে চাই")
    b3 = KeyboardButton("🔙 Back")

    menu.add(b1,b2,b3)

    bot.send_message(message.chat.id,"নিচের যেকোনো একটি অপশন নির্বাচন করুন:",reply_markup=menu)

@bot.message_handler(func=lambda msg: msg.text == "ডলার কিনতে চাই")
def buy_closed(message):

    menu = ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    menu.add(KeyboardButton("🔙 Back"),KeyboardButton("🏠 Main Menu"))

    bot.send_message(message.chat.id,"বর্তমানে বট থেকে ডলার ক্রয় বন্ধ আছে 💔\nআপনি চাইলে ডলার বিক্রয় করতে পারেন।",reply_markup=menu)

# ================== BACK ==================
@bot.message_handler(func=lambda msg: msg.text == "🔙 Back")
def back(message):

    cid = message.chat.id
    bot.clear_step_handler_by_chat_id(cid)

    # যদি history না থাকে → main menu
    if cid not in stage_history or len(stage_history[cid]) == 0:
        main_menu(cid)
        return

    # আগের stage বের করো
    prev_stage = stage_history[cid].pop()
    user_stage[cid] = prev_stage

    # ===== REDIRECT BASED ON STAGE =====

    if prev_stage == "main_menu":
        main_menu(cid)

    elif prev_stage == "buy_sell":
        buy_sell_menu(message)

    elif prev_stage == "sell_menu":
        sell_options(message)

    elif prev_stage == "amount_input":
        set_stage(cid, "amount_input")
        bot.send_message(cid, "আবার amount লিখুন:")
        bot.register_next_step_handler_by_chat_id(cid, calculate_amount)

    elif prev_stage == "screenshot":
        set_stage(cid, "screenshot")
        bot.send_message(cid, "আবার স্ক্রিনশট পাঠান:")
        bot.register_next_step_handler_by_chat_id(cid, receive_screenshot)

    else:
        main_menu(cid)

@bot.message_handler(func=lambda msg: msg.text == "🏠 Main Menu")
def home(message):
    main_menu(message.chat.id)

# ================== SELL OPTIONS ==================
@bot.message_handler(func=lambda msg: msg.text == "ডলার বিক্রি করতে চাই")
def sell_options(message):

    set_stage(message.chat.id, "sell_menu")

    reply = ReplyKeyboardMarkup(resize_keyboard=True)
    reply.add(KeyboardButton("🔙 Back"))

    bot.send_message(message.chat.id,"আপনার ডলার কোথায় আছে সিলেক্ট করুন:",reply_markup=reply)

    inline = InlineKeyboardMarkup()

    inline.add(
        InlineKeyboardButton("Binance",callback_data="binance"),
        InlineKeyboardButton("Bybit",callback_data="bybit")
    )

    inline.add(
        InlineKeyboardButton("Bitget",callback_data="bitget"),
        InlineKeyboardButton("Xrocket",callback_data="xrocket")
    )

    inline.add(
    InlineKeyboardButton("BEP-20", callback_data="BEP-20"),
    InlineKeyboardButton("Polygon", callback_data="Polygon")
)


    bot.send_message(message.chat.id,"👇 নিচের অপশন থেকে নির্বাচন করুন:",reply_markup=inline)

# ================== INLINE HANDLER ==================
@bot.callback_query_handler(func=lambda call: call.data not in ["pm_bkash","pm_nagad","pm_roket"])
def callback_handler(call):

    cid = call.message.chat.id

    # ===== PAYMENT DONE =====
    if call.data.startswith("done_"):

        uid = int(call.data.split("_")[1])

        if uid not in user_pending:
            bot.answer_callback_query(call.id,"⚠️ Already done")
            return

        order = orders.get(uid, {})

        amount = order.get("amount")
        total = order.get("total")
        method = order.get("method")
        number = order.get("number")
        network = order.get("network")

        username = user_name.get(uid,"Unknown")

        time_now = (datetime.datetime.utcnow() + datetime.timedelta(hours=6)).strftime("%H:%M")

        bot.send_message(
            uid,
            f"""💰 Payment Completed

Amount: {total} BDT
Method: {method}

⏰ Time: {time_now}
📌 Status: Successful

ধন্যবাদ আমাদের সাথে লেনদেন করার জন্য ❤️"""
        )

        bot.edit_message_caption(
f"""💰 Payment Completed

👤 User: {username}
🌐 Network: {network}
🆔 User ID: {uid}

💵 Amount: {amount} USDT
💸 Total: {total} BDT
💳 Method: {method}
📱 Number: {number}
📌 Status: Successful
⏰ Time: {time_now}""",
        call.message.chat.id,
        call.message.message_id
)

        user_pending.pop(uid)

        bot.answer_callback_query(call.id,"✅ Done")
        return

# ===== PAYMENT REJECT =====
    if call.data.startswith("reject_"):

        uid = int(call.data.split("_")[1])

        if uid not in user_pending:
            bot.answer_callback_query(call.id,"⚠️ Already processed")
            return

        username = user_name.get(uid,"Unknown")
        order = orders.get(uid, {})

        amount = order.get("amount")
        total = order.get("total")
        method = order.get("method")
        number = order.get("number")
        network = order.get("network")

        time_now = (datetime.datetime.utcnow() + datetime.timedelta(hours=6)).strftime("%H:%M")

        bot.send_message(
            uid,
            """❌ Payment Rejected

আপনার পাঠানো স্ক্রিনশট টি সঠিক নয় তাই পেমেন্ট রিজেক্ট করা হয়েছে।

অনুগ্রহ করে সাপোর্টে যোগাযোগ করুন।

ধন্যবাদ🥀"""
        )

        bot.edit_message_caption(
f"""❌ Payment Rejected

👤 User: {username}
🌐 Network: {network}
🆔 User ID: {uid}

💵 Amount: {amount} USDT
💸 Total: {total} BDT
💳 Method: {method}
📱 Number: {number}

📌 Status: Rejected
⏰ Time: {time_now}""",
        call.message.chat.id,
        call.message.message_id
)

        user_pending.pop(uid)

        bot.answer_callback_query(call.id,"❌ Rejected")
        return

    if call.data == "xrocket":
        bot.send_message(cid,"Xrocket ডলার sell করার জন্য সরাসরি এডমিনের সাথে যোগাযোগ করুন:\n@Online_Jobs_24hours")
        return

    if call.data in ["binance","bybit","bitget","BEP-20","Polygon"]:

        pending_amount[cid] = call.data
        set_stage(cid, "amount_input")

        reply = ReplyKeyboardMarkup(resize_keyboard=True)
        reply.add(KeyboardButton("🔙 Back"))

        bot.send_message(
            cid,
            "👉আপনার ডলারের সঠিক পরিমাণ লিখুন\n\n⚠️ যেমনঃ 0.05, 0.5, 1, 2\n⚠️ শুধুমাত্র সংখ্যা লিখবেন",
            reply_markup=reply
        )

        bot.register_next_step_handler_by_chat_id(cid,calculate_amount)

# ================== CALCULATE ==================
def calculate_amount(message):

    cid = message.chat.id

    if message.text == "🔙 Back":
        back(message)
        return

    try:
        amount = float(message.text)
    except:
        bot.send_message(cid,"সঠিক সংখ্যা লিখুন")
        bot.register_next_step_handler_by_chat_id(cid,calculate_amount)
        return

    rate = 122.5 if amount < 3.5 else 123
    total = int(amount * rate)

    user_amount[cid] = amount
    user_rate[cid] = rate
    user_total[cid] = total

    bot.send_message(cid,f"আপনার টোটাল টাকার পরিমাণ হলো: {total} টাকা")

    method = pending_amount.get(cid)

    if method == "binance":
        uid = "`774896980`"

    elif method == "bybit":
        uid = "`510385821`"

    elif method == "bitget":
        uid = "`4952119040`"

    elif method == "BEP-20":
        uid = "`0x2afdf7b462397e4a901472763e2848d2b85468f0`"

    elif method == "Polygon":
        uid = "`0x2afdf7b462397e4a901472763e2848d2b85468f0`"

    else:
        uid = "`Unknown`"

    bot.send_message(
        cid,
        f"নিচের UID তে ডলার পাঠান\n\n{uid}\n\nএরপর স্ক্রিনশট সেন্ড করুন",
        parse_mode="Markdown"
    )

    reply = ReplyKeyboardMarkup(resize_keyboard=True)
    reply.add(KeyboardButton("🔙 Back"))

    set_stage(cid, "screenshot")

    bot.send_message(cid,"স্ক্রিনশট পাঠান:",reply_markup=reply)

    bot.register_next_step_handler_by_chat_id(cid,receive_screenshot)

# ================== SCREENSHOT ==================
def receive_screenshot(message):

    cid = message.chat.id

    if message.text == "🔙 Back":
        bot.clear_step_handler_by_chat_id(cid)
        set_stage(cid, "amount_input")
        bot.send_message(cid,"আবার amount লিখুন:")
        bot.register_next_step_handler_by_chat_id(cid, calculate_amount)
        return

    if message.content_type != "photo":
        bot.send_message(cid,"স্ক্রিনশট পাঠান")
        bot.register_next_step_handler_by_chat_id(cid,receive_screenshot)
        return

    user_screenshot[cid] = message.photo[-1].file_id

    inline = InlineKeyboardMarkup()

    inline.add(
        InlineKeyboardButton("বিকাশ",callback_data="pm_bkash"),
        InlineKeyboardButton("নগদ",callback_data="pm_nagad"),
        InlineKeyboardButton("রকেট",callback_data="pm_roket")
    )

    bot.send_message(cid,"আপনি কিসে পেমেন্ট নিতে চান?",reply_markup=inline)

# ================== PAYMENT OPTIONS ==================
@bot.callback_query_handler(func=lambda call: call.data in ["pm_bkash","pm_nagad","pm_roket"])
def payment_method(call):

    cid = call.message.chat.id

    if call.data == "pm_bkash":
        user_method[cid] = "Bkash"
        bot.send_message(cid,"আপনার বিকাশ নাম্বার লিখুন")
        bot.register_next_step_handler_by_chat_id(cid,save_number)

    elif call.data == "pm_nagad":
        user_method[cid] = "Nagad"
        bot.send_message(cid,"আপনার নগদ নাম্বার লিখুন")
        bot.register_next_step_handler_by_chat_id(cid,save_number)

    elif call.data == "pm_roket":
        user_method[cid] = "Rocket"
        bot.send_message(cid,"আপনার রকেট নাম্বার লিখুন")
        bot.register_next_step_handler_by_chat_id(cid,save_number)

# ================== SAVE PAYMENT ==================
def save_number(message):

    cid = message.chat.id
    number = message.text

    amount = user_amount.get(cid)
    rate = user_rate.get(cid)
    total = user_total.get(cid)
    method = user_method.get(cid)
    network = pending_amount.get(cid)

    orders[cid] = {
        "amount": amount,
        "rate": rate,
        "total": total,
        "method": method,
        "number": number,
        "network": network
    }

    user = message.from_user
    username = f"@{user.username}" if user.username else user.first_name
    user_name[cid] = username

    caption = (
        f"📥 New Sell Request\n"
        f"👤 User: {username}\n"
        f"🌐 Network: {network}\n"
        f"🆔 User ID: {cid}\n\n"
        f"💵 Amount: {amount} USDT\n"
        f"💰 Rate: {rate}\n"
        f"💸 Total: {total} BDT\n"
        f"💳 Payment: {method}\n"
        f"📱 Number: {number}\n"
        f"📌 Status: Pending"
    )

    admin_buttons = InlineKeyboardMarkup()

    admin_buttons.add(
              InlineKeyboardButton("✅ Payment Done",callback_data=f"done_{cid}"),
              InlineKeyboardButton("❌ Reject",callback_data=f"reject_{cid}")
)

    msg = bot.send_photo(
        ADMIN_GROUP,
        user_screenshot[cid],
        caption=caption,
        reply_markup=admin_buttons
    )

    user_pending[cid] = msg.message_id
    message_user_map[msg.message_id] = cid

    bot.send_message(cid,"আপনার রিকুয়েস্ট টি সঠিকভাবে গ্রহণ করা হয়েছে। অনুগ্রহ করে অপেক্ষা করুন। ১০ মিনিটের মধ্যে পেমেন্ট না পেলে সাপোর্টে যোগাযোগ করুন। ধন্যবাদ🥰🥀\n\nআমাদের সাপোর্ট চ্যানেল\n👉 https://t.me/Online_small_jobs")
    main_menu(cid)

# ================== ADMIN REPLY ==================
@bot.message_handler(func=lambda message: message.chat.id == ADMIN_GROUP)
def admin_reply(message):

    if message.reply_to_message:

        text = message.reply_to_message.caption or ""

        if "User ID:" in text or "User ID" in text:

            try:

                if "User ID:" in text:
                    user_id = int(text.split("User ID:")[1].split("\n")[0].strip())

                else:
                    user_id = int(text.split("User ID")[1].split("\n")[0].strip())

                bot.send_message(
                    user_id,
                    f"💬 Admin Reply:\n\n{message.text}"
                )

            except Exception as e:
                     print("Admin reply error:", e)

# ================== SUPPORT ==================
@bot.message_handler(func=lambda msg: msg.text == "🧑‍💻 Support")
def support(message):
    bot.send_message(message.chat.id,"যেকোনো প্রয়োজনে সাপোর্টে নক করুন: @Online_Jobs_24hours")

@bot.message_handler(func=lambda msg: msg.text == "📢 Support Channel")
def channel(message):
    bot.send_message(message.chat.id,"সাপোর্ট চ্যানেল: https://t.me/Online_small_jobs")

@bot.message_handler(func=lambda msg: msg.text == "🌟বিকাশ নগদ পেমেন্ট রুলস")
def rules(message):
    bot.send_message(message.chat.id,"⚠️বিকাশে পেমেন্ট নেওয়ার জন্য অবশ্যই বিকাশ পার্সোনাল নাম্বার দিতে হবে\n\n⚠️ নগদে ১০০ টাকার নিচে পেমেন্ট নিতে হলে সেন্ড মানি ফি ৫ টাকা কেটে নেওয়া হবে। তবে ১০০ টাকার উপরে সেন্ড মানি ফি নাই। ধন্যবাদ🥰🥀")


# ================== RUN ==================
bot.infinity_polling()

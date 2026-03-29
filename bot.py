import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import datetime

# ================== CONFIG ==================
TOKEN = "8657812226:AAEMVD7GrSZSTuK91tr-zHAlz0vyGMcGuz0"
ADMIN_GROUP = -1003058363661
ADMIN_ID = 7114259913
PROOF_CHANNEL = -1003417566709
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
all_users = set()
proof_messages = {}
first_name = {}
exchange_data = {}
try:
    with open("users.txt", "r") as f:
        users_cache = set(int(x) for x in f.read().splitlines())
except:
    users_cache = set()

def save_user(user_id):
    if user_id in users_cache:
        return

    users_cache.add(user_id)

    with open("users.txt", "a") as f:
        f.write(str(user_id) + "\n")

def set_stage(cid, stage):

    if cid not in stage_history:
        stage_history[cid] = []

    if cid in user_stage and user_stage[cid] != stage:
        stage_history[cid].append(user_stage[cid])

    user_stage[cid] = stage

# ================== MAIN MENU ==================
def main_menu(chat_id):

    set_stage(chat_id, "main_menu")

    menu = ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = KeyboardButton("💵 Dollar Buy/Sell")
    btn2 = KeyboardButton("🧑‍💻 Support")
    btn3 = KeyboardButton("📢 Support Channel")
    btn4 = KeyboardButton("🌟বিকাশ নগদ পেমেন্ট রুলস")
    btn5 = KeyboardButton("📸 Payment Proof Channel")
    btn6 = KeyboardButton("📱 মোবাইল ব্যাংকিং")

    menu.row(btn1, btn3)
    menu.row(btn4)
    menu.row(btn2, btn5)
    menu.row(btn6)

    bot.send_message(chat_id,"আপনি কী করতে চান? নিচের মেনু থেকে নির্বাচন করুন।\n\n অর্ডার করার আগে অবশ্যই বিকাশ নগদ পেমেন্ট রুলস দেখে নিবেন। ধন্যবাদ🥀",reply_markup=menu)

@bot.message_handler(commands=['start'])
def start(message):

    cid = message.chat.id

    save_user(cid)

    bot.clear_step_handler_by_chat_id(cid)

    user_stage.pop(cid, None)
    stage_history[cid] = []

    pending_amount.pop(cid, None)
    user_amount.pop(cid, None)
    user_rate.pop(cid, None)
    user_total.pop(cid, None)
    user_screenshot.pop(cid, None)
    user_method.pop(cid, None)
    all_users.add(cid)

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

    if cid not in stage_history or len(stage_history[cid]) == 0:
        return main_menu(cid)

    prev_stage = stage_history[cid].pop()
    user_stage[cid] = prev_stage

    if prev_stage == "main_menu":
        main_menu(cid)

    elif prev_stage == "buy_sell":
        buy_sell_menu(message)

    elif prev_stage == "sell_menu":
        sell_options(message)

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

@bot.callback_query_handler(func=lambda call: call.data.startswith(("done_","reject_","exdone_","exreject_","binance","bybit","bitget","BEP-20","Polygon","xrocket")))
def callback_handler(call):

    data = call.data
    cid = call.message.chat.id

    # ================= EXCHANGE DONE =================
    if data.startswith("exdone_"):
        uid = int(data.split("_")[1])
        amount = exchange_data.get(uid, {}).get("amount")
        name = first_name.get(uid, "Unknown")
        type_ = exchange_data.get(uid, {}).get("type")

        if type_ == "bkash_to_nagad":
            type_text = "বিকাশ → নগদ"
        elif type_ == "nagad_to_bkash":
            type_text = "নগদ → বিকাশ"
        else:
            type_text = "Unknown"

    # USER MSG
        bot.send_message(uid, f"✅ অর্ডার কনফার্ম হয়েছে\n\nপরিমাণ: {amount} টাকা")

    # PROOF UPDATE
        if uid in proof_messages:
            try:
                bot.edit_message_text(
                    f"🔄 Exchange Order\n\n"
                    f"👤 নাম: {name}\n"
                    f"📌 বিষয়: {type_text}\n"
                    f"💰 এমাউন্ট: {amount}\n"
                    f"📊 Status: Completed ✅",
                    PROOF_CHANNEL,
                    proof_messages[uid]
                )
            except:
                pass

    # ADMIN MESSAGE UPDATE
        try:
            bot.edit_message_caption(
                call.message.caption.replace("Pending", "Completed ✅"),
                call.message.chat.id,
                call.message.message_id
            )
        except:
            pass

    # REMOVE BUTTON
        try:
            bot.edit_message_reply_markup(
                call.message.chat.id,
                call.message.message_id,
        reply_markup=None
            )
        except:
            pass

        bot.answer_callback_query(call.id, "Done")
        return

    # ================= EXCHANGE REJECT =================
    if data.startswith("exreject_"):
        uid = int(data.split("_")[1])
        amount = exchange_data.get(uid, {}).get("amount")
        name = first_name.get(uid, "Unknown")
        time_now = (datetime.datetime.utcnow() + datetime.timedelta(hours=6)).strftime("%H:%M")

        type_ = exchange_data.get(uid, {}).get("type")
        if type_ == "bkash_to_nagad":
            type_text = "বিকাশ → নগদ"
        elif type_ == "nagad_to_bkash":
            type_text = "নগদ → বিকাশ"
        else:
            type_text = "Unknown"

        bot.send_message(uid, "আপনার পাঠানো তথ্য সঠিক নয়❌ তাই অর্ডারটি ক্যান্সিল করা হয়েছে🤝🥀\n\n অনুগ্রহ করে সাপোর্টে যোগাযোগ করুন। ধন্যবাদ🥀")

        if uid in proof_messages:
            try:
                bot.edit_message_text(
                    f"❌ Exchange Order Rejected\n\n"
                    f"⚠️ Reason: পাঠানো তথ্য সঠিক নয়\n"
                    f"👤 নাম: {name}\n"
                    f"📌 বিষয়: {type_text}\n"
                    f"💰 এমাউন্ট: {amount}\n"
                    f"📊 Status: Rejected 🚫",
                    PROOF_CHANNEL,
                    proof_messages[uid]
                )
            except:
                pass

        try:
            bot.edit_message_caption(
                call.message.caption.replace("Pending", "Rejected ❌"),
                call.message.chat.id,
                call.message.message_id
            )
        except:
            pass

        try:
            bot.edit_message_reply_markup(
                call.message.chat.id,
                call.message.message_id,
                reply_markup=None
            )
        except:
            pass

        bot.answer_callback_query(call.id, "Rejected")
        return

    # ===== PAYMENT DONE =====
    if call.data.startswith("done_"):

        uid = int(call.data.split("_")[1])

        if uid not in user_pending:
            bot.answer_callback_query(call.id, "⚠️ Already done")
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

# ================== PROOF CHANNEL UPDATE ==================
        if uid in proof_messages:
            try:
                name = first_name.get(uid, "unknown")
                bot.edit_message_text(
                    f"🟢 Payment Completed\n\n"
                    f"👤 Name: {name}\n"
                    f"🌐 Network: {network}\n"
                    f"💵 Amount: {amount} USDT\n"
                    f"💸 Total: {total} BDT\n"
                    f"⏰ Time: {time_now}",
                    PROOF_CHANNEL,
                    proof_messages[uid]
                )
            except:
                pass

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

        if uid in proof_messages:
            try:
                name = first_name.get(uid, "Unknown")

                bot.edit_message_text(
                    f"""🔴 Payment Rejected

⚠️Reason: পাঠানো তথ্য সঠিক নয়।
👤 Name: {name}
🌐 Network: {network}
💵 Amount: {amount} USDT
💸 Total: {total} BDT
⏰ Time: {time_now}""",
                PROOF_CHANNEL,
                proof_messages[uid]
            )
            except:
                pass


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
        return back(message)

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
        uid = "`510385821`\n\nযাদের bybit এ ১ ডলারের নিচে আছে তারা Aptos এড্রেসে পাঠাবেন।\nAptos= `0x8e03c8e327455f805df7f0dec92d837be894f499aa3be6ff2a7dda44bf08d954`"

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
        return back(message)

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
    first_name[cid] = user.first_name
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

# পেমেন্ট প্রুফ কোড

    time_now = (datetime.datetime.utcnow() + datetime.timedelta(hours=6)).strftime("%H:%M")

    name = user.first_name

    proof_text = (
        f"🟡 Payment Pending\n\n"
        f"👤 Name: {name}\n"
        f"🌐 Network: {network}\n"
        f"💵 Amount: {amount} USDT\n"
        f"💸 Total: {total} BDT\n"
        f"⏰ Time: {time_now}"
    )

    proof_msg = bot.send_message(PROOF_CHANNEL, proof_text)

    proof_messages[cid] = proof_msg.message_id

# 💔💔💔 

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
    bot.send_message(message.chat.id,"⚠️বিকাশে পেমেন্ট নেওয়ার জন্য অবশ্যই বিকাশ পার্সোনাল নাম্বার দিতে হবে\n\n⚠️ নগদে ১০০ টাকার নিচে পেমেন্ট নিতে হলে সেন্ড মানি ফি ৫ টাকা কেটে নেওয়া হবে। তবে ১০০ টাকার উপরে সেন্ড মানি ফি নাই। ধন্যবাদ🥰🥀\n\nবি:দ্র: কেও 0.10$ এর নিচে অর্ডার করবেন না। এর নিচে অর্ডার করলে পেমেন্ট লস হইলে কর্তৃপক্ষ দায়ী নয়। তাই অবশ্যই 0.10$ এর উপরে অর্ডার করবেন। ধন্যবাদ🥰🥀")

@bot.message_handler(func=lambda msg: msg.text == "📸 Payment Proof Channel")
def proof_channel(message):
    bot.send_message(message.chat.id, "আমাদের Payment Proof Channel:\n👉 https://t.me/starhbemama")


# ================== MOBILE BANKING ==================

@bot.message_handler(func=lambda msg: msg.text == "📱 মোবাইল ব্যাংকিং")
def mobile_banking(message):

    set_stage(message.chat.id, "mobile_menu")

    menu = ReplyKeyboardMarkup(resize_keyboard=True)

    menu.row(
        KeyboardButton("📶 এমবি/মিনিট অফার"),
        KeyboardButton("💳 ব্রিলিয়ান্ট রিচার্জ")
    )
    menu.row(KeyboardButton("🔄 বিকাশ<>নগদ এক্সচেঞ্জ"))
    menu.row(KeyboardButton("🔙 Back"))

    bot.send_message(message.chat.id, "একটি অপশন নির্বাচন করুন:", reply_markup=menu)

# ================== OFFER ==================

@bot.message_handler(func=lambda msg: msg.text == "📶 এমবি/মিনিট অফার")
def mb_offer(message):

    set_stage(message.chat.id, "mb_offer")

    inline = InlineKeyboardMarkup()

    inline.add(
        InlineKeyboardButton("রবি", callback_data="sim_robi"),
        InlineKeyboardButton("গ্রামীণ", callback_data="sim_gp")
    )
    inline.add(
        InlineKeyboardButton("বাংলালিংক", callback_data="sim_bl"),
        InlineKeyboardButton("এয়ারটেল", callback_data="sim_airtel")
    )

    bot.send_message(message.chat.id, "আমাদের এমবি/মিনিট অফার সেল বন্ধ আছে। তাই আপনি এখান থেকে কোনো প্রকার অফার কিনতে পারবেন না। তবে আপনি চাইলে এক্সচেঞ্জ সিস্টেম ব্যবহার করতে পারেন। ধন্যবাদ🥀", reply_markup=inline)

# ================== OFFER SLOT ==================

offers = {
    "robi": ["Offer 1", "Offer 2", "Offer 3"],
    "gp": ["Offer 1", "Offer 2"],
}

@bot.callback_query_handler(func=lambda call: call.data.startswith("sim_"))
def show_offers(call):

    sim = call.data.split("_")[1]

    inline = InlineKeyboardMarkup()

    for i, offer in enumerate(offers.get(sim, [])):
        inline.add(InlineKeyboardButton(offer, callback_data=f"offer_{sim}_{i}"))

    bot.send_message(call.message.chat.id, "অফার নির্বাচন করুন:", reply_markup=inline)

# ================== 2ND PAYMENT ==================

@bot.callback_query_handler(func=lambda call: call.data.startswith("offer_"))
def select_offer(call):

    cid = call.message.chat.id

    user_selected_offer = call.data

    user_stage[cid] = "offer_payment"

    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    menu.row(KeyboardButton("বিকাশ"), KeyboardButton("নগদ"), KeyboardButton("রকেট"))
    menu.row(KeyboardButton("🔙 Back"))

    bot.send_message(cid, "অফারটি নিতে আপনি কিসের মাধ্যমে পেমেন্ট করতে চান নির্বাচন করুন:", reply_markup=menu)

@bot.message_handler(func=lambda msg: msg.text in ["বিকাশ","নগদ","রকেট"] and user_stage.get(msg.chat.id) == "offer_payment")
def payment_select(message):

    cid = message.chat.id
    method = message.text

    user_method[cid] = method

    bot.send_message(cid, f"{method} নাম্বারে পেমেন্ট করে স্ক্রিনশট পাঠান")

    bot.register_next_step_handler(message, mb_receive_ss)

def mb_receive_ss(message):

    cid = message.chat.id

    if message.content_type != "photo":
        bot.send_message(cid, "স্ক্রিনশট পাঠান")
        bot.register_next_step_handler(message, mb_receive_ss)
        return

    bot.send_message(cid, "আপনার নাম্বারের লাস্ট ডিজিট লিখুন")

    bot.register_next_step_handler(message, mb_last_digit)

def mb_last_digit(message):

    bot.send_message(message.chat.id, "অর্ডার গ্রহণ করা হয়েছে ❤️‍🩹🥀")
    main_menu(message.chat.id)

# ================== EXCHANGE SYSTEM ==================

@bot.message_handler(func=lambda msg: msg.text == "🔄 বিকাশ<>নগদ এক্সচেঞ্জ")
def exchange(message):

    set_stage(message.chat.id, "exchange_menu")

    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    menu.row(
        KeyboardButton("বিকাশ → নগদ"),
        KeyboardButton("নগদ → বিকাশ")
    )
    menu.row(KeyboardButton("📜 এক্সচেঞ্জ রুলস"))
    menu.row(KeyboardButton("🔙 Back"))

    bot.send_message(message.chat.id,
    "আপনি কী করতে চান? নিচের মেনু থেকে সিলেক্ট করুন।🥰\n\n এক্সচেঞ্জের পূর্বে অবশ্যই রুলস দেখে নিবেন ভুল হলে কর্তৃপক্ষ দায়ী থাকবে না।",
    reply_markup=menu)

# ================== BKASH TO NAGAD ==================

@bot.message_handler(func=lambda msg: msg.text == "বিকাশ → নগদ")
def bkash_to_nagad(message):

    cid = message.chat.id
    set_stage(cid, "bkash_amount")

    exchange_data[cid] = {"type": "bkash_to_nagad"}

    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(KeyboardButton("🔙 Back"))

    bot.send_message(cid,
    "আপনি কতো টাকা এক্সচেঞ্জ করতে চান? নিচে লিখুন\n\nসর্বনিম্ন ৩০ টাকা থেকে সর্বোচ্চ ৩০০ টাকা পর্যন্ত এক্সচেঞ্জ করতে পারবেন।",
    reply_markup=menu)

    bot.register_next_step_handler(message, get_bkash_amount)

def get_bkash_amount(message):

    cid = message.chat.id

    if message.text == "🔙 Back":
        return back(message)

    try:
        amount = int(message.text)
    except:
        bot.send_message(cid, "সঠিক এমাউন্ট লিখুন")
        bot.register_next_step_handler(message, get_bkash_amount)
        return

    if amount < 30 or amount > 300:
        bot.send_message(cid,
        "৩০-৩০০ টাকার ভিতরে লিখুন")
        bot.register_next_step_handler(message, get_bkash_amount)
        return

    exchange_data[cid]["amount"] = amount

    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(KeyboardButton("🔙 Back"))

    bot.send_message(cid,
    "নিচের বিকাশ নাম্বারে টাকা পাঠান:\n\n`01975080634`\n\nতারপর স্ক্রিনশট পাঠান",
    reply_markup=menu)

    bot.register_next_step_handler(message, get_bkash_ss)

def get_bkash_ss(message):

    cid = message.chat.id

    if message.text == "🔙 Back":
        return back(message)

    if message.content_type != "photo":
        bot.send_message(cid, "স্ক্রিনশট পাঠান")
        bot.register_next_step_handler(message, get_bkash_ss)
        return

    exchange_data[cid]["ss"] = message.photo[-1].file_id

    bot.send_message(cid, "আপনার লাস্ট নাম্বার লিখুন")
    bot.register_next_step_handler(message, get_last_digit)

def get_last_digit(message):

    cid = message.chat.id

    if message.text == "🔙 Back":
        return back(message)

    exchange_data[cid]["last"] = message.text

    bot.send_message(cid,
    "আপনি যেই নাম্বারে পেমেন্ট নিতে চান\nসেই *নগদ নাম্বার* লিখুন",
    parse_mode="Markdown")

    bot.register_next_step_handler(message, get_nagad_number)

def get_nagad_number(message):

    cid = message.chat.id

    number = message.text
    data = exchange_data.get(cid, {})

    amount = data.get("amount")
    type_ = exchange_data.get(cid, {}).get("type")

    if type_ == "bkash_to_nagad":
        type_text = "বিকাশ → নগদ"
    elif type_ == "nagad_to_bkash":
        type_text = "নগদ → বিকাশ"
    else:
        type_text = "Unknown"
    last = data.get("last")

    user = message.from_user

    first_name[cid] = message.from_user.first_name
    username = f"@{user.username}" if user.username else user.first_name

    caption = (
        f"🔄 Exchange Request\n\n"
        f"👤 User: {username}\n"
        f"🆔 ID: {cid}\n"
        f"🔢 Last Digit: {last}\n"
        f"📡 Type: বিকাশ → নগদ\n"
        f"💰 Amount: {amount}\n"
        f"📱 Nagad: {number}\n"
        f"📌 Status: Pending"
    )

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Done", callback_data=f"exdone_{cid}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"exreject_{cid}")
    )

    # ✅ এটা ভিতরে
    msg = bot.send_photo(
        ADMIN_GROUP,
        data["ss"],
        caption=caption,
        reply_markup=markup
    )

    # ===== PROOF CHANNEL =====
    name = user.first_name

    proof_text = (
        f"🔄 Exchange Order\n\n"
        f"👤 নাম: {name}\n"
        f"📌 বিষয়: {type_text}\n"
        f"💰 এমাউন্ট: {amount}\n"
        f"📊 Status: Pending 🔄"
    )

    proof_msg = bot.send_message(PROOF_CHANNEL, proof_text)

    proof_messages[cid] = proof_msg.message_id

    bot.send_message(cid, "আপনার অর্ডারটি সফলভাবে গ্রহণ করা হয়েছে। অনুগ্রহ করে অপেক্ষা করুন🥰। যেকোনো প্রয়োজনে সাপোর্টে যোগাযোগ করুন🥰।\n\nআমাদের সাপোর্ট চ্যানেল: https://t.me/Online_small_jobs 👈")

    main_menu(cid)

# ================== NAGAD TO BKASH ==================

@bot.message_handler(func=lambda msg: msg.text == "নগদ → বিকাশ")
def nagad_to_bkash(message):

    cid = message.chat.id
    set_stage(cid, "nagad_amount")

    exchange_data[cid] = {"type": "nagad_to_bkash"}

    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(KeyboardButton("🔙 Back"))

    bot.send_message(
        cid,
        "আপনি কতো টাকা এক্সচেঞ্জ করতে চান? নিচে লিখুন\n\nসর্বনিম্ন ৩০ টাকা থেকে সর্বোচ্চ ৩০০ টাকা পর্যন্ত এক্সচেঞ্জ করতে পারবেন।",
        reply_markup=menu
    )

    bot.register_next_step_handler(message, get_nagad_amount)

def get_nagad_amount(message):

    cid = message.chat.id

    if message.text == "🔙 Back":
        return back(message)

    try:
        amount = int(message.text)
    except:
        bot.send_message(cid, "সঠিক এমাউন্ট লিখুন")
        bot.register_next_step_handler(message, get_nagad_amount)
        return

    if amount < 30 or amount > 300:
        bot.send_message(cid, "৩০-৩০০ টাকার ভিতরে লিখুন")
        bot.register_next_step_handler(message, get_nagad_amount)
        return

    exchange_data[cid]["amount"] = amount

    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(KeyboardButton("🔙 Back"))

    bot.send_message(
        cid,
        "নিচের নগদ নাম্বারে টাকা পাঠান:\n\n`9856001086179441`\n\n তারপর স্ক্রিনশট পাঠান\n\nনাম্বার ঠিক আছে এটা ভার্চুয়াল নাম্বার তাই এমন। আপনি সেন্ড মানি করেন।",
        reply_markup=menu,
        parse_mode="Markdown"
    )

    bot.register_next_step_handler(message, get_nagad_ss)

def get_nagad_ss(message):

    cid = message.chat.id

    if message.text == "🔙 Back":
        return back(message)

    if message.content_type != "photo":
        bot.send_message(cid, "স্ক্রিনশট পাঠান")
        bot.register_next_step_handler(message, get_nagad_ss)
        return

    exchange_data[cid]["ss"] = message.photo[-1].file_id

    bot.send_message(cid, "আপনার লাস্ট নাম্বার লিখুন")

    bot.register_next_step_handler(message, get_nagad_last)

def get_nagad_last(message):

    cid = message.chat.id

    if message.text == "🔙 Back":
        return back(message)

    exchange_data[cid]["last"] = message.text

    bot.send_message(
        cid,
        "আপনি যেই নাম্বারে পেমেন্ট নিতে চান\nসেই *বিকাশ নাম্বার* লিখুন",
        parse_mode="Markdown"
    )

    bot.register_next_step_handler(message, get_bkash_number_from_nagad)

def get_bkash_number_from_nagad(message):

    cid = message.chat.id

    number = message.text
    data = exchange_data.get(cid, {})

    amount = data.get("amount")
    last = data.get("last")

    user = message.from_user

    first_name[cid] = user.first_name
    username = f"@{user.username}" if user.username else user.first_name

    caption = (
        f"🔄 Exchange Request\n\n"
        f"👤 User: {username}\n"
        f"🆔 ID: {cid}\n"
        f"🔢 Last Digit: `{last}`\n"
        f"📡 Type: নগদ → বিকাশ\n"
        f"💰 Amount: {amount}\n"
        f"📱 Bkash: `{number}`\n"
        f"📌 Status: Pending"
    )

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Done", callback_data=f"exdone_{cid}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"exreject_{cid}")
    )

    msg = bot.send_photo(
        ADMIN_GROUP,
        data["ss"],
        caption=caption,
        reply_markup=markup,
        parse_mode="Markdown"
    )

    # 🔥 PROOF CHANNEL
    type_ = exchange_data.get(cid, {}).get("type")

    if type_ == "bkash_to_nagad":
        type_text = "বিকাশ → নগদ"
    elif type_ == "nagad_to_bkash":
        type_text = "নগদ → বিকাশ"
    else:
        type_text = "Unknown"
    proof_text = (
        f"🔄 Exchange Order\n\n"
        f"👤 নাম: {user.first_name}\n"
        f"📌 বিষয়: {type_text}\n"
        f"💰 এমাউন্ট: {amount}\n"
        f"📊 Status: Pending 🔄"
    )

    proof_msg = bot.send_message(PROOF_CHANNEL, proof_text)

    proof_messages[cid] = proof_msg.message_id

    bot.send_message(cid, "আপনার অর্ডারটি সফলভাবে গ্রহণ করা হয়েছে। অনুগ্রহ করে অপেক্ষা করুন🥰। যেকোনো প্রয়োজনে সাপোর্টে যোগাযোগ করুন🥰।\n\nআমাদের সাপোর্ট চ্যানেল: https://t.me/Online_small_jobs 👈")

    main_menu(cid)

# ================== ADMIN PANEL ==================

@bot.message_handler(commands=['setoffer'])
def set_offer(message):

    if message.chat.id != ADMIN_ID:
        return

    bot.send_message(message.chat.id, "Format:\nsim|offer")

    bot.register_next_step_handler(message, save_offer)
    
def save_offer(message):

    try:
        sim, offer = message.text.split("|")

        if sim not in offers:
            offers[sim] = []

        offers[sim].append(offer)

        bot.send_message(message.chat.id, "✅ Offer added")

    except:
        bot.send_message(message.chat.id, "❌ Format ভুল")

# ================== EXCHANGE RULES ==================

@bot.message_handler(func=lambda msg: msg.text == "📜 এক্সচেঞ্জ রুলস")
def exrules(message):
    bot.send_message(message.chat.id, "এক্সচেঞ্জ রুলস:\n\n ১. বিকাশে পেমেন্ট নেওয়ার জন্য অবশ্যই বিকাশ পার্সোনাল নাম্বার দিতে হবে। বিকাশ পার্সোনাল না থাকলে স্টুডেন্ট নাম্বার যদি দেন তবে নাম্বারের সাথে ফার্স্ট ব্র‍্যাকেটে লিখে দিবেন (স্টুডেন্ট) 👈 এভাবে।✅\n\n ২.প্রতি এক্সচেঞ্জে খরচ হিসেবে ৫ টাকা ফি কেটে নেওয়া হবে। যেমন: আপনি ১০৫ টাকা পাঠাইলে আপনি পাবেন ১০০ টাকা\n\n  ৩. যেকোনো এক্সচেঞ্জে অবশ্যই স্ক্রিনশট পাঠাতে হবে। স্ক্রিনশট ব্যতীত কোনো এক্সচেঞ্জ গ্রহণযোগ্য হবে না।🥰🤝🥰\n\n ❝আশা করি সকলেই রুলস ফলো করে সততার সাথে লেনদেন করবেন।❞ ধন্যবাদ🥰🤝🥰")

@bot.message_handler(func=lambda m: True, content_types=['text'])
def track_users(message):
    save_user(message.chat.id)

# ================== RUN ==================
bot.infinity_polling()

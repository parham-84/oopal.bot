import uuid
import random
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
    ContextTypes,
)

TOKEN = "8329825566:AAE8xRpY-AAe8rW9R1TGZiuWq0ttTyV9SUk"

# ═══════════════════════════════════════════════
# دوز
# ═══════════════════════════════════════════════
games = {}

WIN_LINES = [
    (0,1,2),(3,4,5),(6,7,8),
    (0,3,6),(1,4,7),(2,5,8),
    (0,4,8),(2,4,6),
]

def check_winner(board):
    for a,b,c in WIN_LINES:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    if " " not in board:
        return "draw"
    return None

def build_ttt_keyboard(board, game_id):
    emoji_map = {"X":"❌","O":"⭕"," ":"⬜"}
    buttons = []
    for row in range(3):
        rb = []
        for col in range(3):
            idx = row*3+col
            rb.append(InlineKeyboardButton(emoji_map.get(board[idx],board[idx]), callback_data=f"move:{game_id}:{idx}"))
        buttons.append(rb)
    return InlineKeyboardMarkup(buttons)

def render_ttt(game):
    x_name = game["players"]["X"][1]
    if game["status"] == "waiting":
        return (
            "🎮 بازی دوز — آماده نبرد!\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"🔥 {x_name} وارد میدان شد!\n\n"
            "⏳ دنبال یه حریف می‌گردیم...\n"
            "کِیه که جرأت داره قبول کنه؟ 😤"
        )
    o_name = game["players"]["O"][1]
    if game["status"] == "finished":
        result = check_winner(game["board"])
        if result == "draw":
            return (
                "🎮 بازی دوز\n━━━━━━━━━━━━━━━━━━\n"
                f"❌ {x_name}  vs  ⭕ {o_name}\n\n"
                "🤝 مساوی شد!\n"
                "هر دو نه بردید نه باختید 😐 یعنی هر دو باختید 😂"
            )
        winner = x_name if result=="X" else o_name
        loser  = o_name if result=="X" else x_name
        return (
            "🎮 بازی دوز\n━━━━━━━━━━━━━━━━━━\n"
            f"❌ {x_name}  vs  ⭕ {o_name}\n\n"
            f"🏆 {winner} برنده شد!\n"
            f"💀 {loser} برو یکم تمرین کن بیا 😹"
        )
    turn_emoji = "❌" if game["turn"]=="X" else "⭕"
    turn_name  = x_name if game["turn"]=="X" else o_name
    wait_name  = o_name if game["turn"]=="X" else x_name
    return (
        "🎮 بازی دوز\n━━━━━━━━━━━━━━━━━━\n"
        f"❌ {x_name}  vs  ⭕ {o_name}\n\n"
        f"{turn_emoji} نوبت {turn_name}ه — فکر کن!\n"
        f"😴 {wait_name} داره می‌میره از بی‌حوصلگی..."
    )

# ═══════════════════════════════════════════════
# سنگ کاغذ قیچی
# ═══════════════════════════════════════════════
RPS_CHOICES = {"rock":"🪨 سنگ","paper":"📄 کاغذ","scissors":"✂️ قیچی"}
RPS_BEATS   = {"rock":"scissors","paper":"rock","scissors":"paper"}
RPS_ROAST   = {"rock":"سنگ؟! خیلی کلاسیکی 😒","paper":"کاغذ؟! جسورانه‌ست 😏","scissors":"قیچی؟! ریسکی بود این 😬"}
rps_games   = {}

def rps_judge(cx, co):
    if cx == co: return "draw"
    return "X" if RPS_BEATS[cx]==co else "O"

def build_rps_keyboard(game_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🪨  سنگ",   callback_data=f"rpsmove:{game_id}:rock")],
        [InlineKeyboardButton("📄  کاغذ",  callback_data=f"rpsmove:{game_id}:paper")],
        [InlineKeyboardButton("✂️  قیچی", callback_data=f"rpsmove:{game_id}:scissors")],
    ])

def render_rps(game):
    x_name = game["players"]["X"][1]
    if game["status"] == "waiting":
        return (
            "✊📄✂️  بازی سنگ‌کاغذقیچی!\n━━━━━━━━━━━━━━━━━━\n"
            f"⚔️  بازیکن اول:  {x_name}\n\n"
            "⏳ منتظر یه قربانی دیگه‌ایم...\n"
            "دوستت رو دعوت کن تا له‌اش کنی! 😈"
        )
    o_name = game["players"]["O"][1]
    if game["status"] == "finished":
        cx = RPS_CHOICES[game["choices"]["X"]]
        co = RPS_CHOICES[game["choices"]["O"]]
        result = game["result"]
        lines = ["🥁 نتیجه نهایی:\n━━━━━━━━━━━━━━━━━━",
                 f"❌ {x_name}  ←  {cx}", f"⭕ {o_name}  ←  {co}", ""]
        if result == "draw":
            lines.append("🤝 مساوی! هر دو باختید 😂")
        else:
            winner = x_name if result=="X" else o_name
            loser  = o_name if result=="X" else x_name
            lines += [f"🏆 {winner} قهرمان شد!", f"💀 {loser} خجالت بکش برو خونه 😹"]
        return "\n".join(lines)
    chosen = list(game["choices"].keys())
    return "\n".join([
        "✊📄✂️  سنگ‌کاغذقیچی در جریانه!\n━━━━━━━━━━━━━━━━━━",
        f"❌ {x_name}  vs  ⭕ {o_name}", "",
        "🤫 مخفیانه انتخاب کن! حریفت نباید بفهمه...", "",
        f"{'✅' if 'X' in chosen else '⏳'} {x_name}",
        f"{'✅' if 'O' in chosen else '⏳'} {o_name}",
    ])

# ═══════════════════════════════════════════════
# Battleship 8×8
# ═══════════════════════════════════════════════
bs_games = {}

# کشتی‌ها: (اسم، سایز، ایموجی)
SHIPS = [
    ("ناو هواپیمابر", 4, "🛸"),
    ("رزمناو",        3, "🚢"),
    ("زیردریایی",     3, "🐬"),
    ("ناوشکن",        2, "⛵"),
]

SIZE = 8

WATER     = "🟦"
SHIP_CELL = "🟫"  # فقط برای خودِ بازیکن نمایش داده میشه
HIT       = "💥"
MISS      = "⚫"
SUNK      = "🔥"

def empty_grid():
    return [[WATER]*SIZE for _ in range(SIZE)]

def can_place(grid, r, c, length, horiz):
    cells = [(r, c+i) if horiz else (r+i, c) for i in range(length)]
    for rr, cc in cells:
        if rr<0 or rr>=SIZE or cc<0 or cc>=SIZE: return False
        if grid.get((rr, cc), WATER) != WATER: return False
    return True

def place_ship(grid, ship_grid, r, c, length, horiz, emoji):
    cells = [(r, c+i) if horiz else (r+i, c) for i in range(length)]
    for rr, cc in cells:
        grid[(rr, cc)] = SHIP_CELL
        ship_grid[(rr, cc)] = emoji

def new_bs_game():
    return {
        "players": {},          # {0: (uid, name), 1: (uid, name)}
        "grids":   [{}, {}],    # grid نمایشی هر بازیکن (شامل کشتی‌هاش)
        "ship_grids": [{}, {}], # نگه میداره هر سلول به کدوم کشتی تعلق داره
        "targets": [{}, {}],    # grid حمله هر بازیکن به دیگری
        "ships_remaining": [{}, {}],  # کشتی‌های باقیمانده
        "placing": [0, 0],      # ایندکس کشتی در حال چیدن
        "placing_horiz": [True, True],
        "status": "waiting",    # waiting / placing / playing / finished
        "turn": 0,
        "msg_ids": [None, None],# آیدی پیام صفحه هر بازیکن
        "winner": None,
    }

def render_bs_own_grid(game, pid):
    """صفحه خودِ بازیکن (کشتی‌هاش رو می‌بینه)"""
    grid = game["grids"][pid]
    rows = []
    header = "⬛" + "".join([f"{chr(0x1F1E6+i)}" for i in range(SIZE)])
    rows.append(header)
    num_emojis = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣"]
    for r in range(SIZE):
        row = num_emojis[r]
        for c in range(SIZE):
            row += grid.get((r,c), WATER)
        rows.append(row)
    return "\n".join(rows)

def render_bs_target_grid(game, pid):
    """صفحه حمله بازیکن (فقط hit/miss می‌بینه)"""
    grid = game["targets"][pid]
    rows = []
    header = "⬛" + "".join([f"{chr(0x1F1E6+i)}" for i in range(SIZE)])
    rows.append(header)
    num_emojis = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣"]
    for r in range(SIZE):
        row = num_emojis[r]
        for c in range(SIZE):
            row += grid.get((r,c), WATER)
        rows.append(row)
    return "\n".join(rows)

def build_bs_place_keyboard(game, pid):
    """کیبورد چیدن کشتی"""
    grid = game["grids"][pid]
    ship_idx = game["placing"][pid]
    if ship_idx >= len(SHIPS):
        return None
    name, length, emoji = SHIPS[ship_idx]
    horiz = game["placing_horiz"][pid]

    buttons = []
    num_emojis = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣"]
    letters = [chr(0x1F1E6+i) for i in range(SIZE)]

    # هدر حروف
    header_row = [InlineKeyboardButton("⬛", callback_data="bs_noop")]
    for c in range(SIZE):
        header_row.append(InlineKeyboardButton(letters[c], callback_data="bs_noop"))
    buttons.append(header_row)

    for r in range(SIZE):
        row = [InlineKeyboardButton(num_emojis[r], callback_data="bs_noop")]
        for c in range(SIZE):
            cell = grid.get((r,c), WATER)
            row.append(InlineKeyboardButton(cell, callback_data=f"bsplace:{pid}:{r}:{c}"))
        buttons.append(row)

    # دکمه چرخش
    buttons.append([InlineKeyboardButton(
        f"🔄 چرخش: {'افقی ↔️' if horiz else 'عمودی ↕️'}",
        callback_data=f"bsrotate:{pid}"
    )])
    return InlineKeyboardMarkup(buttons)

def build_bs_attack_keyboard(game, pid):
    """کیبورد حمله"""
    target_grid = game["targets"][pid]
    buttons = []
    letters = [chr(0x1F1E6+i) for i in range(SIZE)]
    num_emojis = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣"]

    header_row = [InlineKeyboardButton("⬛", callback_data="bs_noop")]
    for c in range(SIZE):
        header_row.append(InlineKeyboardButton(letters[c], callback_data="bs_noop"))
    buttons.append(header_row)

    for r in range(SIZE):
        row = [InlineKeyboardButton(num_emojis[r], callback_data="bs_noop")]
        for c in range(SIZE):
            cell = target_grid.get((r,c), WATER)
            row.append(InlineKeyboardButton(cell, callback_data=f"bsattack:{pid}:{r}:{c}"))
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)

def check_ship_sunk(game, enemy_pid, r, c):
    """آیا کشتی‌ای که زده شد غرق شد؟"""
    ship_emoji = game["ship_grids"][enemy_pid].get((r,c))
    if not ship_emoji:
        return False, None
    # پیدا کردن همه سلول‌های این کشتی
    all_cells = [(rr,cc) for (rr,cc),e in game["ship_grids"][enemy_pid].items() if e==ship_emoji]
    attacker_pid = 1-enemy_pid
    target = game["targets"][attacker_pid]
    # همه سلول‌هاش زده شده؟
    if all(target.get((rr,cc)) in (HIT, SUNK) for rr,cc in all_cells):
        return True, all_cells
    return False, None

# ═══════════════════════════════════════════════
# هندلرهای اصلی
# ═══════════════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_username = (await context.bot.get_me()).username
    await update.message.reply_text(
        "👾 سلام قهرمان!\n\n"
        "اینجا میتونی با دوستات بازی کنی و له‌شون کنی 😈\n\n"
        "📌 چطور شروع کنم؟\n"
        f"توی هر چتی بنویس:  @{bot_username}\n"
        "بعد یه بازی انتخاب کن و لینکش رو برای دوستت بفرست!\n\n"
        "🎮 دوز  |  ✊ سنگ‌کاغذقیچی  |  🚢 دریایی\n\n"
        "بریم که وقت باختن دوستته! 😂"
    )

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query

    # دوز
    ttt_id = str(uuid.uuid4())
    ttt_result = InlineQueryResultArticle(
        id=ttt_id, title="🎮 بازی دوز — دو نفره",
        description="دوستت رو له کن! 😈",
        input_message_content=InputTextMessageContent("🎮 یه نفر اومده دوز بازی کنه!\nاگه جرأت داری روی دکمه بزن... 😤"),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎮 منم میخوام!", callback_data=f"join:{ttt_id}")]]),
    )

    # سنگ کاغذ قیچی
    rps_id = str(uuid.uuid4())
    rps_result = InlineQueryResultArticle(
        id=rps_id, title="✊ سنگ، کاغذ، قیچی",
        description="یه دور سریع با دوستت!",
        input_message_content=InputTextMessageContent("✊ یه نفر اومده سنگ‌کاغذقیچی بازی کنه!\nقبول می‌کنی چالشش رو؟ 😏"),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✊ منم میخوام!", callback_data=f"rpsjoin:{rps_id}")]]),
    )

    # دریایی
    bs_id = str(uuid.uuid4())
    bs_result = InlineQueryResultArticle(
        id=bs_id, title="🚢 بازی دریایی — Battleship",
        description="کشتی‌هات رو بچین و حریفت رو غرق کن! 💣",
        input_message_content=InputTextMessageContent("🚢 یه نفر اومده دریایی بازی کنه!\nجرأت داری کشتی‌هاش رو غرق کنی؟ 💣"),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚢 قبول می‌کنم!", callback_data=f"bsjoin:{bs_id}")]]),
    )

    tod_id = str(uuid.uuid4())
    tod_result = InlineQueryResultArticle(
        id=tod_id,
        title="جرئت و حقیقت",
        description="با دوستات بازی کن!",
        input_message_content=InputTextMessageContent("جرئت و حقیقت - برای ورود روی دکمه بزن!"),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("منم میام!", callback_data=f"todinljoin:{tod_id}")]]),
    )

    await query.answer([ttt_result, rps_result, bs_result, tod_result], cache_time=0)

# ─── دوز هندلرها ───────────────────────────────
async def handle_join(update, context, temp_id):
    q = update.callback_query
    user = q.from_user
    game_id = str(uuid.uuid4())
    games[game_id] = {"board":[" "]*9,"turn":"X","players":{"X":(user.id,user.first_name)},"status":"waiting"}
    await q.answer("وارد شدی به عنوان ❌", show_alert=False)
    await q.edit_message_text(
        text=render_ttt(games[game_id]),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🤝 قبول می‌کنم! (⭕)", callback_data=f"accept:{game_id}")]]),
    )

async def handle_accept(update, context, game_id):
    q = update.callback_query
    user = q.from_user
    game = games.get(game_id)
    if not game: await q.answer("بازی پیدا نشد 😬", show_alert=True); return
    if game["status"]!="waiting": await q.answer("دیر رسیدی! 😅", show_alert=True); return
    if user.id==game["players"]["X"][0]: await q.answer("نمیتونی با خودت بازی کنی! 😂", show_alert=True); return
    game["players"]["O"]=(user.id,user.first_name); game["status"]="playing"
    await q.answer("🎉 بازی شروع شد!", show_alert=False)
    await q.edit_message_text(text=render_ttt(game), reply_markup=build_ttt_keyboard(game["board"],game_id))

async def handle_ttt_move(update, context, game_id, idx):
    q = update.callback_query
    user = q.from_user
    game = games.get(game_id)
    if not game or game["status"]!="playing": await q.answer("بازی تموم شده!"); return
    symbol = game["turn"]
    if user.id!=game["players"][symbol][0]: await q.answer("صبر کن نوبتت بشه! 😒", show_alert=True); return
    if game["board"][idx]!=" ": await q.answer("این خونه پره! 😂", show_alert=True); return
    game["board"][idx]=symbol
    if check_winner(game["board"]): game["status"]="finished"
    else: game["turn"]="O" if symbol=="X" else "X"
    await q.edit_message_text(text=render_ttt(game), reply_markup=build_ttt_keyboard(game["board"],game_id))
    await q.answer()

# ─── RPS هندلرها ───────────────────────────────
async def handle_rps_join(update, context, temp_id):
    q = update.callback_query
    user = q.from_user
    game_id = str(uuid.uuid4())
    rps_games[game_id]={"players":{"X":(user.id,user.first_name)},"choices":{},"status":"waiting"}
    await q.answer("وارد شدی! منتظر حریف باش... 😤", show_alert=False)
    await q.edit_message_text(
        text=render_rps(rps_games[game_id]),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✊ قبول می‌کنم!", callback_data=f"rpsaccept:{game_id}")]]),
    )

async def handle_rps_accept(update, context, game_id):
    q = update.callback_query
    user = q.from_user
    game = rps_games.get(game_id)
    if not game: await q.answer("بازی پیدا نشد 😬", show_alert=True); return
    if game["status"]!="waiting": await q.answer("دیر رسیدی! 😅", show_alert=True); return
    if user.id==game["players"]["X"][0]: await q.answer("با خودت نمیشه! 😂", show_alert=True); return
    game["players"]["O"]=(user.id,user.first_name); game["status"]="playing"
    await q.answer("🎉 بازی شروع! مخفیانه انتخاب کن 🤫", show_alert=False)
    await q.edit_message_text(text=render_rps(game), reply_markup=build_rps_keyboard(game_id))

async def handle_rps_move(update, context, game_id, choice):
    q = update.callback_query
    user = q.from_user
    game = rps_games.get(game_id)
    if not game or game["status"]!="playing": await q.answer("بازی تموم شده!"); return
    symbol = next((s for s,(uid,_) in game["players"].items() if uid==user.id), None)
    if symbol is None: await q.answer("تو بازیکن این بازی نیستی! 😂", show_alert=True); return
    if symbol in game["choices"]: await q.answer("قبلاً انتخاب کردی! 😏", show_alert=True); return
    game["choices"][symbol]=choice
    await q.answer(f"ثبت شد: {RPS_CHOICES[choice]}\n{RPS_ROAST[choice]}", show_alert=True)
    if len(game["choices"])<2:
        await q.edit_message_text(text=render_rps(game), reply_markup=build_rps_keyboard(game_id)); return
    game["result"]=rps_judge(game["choices"]["X"],game["choices"]["O"]); game["status"]="finished"
    await q.edit_message_text(text=render_rps(game))

# ─── Battleship هندلرها ────────────────────────
async def handle_bs_join(update, context, temp_id):
    q = update.callback_query
    user = q.from_user
    game_id = str(uuid.uuid4())
    game = new_bs_game()
    game["players"][0] = (user.id, user.first_name)
    game["grids"][0] = {}
    game["ship_grids"][0] = {}
    game["targets"][0] = {}
    game["ships_remaining"][0] = {e: len([c for c in range(l)]) for _,l,e in SHIPS}
    bs_games[game_id] = game
    await q.answer("وارد شدی! کشتی‌هات رو بچین 🚢", show_alert=False)
    await q.edit_message_text(
        text=(
            "🚢 بازی دریایی!\n━━━━━━━━━━━━━━━━━━\n"
            f"⚓ {user.first_name} وارد شد!\n\n"
            "⏳ منتظر حریف...\n"
            "لینک رو برای دوستت بفرست تا شروع بشه 💣"
        ),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚢 منم میام!", callback_data=f"bsaccept:{game_id}")]]),
    )

async def handle_bs_accept(update, context, game_id):
    q = update.callback_query
    user = q.from_user
    game = bs_games.get(game_id)
    if not game: await q.answer("بازی پیدا نشد 😬", show_alert=True); return
    if game["status"]!="waiting": await q.answer("دیر رسیدی! 😅", show_alert=True); return
    if user.id==game["players"][0][0]: await q.answer("با خودت نمیشه! 😂", show_alert=True); return
    game["players"][1]=(user.id,user.first_name)
    game["grids"][1]={}; game["ship_grids"][1]={}; game["targets"][1]={}
    game["ships_remaining"][1]={e: l for _,l,e in SHIPS}
    game["status"]="placing"
    await q.answer("🎉 بازی شروع! حالا کشتی‌هات رو بچین", show_alert=False)

    # پیام چیدن برای هر دو نفر جداگانه
    p0_name, p1_name = game["players"][0][1], game["players"][1][1]
    ship_name, ship_len, ship_emoji = SHIPS[0]

    for pid in [0, 1]:
        pname = game["players"][pid][1]
        kb = build_bs_place_keyboard(game, pid)
        text = (
            f"🚢 {pname} — مرحله چیدن کشتی‌ها\n━━━━━━━━━━━━━━━━━━\n"
            f"الان بچین: {ship_emoji} {ship_name} (سایز {ship_len})\n\n"
            "روی صفحه کلیک کن تا کشتی بذاری\n"
            "🔄 دکمه چرخش رو بزن تا جهتش عوض بشه"
        )
        try:
            sent = await context.bot.send_message(chat_id=game["players"][pid][0], text=text, reply_markup=kb)
            game["msg_ids"][pid] = sent.message_id
        except Exception as e:
            print(f"BS Accept send error p{pid}: {e}")

    await q.edit_message_text(
        f"🚢 بازی دریایی شروع شد!\n━━━━━━━━━━━━━━━━━━\n"
        f"⚔️ {p0_name}  vs  {p1_name}\n\n"
        "هر دو دارن کشتی‌هاشون رو می‌چینن... 🤫\n"
        "نتیجه رو اینجا اعلام می‌کنیم!"
    )

async def handle_bs_rotate(update, context, pid_str):
    q = update.callback_query
    user = q.from_user
    pid = int(pid_str)
    game_id = next((gid for gid,g in bs_games.items() if g["players"].get(pid) and g["players"][pid][0]==user.id and g["status"]=="placing"), None)
    if not game_id: await q.answer("بازی پیدا نشد!"); return
    game = bs_games[game_id]
    game["placing_horiz"][pid] = not game["placing_horiz"][pid]
    ship_idx = game["placing"][pid]
    ship_name, ship_len, ship_emoji = SHIPS[ship_idx]
    horiz = game["placing_horiz"][pid]
    await q.answer(f"جهت: {'افقی ↔️' if horiz else 'عمودی ↕️'}")
    kb = build_bs_place_keyboard(game, pid)
    text = (
        f"🚢 مرحله چیدن کشتی‌ها\n━━━━━━━━━━━━━━━━━━\n"
        f"الان بچین: {ship_emoji} {ship_name} (سایز {ship_len})\n"
        f"جهت: {'افقی ↔️' if horiz else 'عمودی ↕️'}\n\n"
        "روی صفحه کلیک کن تا کشتی بذاری"
    )
    await q.edit_message_text(text=text, reply_markup=kb)

async def handle_bs_place(update, context, pid_str, r_str, c_str):
    q = update.callback_query
    user = q.from_user
    pid = int(pid_str); r = int(r_str); c = int(c_str)
    game_id = next((gid for gid,g in bs_games.items() if g["players"].get(pid) and g["players"][pid][0]==user.id and g["status"]=="placing"), None)
    if not game_id: await q.answer("بازی پیدا نشد!"); return
    game = bs_games[game_id]
    ship_idx = game["placing"][pid]
    if ship_idx >= len(SHIPS): await q.answer("همه کشتی‌ها چیده شدن!"); return
    ship_name, ship_len, ship_emoji = SHIPS[ship_idx]
    horiz = game["placing_horiz"][pid]

    if not can_place(game["grids"][pid], r, c, ship_len, horiz):
        await q.answer("اینجا جا نیست! یه جای دیگه امتحان کن 😅", show_alert=True); return

    # چیدن کشتی
    place_ship(game["grids"][pid], game["ship_grids"][pid], r, c, ship_len, horiz, ship_emoji)
    game["placing"][pid] += 1
    await q.answer(f"{ship_emoji} {ship_name} چیده شد! ✅")

    next_idx = game["placing"][pid]
    if next_idx < len(SHIPS):
        next_name, next_len, next_emoji = SHIPS[next_idx]
        kb = build_bs_place_keyboard(game, pid)
        text = (
            f"🚢 مرحله چیدن کشتی‌ها\n━━━━━━━━━━━━━━━━━━\n"
            f"✅ {ship_emoji} {ship_name} چیده شد!\n\n"
            f"بعدی: {next_emoji} {next_name} (سایز {next_len})\n\n"
            "روی صفحه کلیک کن"
        )
        await q.edit_message_text(text=text, reply_markup=kb)
    else:
        # همه کشتی‌ها چیده شد
        text = (
            f"🚢 صفحه تو\n━━━━━━━━━━━━━━━━━━\n"
            f"{render_bs_own_grid(game, pid)}\n\n"
            "✅ همه کشتی‌هات چیده شدن!\n"
            "⏳ منتظر حریف بمون..."
        )
        await q.edit_message_text(text=text)

        # اگه هر دو چیدن بازی شروع میشه
        if game["placing"][0]>=len(SHIPS) and game["placing"][1]>=len(SHIPS):
            game["status"]="playing"
            game["turn"]=0
            await start_bs_battle(context, game_id)

async def start_bs_battle(context, game_id):
    game = bs_games[game_id]
    p0_name = game["players"][0][1]
    p1_name = game["players"][1][1]

    for pid in [0,1]:
        is_turn = (game["turn"]==pid)
        text = (
            f"💣 بازی شروع شد!\n━━━━━━━━━━━━━━━━━━\n"
            f"⚔️ {p0_name}  vs  {p1_name}\n\n"
            f"{'🎯 نوبت توئه! یه خونه رو هدف بگیر:' if is_turn else f'⏳ نوبت {p0_name if pid==1 else p1_name}ه...'}\n\n"
            f"📍 صفحه حمله تو:\n{render_bs_target_grid(game, pid)}"
        )
        kb = build_bs_attack_keyboard(game, pid) if is_turn else None
        try:
            sent = await context.bot.send_message(chat_id=game["players"][pid][0], text=text, reply_markup=kb)
            game["msg_ids"][pid]=sent.message_id
        except Exception as e:
            print(f"BS battle start error p{pid}: {e}")

async def handle_bs_attack(update, context, pid_str, r_str, c_str):
    q = update.callback_query
    user = q.from_user
    pid = int(pid_str); r = int(r_str); c = int(c_str)
    game_id = next((gid for gid,g in bs_games.items() if g["players"].get(pid) and g["players"][pid][0]==user.id and g["status"]=="playing"), None)
    if not game_id: await q.answer("بازی پیدا نشد!"); return
    game = bs_games[game_id]

    if game["turn"]!=pid: await q.answer("نوبت تو نیست! 😒", show_alert=True); return
    if game["targets"][pid].get((r,c)) not in (None, WATER): await q.answer("اینجا رو قبلاً زدی! 😂", show_alert=True); return

    enemy_pid = 1-pid
    enemy_grid = game["grids"][enemy_pid]
    cell = enemy_grid.get((r,c), WATER)

    if cell == WATER or cell == MISS:
        # خطا
        game["targets"][pid][(r,c)] = MISS
        result_text = "⚫ دریغ! اشتباه زدی، آب بود 💧"
        await q.answer("⚫ خطا! آب بود...", show_alert=False)
        game["turn"] = enemy_pid
    else:
        # هیت
        game["targets"][pid][(r,c)] = HIT
        game["grids"][enemy_pid][(r,c)] = HIT
        sunk, sunk_cells = check_ship_sunk(game, enemy_pid, r, c)
        if sunk:
            for rr,cc in sunk_cells:
                game["targets"][pid][(rr,cc)] = SUNK
                game["grids"][enemy_pid][(rr,cc)] = SUNK
            ship_emoji = game["ship_grids"][enemy_pid].get((r,c),"🚢")
            result_text = f"🔥 غرق شد! کشتی {ship_emoji} حریفت رو نابود کردی! 💥"
            await q.answer(f"🔥 کشتی غرق شد!", show_alert=True)

            # چک برنده
            enemy_ships = list(game["ship_grids"][enemy_pid].keys())
            enemy_hit = [game["targets"][pid].get((rr,cc)) for rr,cc in enemy_ships]
            if len(enemy_hit)>0 and all(h in (HIT, SUNK) for h in enemy_hit):
                game["status"]="finished"
                game["winner"]=pid
                winner_name = game["players"][pid][1]
                loser_name  = game["players"][enemy_pid][1]
                for p in [0,1]:
                    txt = (
                        "🏆 بازی تموم شد!\n━━━━━━━━━━━━━━━━━━\n"
                        f"{'🎉 تو بردی! همه کشتی‌های حریف رو غرق کردی! 💪' if p==pid else f'💀 باختی! {winner_name} همه کشتی‌هات رو غرق کرد 😭'}\n\n"
                        f"🏆 {winner_name}\n💀 {loser_name}"
                    )
                    try:
                        await context.bot.send_message(chat_id=game["players"][p][0], text=txt)
                    except: pass
                await q.edit_message_text(text=q.message.text+" \n\n🏆 بازی تموم شد!")
                return
        else:
            result_text = f"💥 هیت! کشتی حریف رو زدی! نوبتت ادامه داره 🎯"
            await q.answer("💥 هیت! دوباره بزن!", show_alert=False)
            # نوبت همون بازیکن میمونه چون هیت زده

    p0_name = game["players"][0][1]
    p1_name = game["players"][1][1]

    # آپدیت هر دو بازیکن
    for p in [0,1]:
        is_turn = (game["turn"]==p)
        text = (
            f"💣 بازی دریایی\n━━━━━━━━━━━━━━━━━━\n"
            f"⚔️ {p0_name}  vs  {p1_name}\n\n"
            f"{result_text}\n\n"
            f"{'🎯 نوبت توئه!' if is_turn else f'⏳ نوبت {p0_name if p==1 else p1_name}ه...'}\n\n"
            f"📍 صفحه حمله تو:\n{render_bs_target_grid(game, p)}"
        )
        kb = build_bs_attack_keyboard(game, p) if is_turn else None
        try:
            await context.bot.send_message(chat_id=game["players"][p][0], text=text, reply_markup=kb)
        except Exception as e:
            print(f"BS attack update error p{p}: {e}")

    await q.edit_message_text(text=q.message.text+f"\n\n{result_text}")

# ═══════════════════════════════════════════════
# روتر callback
# ═══════════════════════════════════════════════
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data or ""
    if data == "bs_noop":
        await q.answer()
        return
    if ":" not in data:
        await q.answer()
        return
    parts = data.split(":")
    action = parts[0]
    try:
        if action=="join":           await handle_join(update, context, parts[1])
        elif action=="accept":       await handle_accept(update, context, parts[1])
        elif action=="move":         await handle_ttt_move(update, context, parts[1], int(parts[2]))
        elif action=="rpsjoin":      await handle_rps_join(update, context, parts[1])
        elif action=="rpsaccept":    await handle_rps_accept(update, context, parts[1])
        elif action=="rpsmove":      await handle_rps_move(update, context, parts[1], parts[2])
        elif action=="bsjoin":       await handle_bs_join(update, context, parts[1])
        elif action=="bsaccept":     await handle_bs_accept(update, context, parts[1])
        elif action=="bsrotate":     await handle_bs_rotate(update, context, parts[1])
        elif action=="bsplace":      await handle_bs_place(update, context, parts[1], parts[2], parts[3])
        elif action=="bsattack":     await handle_bs_attack(update, context, parts[1], parts[2], parts[3])
        elif action=="todinljoin":   await handle_tod_inl_join(update, context, parts[1])
        elif action=="todjoin":      await handle_tod_join(update, context, parts[1])
        elif action=="todstart":     await handle_tod_start(update, context, parts[1])
        elif action=="todvote":      await handle_tod_vote(update, context, parts[1], parts[2])
        elif action=="toddone":      await handle_tod_done(update, context, parts[1])
        elif action=="todnext":      await handle_tod_next(update, context, parts[1])
        elif action=="todleave":     await handle_tod_leave(update, context, parts[1])
    except Exception as e:
        print(f"Callback Error: {e}")
        await q.answer("یه چیزی خراب شد 😅", show_alert=True)


async def handle_tod_inl_join(update, context, temp_id):
    q = update.callback_query
    user = q.from_user
    game_id = str(uuid.uuid4())
    # بازی از طریق inline query شروع شده -> chat_id نداریم، فقط inline_message_id داریم
    game = new_tod_game(None, "group", inline_message_id=q.inline_message_id)
    game["players"][user.id] = user.first_name
    tod_games[game_id] = game
    await q.answer("✅ وارد بازی شدی!")
    await q.edit_message_text(
        text=tod_status_text(game, game_id),
        reply_markup=build_join_keyboard(game_id)
    )

async def tod_group_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_tod_group(update, context)

async def tod_private_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_tod_private(update, context)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("grouptod", tod_group_cmd))
    app.add_handler(CommandHandler("privatetod", tod_private_cmd))
    app.add_handler(InlineQueryHandler(inline_query))
    app.add_handler(CallbackQueryHandler(button_callback))
    print("✅ ربات با موفقیت اجرا شد — بریم له کنیم! 😈")
    app.run_polling()

# ═══════════════════════════════════════════════
# 🎮 جرئت و حقیقت
# ═══════════════════════════════════════════════
import asyncio

TOD_TRUTH = [
    "تقلب کردی تو بازی و امتحان؟",
    "عادت بد یا عجیبی که داری؟",
    "کار بچگانه‌ای که هنوز انجام می‌دی؟",
    "یه غذای عجیب که عاشقشی؟",
    "تو بچگی ترس بزرگت چی بود؟",
    "بدترین نمره‌ای که تو مدرسه گرفتی؟",
    "تا حالا تصادف کردی؟",
    "چه فوبیایی داری؟",
    "خجالت‌آورترین کاری که کردی؟",
    "بزرگ‌ترین اشتباهت چی بوده؟",
    "بابت چه کاری و از چه کسی آخرین بار عذرخواهی کردی؟",
    "تا حالا شده کسی رو لو بدی؟",
    "اگه خونت آتش بگیره چه چیزهایی رو برمی‌داری؟",
    "کدوم یکی از افراد این جمع رو با خودت تو جزیره دور افتاده می‌بری؟",
    "دوست داشتی چه سرگرمی یا ورزشی رو تجربه کنی؟",
    "تا حالا چیزی رو بی‌اجازه برداشتی؟",
    "تا حالا شده از رستوران، کافه یا سینما بیرونت کنن؟",
    "عجیب‌ترین کارت توی مکان عمومی؟",
    "برای کنسل کردن برنامه‌هات چه بهانه‌ای آوردی؟",
    "اشتباه بدی که توی مدرسه یا سر کارت انجام دادی؟",
    "کثیف‌ترین کاری که تا حالا کردی؟",
    "آخرین باری که گریه کردی؟",
    "آخرین باری که کسی رو به گریه انداختی؟",
    "طولانی‌ترین مدتی که حمام نرفتی؟",
    "هر چند وقت یکبار حمام می‌ری؟",
    "توی استخر یا زیر دوش دستشویی کردی؟",
    "تا حالا به کسی به دروغ گفتی دوستت دارم؟",
    "چه چیزی رو تو کمدت داری که دوست نداری کسی ببینه؟",
    "بدون کدوم وسیله توی خونت نمی‌تونی زندگی کنی؟",
    "بدترین دعوایی که تا حالا کردی سر چی بوده؟",
    "خواب عجیبی که تا حالا دیدی؟",
    "تا حالا سر کلاس خوراکی خوردی؟",
    "چند کاری که دوست داری یه روزی انجام بدی چیه؟",
    "چه اسمی دوست داری صدات کنن؟",
    "کی و چی حوصله‌ات رو سر می‌بره؟",
    "دوست داشتی به آینده یا گذشته می‌رفتی؟",
    "اگر می‌توانستی به یک زمان خاص در تاریخ برگردی، کدام زمان بود؟",
    "دوست داری چی‌کاره بشی؟",
    "تا حالا یه چیز گرون‌قیمت رو شکستی؟",
    "دوست داشتی چه چیزی رو توی ظاهرت تغییر می‌دادی؟",
    "اگه یه پول خیلی بزرگ داشتی چطوری خرجش می‌کردی؟",
    "خجالت‌آورترین کاری که در فضای مجازی کردی؟",
    "تا حالا راز کسی رو لو دادی؟",
    "دوست داری چندتا بچه داشته باشی؟",
    "چه غذایی رو می‌تونی تا آخر عمر بخوری؟",
    "یه راز که هیچ‌وقت خانوادت نفهمیدن؟",
    "چه کتابی رو دوست داری؟",
    "آخرین پیام به دوست صمیمیت چی بوده؟",
    "بیشتر شبیه مامانتی یا بابات از لحاظ اخلاق؟",
    "کدوم یکی از اعضای خانوادت رو بیشتر دوست داری؟",
    "آخرین باری که گریه کردی کی بوده و چرا؟",
    "تا حالا جلوی کسی گریه کردی؟",
    "اولین کاری که هر روز صبح انجام می‌دی؟",
    "آخرین کاری که هر شب انجام می‌دی؟",
    "عجیب‌ترین کاری که در تنهایی انجام دادی؟",
    "یه خواب تکرارشونده و عجیبت رو بگو؟",
    "مسخره‌ترین لباسی که تا به حال پوشیدی؟",
    "چندتا زبان بلدی؟",
    "تاریخ تولد دوستاتو می‌دونی؟",
    "تو چه فیلمی دوست داشتی بازی کنی؟",
    "دوست داشتی یه فرد سیاسی بودی؟",
    "اگه می‌تونستی اسم کشور رو چی می‌ذاشتی؟",
    "از تاریکی می‌ترسی؟",
    "کدوم محصول تبلیغی رو دوست داری یواشکی بخری؟",
    "تو تنهایی چه کارهایی می‌کنی؟",
    "چند تا سلفی در روز از خودت می‌گیری؟",
    "آخرین بار کی مسواک زدی؟",
    "تا حالا چیزی پیدا کردی که پس ندی؟",
    "تا حالا چیزی از روی زمین برداشتی بخوری؟",
    "بیرون رفتن با مامان و باباتو دوست داری؟",
    "ترس بزرگت چیه؟",
    "چه کار بچگانه‌ای رو هنوز انجام می‌دی؟",
    "لقبی که بهت دادن چی بوده؟",
    "تا حالا خودت رو به مریضی زدی؟",
    "مسواکت رو می‌دی بهترین رفیقت بزنه؟",
    "تا حالا جواب پیام کدوم دوستت ندادی و چرا؟",
    "اگه دوستت بگه به خاطر من دروغ بگو قبول می‌کنی؟",
    "با کی دوست داری دیگه دوست نباشی؟",
    "چه چیزی رو در هر کدوم از افراد این جمع تغییر می‌دی؟",
    "اگه یه پول بزرگ برنده بشی با چه کسانی تقسیم می‌کنی؟",
    "اگه دوستت بوی عرق بدی بده، بهش می‌گی؟",
    "آزاردهنده‌ترین چیز در مورد دوست صمیمیت چیه؟",
    "یه چیزی تو بدنت رو تغییر بدی، اون چیه؟",
    "به کی حسادت می‌کنی؟",
    "دوست داشتی جای کدوم یکی از دوستات بودی؟",
    "چند تا بچه دوست داری در آینده داشته باشی؟",
    "اگه تو یه جزیره گیر بیفتی دوست داری کی کنارت باشه؟",
    "دوست داشتی پسر/دختر بودی؟",
    "اگه بهت پول بدن، غذای چینی می‌خوری؟",
    "حاضری یک سال گوشی کنار بذاری اما با فرد رویاهات ازدواج کنی؟",
    "پنج چیزی که با خودت تو یه جزیره متروک می‌بری چیه؟",
    "مچت رو تو انجام چه کاری گرفتن؟",
    "از کدوم قسمت بدنت خوشت نمیاد؟",
    "دوست داری با کدوم فرد مشهور ازدواج کنی؟",
    "دوست داری چه کاری کنی که نمی‌تونی؟",
    "یه چیزی که آرزو می‌کنی ای کاش هیچ‌وقت نمی‌دیدی؟",
    "بزرگ‌ترین عیب اخلاقیت چیه؟",
    "تا حالا چه دروغی گفتی که عذاب وجدان گرفتی؟",
    "جذاب‌ترین افراد این جمع رو نام ببر",
    "غذایی که ازش متنفری؟",
    "از بین افراد این جمع به کی زنگ نمی‌زنی اگه ماشینت وسط جاده خراب شه؟",
    "اگه نامرئی بودی چه کار می‌کردی؟",
    "از کی چی گرفتی که خوشت نیامده؟",
    "حاضری یک ماه هر روز یه غذای تکراری بخوری؟ چی؟",
    "شبیه کدوم حیوانی؟",
    "وقتی میری توی یک جمع و می‌خوای جذاب به نظر برسی چیکار می‌کنی؟",
    "تا حالا عاشق معلمت یا استادت شدی؟",
    "اگر از خواب بیدار بشی و ببینی جنسیتت عوض شده، پنج کاری که می‌کنی رو بگو",
    "چه بهونه‌ای برای کنسل کردن یا پیچوندن دوستات میاری؟",
    "چه رفتاری ببینی از کسی که می‌خوای پارتنرت باشه، کنسل می‌شی؟",
    "چه کاری هست که انجام دادی اما به هیچ عنوان دیگه انجام نمی‌دی؟",
    "اگر قرار باشه سه تا کاری که هیچ‌کس نفهمه انجام بدی، چیکار می‌کردی؟",
    "دوتا چیزی که وانمود می‌کنی مهم نیست اما خیلی برات مهمه؟",
    "اگه فقط یک نفر رو از ذهنت پاک کنی، اون کی بود؟",
    "اگر امشب آخرین شب زندگیت بود، به چه کسی پیام می‌دادی و چی می‌گفتی؟",
    "آخرین چیزی که امروز روی گوشی جستجو کردی؟",
    "آیا تو دست توی دماغت می‌کنی؟",
    "آیا با خودت جلوی آینه صحبت می‌کنی؟",
    "اگر بفهمی کسی که دوستش داری از دوست صمیمی تو خوشش میاد چیکار می‌کنی؟",
    "تو جذاب‌تری یا بهترین دوستت؟",
    "تا به حال راز دوستات رو به بقیه گفتی؟",
    "اگر مجبور باشی با یکی از دوستات قطع رابطه کنی، اون کیه؟",
    "بیش از همه تحت تأثیر چه کسی هستی؟",
    "شغل مورد علاقه‌ات چیه؟",
    "سلبریتی مورد علاقه‌ات کیه؟",
    "در مورد هر فرد این جمع یک ویژگی مثبت و یک منفی بگو",
    "یک واقعیت آزاردهنده در مورد خودت بگو",
    "اگر بتونی یک معلم رو اخراج کنی، اون کیه و چرا؟",
    "دوست داشتی قدبلندتر باشی؟",
    "عاشق معلم‌ها یا استادات شدی؟",
    "بزرگ‌ترین صدمه‌ای که به کسی زدی چی بوده؟",
    "شده توی دفتر خاطرات کسی فضولی کنی؟",
    "اگه الان قدرت داشتی که یک قانون بذاری که همه مجبور باشن رعایت کنن، اون چیه؟",
    "اون لحظه از زندگیت که خیلی ازش احساس خجالت می‌کنی چیه؟",
    "از نظر احساسی به چه چیزی خیلی وابسته‌ای؟",
    "چه ویژگی از خودت رو دوست داری برای همیشه از دست بدی و چرا؟",
    "بدترین شکستی که توی زندگیت تجربه کردی چی بوده؟",
    "شرم‌آورترین لحظه زندگیت رو توصیف کن",
    "اگر بتونی تا آخر عمر فقط یک فحش بگی، کدوم رو انتخاب می‌کنی؟",
    "کدام حیوان بیشتر به سبک غذاخوردن شما شباهت دارد؟",
    "اکثر مردم چه چیزی رو در مورد شما فرض می‌کنند که درست نیست؟",
    "اولین بار که الکل رو امتحان کردی چند ساله بودی؟",
    "جذاب‌ترین چیز در مورد پسر/دختر چیست؟",
    "اگر با یک جن ملاقات کنی، سه آرزوی شما چه خواهد بود؟",
    "آیا تاکنون از سوپرمارکت دزدی کردی؟",
    "اگر بتونی در بدن شخص دیگری تناسخ پیدا کنی، دوست داری چه کسی بشی؟",
    "عجیب‌ترین کاری که تا به حال جلوی آینه انجام دادی؟",
    "آیا در بزرگسالی به طور تصادفی شلوارت رو خیس کردی؟",
    "روزانه چند عکس سلفی می‌گیری؟",
    "آیا تا به حال از کیف پول پدرت پول دزدیدی؟",
    "آخرین باری که گریه کردی کی بود؟",
    "تا حالا مواد مصرف کردی؟",
    "دوست داری کجا زندگی کنی؟",
    "تا حالا امتحان تقلب کردی؟",
    "آخرین نفری که بهش پیام دادی کی بود؟",
    "تا حالا کسی رو بلاک کردی؟",
    "تا حالا از کسی معذرت‌خواهی کردی که حق با تو بوده؟",
    "بیشتر شب‌بیداری یا سحرخیز؟",
    "آخرین فیلمی که دیدی چی بود؟",
    "دوست داری مشهور بشی؟",
    "از چی زود ناراحت می‌شی؟",
    "تا حالا شده از روی ظاهر کسی قضاوتش کنی؟",
    "اگه یک آرزو داشتی، چی بود؟",
    "دوست داری قدرت پرواز داشته باشی یا نامرئی شدن؟",
    "بیشترین پولی که بیهوده خرج کردی؟",
    "تا حالا چیزی رو گم کردی که خیلی برات مهم بوده؟",
    "اگه مجبور باشی یک ماه بدون اینترنت زندگی کنی، می‌تونی؟",
    "عجیب‌ترین خوابی که دیدی؟",
    "تا حالا پیام رو پاک کردی وانمود کنی نفرستادی؟",
    "عجیب‌ترین غذایی که خوردی؟",
    "اگه حیوان بودی، چی بودی؟",
    "تا حالا وسط خواب حرف زدی؟",
    "تا حالا شده خودت رو توی آینه تشویق کنی؟",
    "اولین چیزی که صبح چک می‌کنی؟",
    "تا حالا شده گوشی رو دنبال کنی در حالی که توی دستت بوده؟",
    "دوست داری ذهن بقیه رو بخونی؟",
    "اگه مجبور باشی یک رنگ باشی، چی می‌شی؟",
    "آخرین نفری که استاکش کردی کی بود؟",
    "اگه فقط یک نفر رو از مخاطبینت نگه داری، کیه؟",
    "عجیب‌ترین سرچت توی اینترنت چی بوده؟",
    "از بین افراد حاضر، اولین نفری که دوست داشتی بیشتر بشناسی کیه؟",
    "تا حالا شده وانمود کنی خوابی تا جواب کسی رو ندی؟",
    "بیشترین زمانی که یک نفر رو سین نکردی چقدر بوده؟",
    "چیزی هست که هیچ‌وقت به خانوادت نگفته باشی؟",
    "تا حالا از روی حسادت کاری کردی؟",
    "بزرگ‌ترین نقطه ضعفت چیه؟",
    "اگه فردا مشهور بشی، اولین کاری که می‌کنی چیه؟",
    "اگه می‌توانستی گذشته را تغییر بدی، چه کاری رو عوض می‌کردی؟",
    "بدترین آهنگی که تو جمع خوندی یا زمزمه کردی؟",
    "خجالت‌آورترین لحظه‌ای که تو مهمونی یا جمع خانوادگی داشتی؟",
    "تا حالا تو خواب راه رفتی یا حرف زدی؟",
    "احمقانه‌ترین ترست از بچگی چی بوده؟",
    "بدترین رقصی که تو عروسی یا مهمونی انجام دادی؟",
    "تا حالا چیزی رو قورت دادی که نباید؟",
    "اگر قرار باشه یک روز مثل یک کودک ۵ ساله رفتار کنی، اولین کاری که می‌کنی چیه؟",
    "وقتی با مشکلی روبرو می‌شی، اول چیکار می‌کنی؟",
    "بزرگ‌ترین ارزشی که تو زندگی برات مهمه چیه؟",
    "تو موقعیت‌های سخت، منطقی هستی یا احساسی؟",
    "چطور با شکست کنار میای؟",
    "اگر قرار باشه بین پول زیاد و خوشحالی واقعی یکی رو انتخاب کنی، کدوم؟",
    "تو روابط دوستانه، بیشتر آدم بخشنده‌ای یا انتظار داری؟",
    "چیزی که توی دیگران تحملش رو نداری چیه؟",
    "وقتی عصبانی می‌شی، چطور خالی می‌کنی؟",
    "دوست داری دیگران تو رو چطور به یاد بیارن؟",
    "تو زندگی، بیشتر به گذشته فکر می‌کنی، حال یا آینده؟",
    "چقدر راحت نظرات مخالف رو قبول می‌کنی؟",
    "اگر قرار باشه یک ویژگی شخصیتت رو به همه هدیه بدی، چی باشه؟",
    "چقدر به حس درونی خودت اعتماد داری؟",
    "بهترین خاطره دوران کودکی‌ت چیه؟",
    "اگر بتونی به هر جای دنیا سفر کنی، اولین مقصدت کجاست؟",
    "غذای مورد علاقه‌ت چیه و چرا؟",
    "تا حالا عاشق شدی؟ چند بار؟",
    "بزرگ‌ترین هدفت تو پنج سال آینده چیه؟",
    "کتاب، فیلم یا سریالی که خیلی تأثیرگذار بوده برات چیه؟",
    "بهترین دوستت چه ویژگی‌ای داره که خیلی دوستش داری؟",
    "اگر یک روز پول نامحدود داشته باشی، اولین کاری که می‌کنی چیه؟",
    "سرگرمی مورد علاقه‌ت چیه؟",
    "تا حالا تجربه بیماری یا تصادف جدی داشتی؟",
    "اگر بتونی یک مهارت جدید یاد بگیری، چی رو انتخاب می‌کنی؟",
    "اگر یک روز صدای همه حیوانات رو بفهمی، اولین سوالی که از سگ یا گربه می‌پرسی چیه؟",
    "اگر قرار باشه موهاتو هر رنگی کنی، چه رنگی می‌زنی که همه شوکه بشن؟",
    "تا حالا چیزی رو از یخچال دزدیدی و بعد تقصیر کسی انداختی؟",
    "وقتی کسی بهت دروغ می‌گه، چطور واکنش نشون می‌دی؟",
    "تو زندگی بیشتر آدم ریسک‌پذیری هستی یا محتاط؟",
    "چقدر به تعهدات و قول‌هات پایبندی؟",
    "بزرگ‌ترین نقطه ضعف شخصیتیت از نظر خودته چیه؟",
    "وقتی موفق می‌شی، با دیگران جشن می‌گیری یا تنهایی لذت می‌بری؟",
    "اگر قرار باشه بین عدالت و مهربونی یکی رو انتخاب کنی، کدوم؟",
    "چقدر راحت احساساتت رو با دیگران در میان می‌ذاری؟",
    "تو موقعیت‌های استرس‌زا، آرامش خودتو حفظ می‌کنی یا زود عصبی می‌شی؟",
    "وقتی کسی نیاز به کمک داره، اول به فکر خودت هستی یا سریع کمک می‌کنی؟",
    "تو بحث‌ها بیشتر منطقی بحث می‌کنی یا احساسی؟",
    "بهترین سفر یا تعطیلاتی که تا حالا رفتی کجا بوده؟",
    "شغل رویایی کودکی‌ت چی بوده؟",
    "اگر بتونی با یک شخصیت تاریخی یه ساعت حرف بزنی، کی باشه؟",
    "بزرگ‌ترین درس زندگی که تا حالا یاد گرفتی چیه؟",
    "تا حالا ورزش حرفه‌ای یا جدی انجام دادی؟",
    "رابطه‌ت با خواهر/برادرت چطوره؟",
    "تا حالا تو بیمارستان بستری شدی؟ خاطره‌اش چیه؟",
    "رویای دوران نوجوانی‌ت که هنوزم گاهی بهش فکر می‌کنی چیه؟",
    "بهترین معلم یا استاد زندگی‌ت کی بوده و چرا؟",
    "از نظرت موفقیت یعنی چی؟",
    "دوست داری بیشتر به خاطر هوشت شناخته بشی یا شخصیتت؟",
    "چه چیزی باعث می‌شه احترامت رو یک نفر از دست بده؟",
    "چه چیزی باعث می‌شه بدون فکر به کسی اعتماد کنی؟",
    "از چه نوع آدم‌هایی خوشت نمیاد؟",
    "از بین عشق، خانواده و دوست، کدوم اولویته؟",
    "اگر خیانت ببینی، می‌بخشی؟",
    "چه چیزی باعث می‌شه رابطه رو تموم کنی؟",
    "تا حالا کسی رو بدون اینکه بفهمه دوست داشتی؟",
    "دوست داری طرف مقابل اولین قدم رو برداره یا خودت؟",
    "حسادت رو طبیعی می‌دونی؟",
    "بیشتر عاشق عقل می‌شی یا احساس؟",
    "اگر عشقت با بهترین دوستت دشمن باشه، طرف کی رو می‌گیری؟",
    "دوست داری بیشتر دوست داشته بشی یا درک بشی؟",
    "مهم‌ترین ویژگی شریک زندگیت باید چی باشه؟",
    "وقتی ناراحتی، تنهایی رو ترجیح می‌دی یا حرف زدن؟",
    "از شکست بیشتر می‌ترسی یا از امتحان نکردن؟",
    "دوست داری رهبر باشی یا عضو تیم؟",
    "بیشتر درونگرایی یا برونگرا؟",
    "زود می‌بخشی؟",
    "اگر کسی بهت توهین کنه، جواب می‌دی یا بی‌خیال می‌شی؟",
    "دوست داری برنامه‌ریزی داشته باشی یا لحظه‌ای زندگی کنی؟",
    "بیشتر به گذشته فکر می‌کنی یا آینده؟",
    "اگر یک میلیارد پول بگیری ولی نتونی به کسی بگی، قبول می‌کنی؟",
    "اگر می‌توانستی یک حقیقت دنیا رو بفهمی، چی رو انتخاب می‌کردی؟",
    "اگر مجبور باشی یک نفر رو برای نجات جان پنج نفر قربانی کنی، انجام می‌دی؟",
    "اگر بدونی هیچ‌کس متوجه نمی‌شه، قانون‌شکنی می‌کنی؟",
    "اگر قدرت خوندن ذهن داشته باشی، ازش استفاده می‌کنی؟",
    "اگر مشهور بشی، حاضری حریم خصوصیت از بین بره؟",
    "اگر تا آخر عمر فقط یک احساس داشته باشی، شادی رو انتخاب می‌کنی یا آرامش؟",
    "فکر می‌کنی بزرگ‌ترین ویژگی مثبتت چیه؟",
    "دوست داری مردم بعد از آشنایی باهات چی بگن؟",
    "از خودت بیشتر به چی افتخار می‌کنی؟",
    "اگر دوباره متولد بشی، باز خودت بودن رو انتخاب می‌کنی؟",
    "چیزی هست که هیچ‌وقت نتونستی خودت رو بابتش ببخشی؟",
    "بیشتر از چی پشیمونی؟",
    "بزرگ‌ترین ترست که کمتر کسی می‌دونه چیه؟",
    "چه چیزی سریع حالت رو خوب می‌کنه؟",
    "اگر بخوای خودت رو در سه کلمه توصیف کنی، چی می‌گی؟",
    "دوست داری پنج سال دیگه چه آدمی باشی؟",
    "به نظرت تنهایی خوبه یا بده؟",
    "اگر همه حافظه‌شون از تو پاک بشه، چه حسی داری؟",
    "خوشبختی رو چطور تعریف می‌کنی؟",
    "اگر هیچ پولی وجود نداشت، دوست داشتی چه کاری انجام بدی؟",
    "فکر می‌کنی انسان‌ها تغییر می‌کنن یا فقط نقابشون عوض می‌شه؟",
    "به نظرت مهم‌تره آدم موفق باشه یا آدم خوبی؟",
]

TOD_DARE = [
    "زبونت رو بزن به نوک بینیت! عکس بفرست",
    "اسم پروفایلت رو ۱۰ دقیقه به «من باختم» تغییر بده",
    "سه نفر حاضر رو با یک کلمه توصیف کن",
    "یک جمله انگیزشی از خودت بساز",
    "یک متن عاشقانه بداهه بنویس",
    "یک جمله با هر حرف الفبا پشت سر هم بساز",
    "تا یک دقیقه فقط با ایموجی ارتباط برقرار کن",
    "یه جمله بنویس بدون استفاده از حرف الف",
    "پنج حیوان رو در کمتر از ۵ ثانیه نام ببر",
    "از یک شیء کنار خودت عکس هنری بگیر و ارسال کن",
    "به صورت مداوم ۱ دقیقه صدای حیوون دربیار!",
    "یه داستان خنده‌دار در مورد یکی از افراد این جمع بساز!",
    "آرنجت رو لیس بزن! عکس بفرست",
    "آخرین باری که به کسی دایرکت دادی رو بخون",
    "یه شعر عاشقانه کوتاه بگو!",
    "یکی از عکس‌های قدیمی و خنده‌دار از خودت رو بذار",
    "با دستمال توالت سرت رو ببند و عکس بفرست!",
    "یکی از بدترین اسکرین‌شات‌هایی که داری رو نشون بده",
    "بدترین پیام یک ماه اخیر خودت رو بخون",
    "بک‌گراند گوشیت رو عکس یکی از افراد جمع بذار!",
    "به برادر/خواهرت یه پیام بده و فقط بگو سلام!",
    "یک ویس ۱۰ ثانیه‌ای با صدای خنده بفرست",
    "تا دور بعد فقط با ایموجی جواب بده",
    "یک لطیفه تعریف کن",
    "سه نفر گروه را با یک کلمه توصیف کن",
    "یک شعر بخوان",
    "یک جمله انگیزشی از خودت بنویس",
    "یک چیستان بگو",
    "اسم خودت رو برعکس بنویس",
    "تا یک دقیقه فقط با گیف جواب بده",
    "یک خاطره خنده‌دار تعریف کن",
    "اسم پنج شهر رو در ۱۰ ثانیه بنویس",
    "پنج حیوان با حرف م بنویس",
    "یک جمله بدون نقطه بنویس",
    "یک جمله فقط با ایموجی بنویس تا بقیه حدس بزنن",
    "یک آهنگ رو با متن ادامه بده",
    "یک جمله با هر حرف الفبا شروع کن",
    "از یک وسیله کنار خودت عکس بفرست",
    "اسم سه فیلم بگو",
    "تا دور بعد فقط با بله یا نه جواب بده",
    "تو استوری لینک آخرین ویدیویی که توی یوتیوب دیدی رو بزار!",
    "تا دور بعد آخر هر جمله اموجی خنده بذار",
    "با چشمای بسته یه پیام برای یکی بفرست!",
    "اسم پروفایلت رو ۵ دقیقه تغییر بده",
    "یک شعر کودکانه بخون",
    "یک جمله رو برعکس تایپ کن",
    "با چشم بسته یک پیام بنویس",
    "یک داستان سه جمله‌ای بساز",
    "خودت رو با یک شخصیت کارتونی مقایسه کن",
    "فقط با GIF صحبت کن تا نوبت بعد",
    "اسم یک فیلم رو با ایموجی توضیح بده",
    "یک معما بساز",
    "یک جمله با ۱۰ ایموجی مختلف بنویس",
    "از بقیه بخواهند یک کلمه بدهند و با آن داستان بسازی",
    "اسم یک نفر حاضر را با سه ویژگی مثبت توصیف کن",
    "یک خاطره شرم‌آور تعریف کن",
    "تا دور بعد هر پیام رو با قربان شما شروع کن",
    "از یه نفر تو جمع یه پست تعریف و تمجید کن!",
    "یه استوری بزار از خودت و بگو خیلی خوش‌شانسی!",
    "تا ۲ دقیقه از بله و نه استفاده نکن!",
    "ناخن‌هات رو با مداد رنگی یا ماژیک لاک بزن!",
    "سرت رو بکن توی یقه‌ات و تا دور بعدی همونجا بمون!",
    "به یکی از افراد گروه تاریخچه سرچت رو نشون بده!",
    "از کلمه لطفا تا آخر بازی توی همه جملاتت استفاده کن!",
    "فکر کن برنده جایزه مهمی شدی و شروع کن به سخنرانی!",
    "فکر کن بازنشسته‌ای و داری آخرین حرفات رو می‌زنی!",
    "آخرین پیامت رو با صدای بلند بخون",
    "به هر کدوم از افراد بگو شکل کدوم شخصیت مشهورن!",
    "یه آهنگ بذار و تا آخرش اداشو دربیار",
    "با صدای گزارشگر، بازی رو گزارش کن!",
    "یه لقب برای هر کسی انتخاب کن!",
    "با یکی از مخاطبینت تماس بگیر و بگو تولدت مبارک!",
    "یک استایل بامزه بگیر و سلفی بفرست برای همه",
    "توی اینستاگرامت یه عکس مسخره از خودت پست کن!",
    "فقط با GIF صحبت کن تا نوبت بعد",
]

# وضعیت بازی‌های جرئت و حقیقت
tod_games = {}

def new_tod_game(chat_id, mode, inline_message_id=None):
    return {
        "chat_id": chat_id,
        "inline_message_id": inline_message_id,  # فقط وقتی بازی از طریق inline query شروع بشه پر می‌شه
        "mode": mode,           # "group" یا "private"
        "players": {},          # {user_id: name}
        "status": "joining",    # joining / voting / playing / finished
        "used_truth": [],
        "used_dare": [],
        "current_q": None,
        "current_type": None,   # "truth" یا "dare"
        "votes": {},            # {user_id: "truth"/"dare"}
        "done_votes": {},       # {user_id: True}
        "next_votes": {},       # {user_id: True}
        "answerer": None,       # user_id
        "asker": None,          # user_id (حالت نفر به نفر)
        "last_answerers": [],   # برای جلوگیری از تکرار
        "timer_task": None,
        "msg_id": None,
    }

async def tod_deliver(context, game, text, reply_markup=None):
    """
    پیام رو تحویل میده:
    - اگه بازی از طریق inline query شروع شده باشه (inline_message_id داره)،
      همون یک پیام inline رو ادیت می‌کنه (چون chat_id نداریم و نمی‌تونیم پیام جدید بفرستیم).
    - در غیر این صورت (بازی گروهی/خصوصی معمولی)، یه پیام جدید به chat_id می‌فرسته.
    """
    if game.get("inline_message_id"):
        try:
            await context.bot.edit_message_text(
                inline_message_id=game["inline_message_id"],
                text=text,
                reply_markup=reply_markup
            )
        except Exception as e:
            print(f"TOD inline deliver error: {e}")
    else:
        try:
            msg = await context.bot.send_message(
                chat_id=game["chat_id"], text=text, reply_markup=reply_markup
            )
            game["msg_id"] = msg.message_id
        except Exception as e:
            print(f"TOD deliver error: {e}")

def tod_random_question(game, qtype):
    if qtype == "truth":
        pool = [q for q in TOD_TRUTH if q not in game["used_truth"]]
        if not pool:
            game["used_truth"] = []
            pool = TOD_TRUTH[:]
    else:
        pool = [q for q in TOD_DARE if q not in game["used_dare"]]
        if not pool:
            game["used_dare"] = []
            pool = TOD_DARE[:]
    q = random.choice(pool)
    if qtype == "truth":
        game["used_truth"].append(q)
    else:
        game["used_dare"].append(q)
    return q

def tod_pick_answerer(game):
    players = list(game["players"].keys())
    if len(players) < 2:
        return None, None
    # جلوگیری از تکرار پشت سر هم
    candidates = [p for p in players if p not in game["last_answerers"]]
    if not candidates:
        candidates = players[:]
    answerer = random.choice(candidates)
    asker_candidates = [p for p in players if p != answerer]
    asker = random.choice(asker_candidates)
    # آپدیت تاریخچه
    game["last_answerers"].append(answerer)
    if len(game["last_answerers"]) > max(1, len(players)//2):
        game["last_answerers"].pop(0)
    return answerer, asker

def build_join_keyboard(game_id):
    btns = [
        [InlineKeyboardButton("✅ شرکت در بازی", callback_data=f"todjoin:{game_id}")],
        [InlineKeyboardButton("▶️ شروع بازی", callback_data=f"todstart:{game_id}")],
    ]
    return InlineKeyboardMarkup(btns)

def build_vote_keyboard(game_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟢 حقیقت", callback_data=f"todvote:{game_id}:truth"),
            InlineKeyboardButton("🔴 جرئت",  callback_data=f"todvote:{game_id}:dare"),
        ],
        [InlineKeyboardButton("🚪 خروج از بازی", callback_data=f"todleave:{game_id}")],
    ])

def build_done_keyboard(game_id, qtype, is_asker=False):
    if qtype == "truth":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ جواب دادم", callback_data=f"toddone:{game_id}")],
            [InlineKeyboardButton("🚪 خروج از بازی", callback_data=f"todleave:{game_id}")],
        ])
    else:
        if is_asker:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ انجام شد (تأیید پرسشگر)", callback_data=f"toddone:{game_id}")],
                [InlineKeyboardButton("🚪 خروج از بازی", callback_data=f"todleave:{game_id}")],
            ])
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🚪 خروج از بازی", callback_data=f"todleave:{game_id}")],
        ])

def build_next_keyboard(game_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ سوال بعدی", callback_data=f"todnext:{game_id}")],
        [InlineKeyboardButton("🚪 خروج از بازی", callback_data=f"todleave:{game_id}")],
    ])

def tod_status_text(game, game_id):
    n = len(game["players"])
    names = "، ".join(game["players"].values()) if game["players"] else "—"
    return (
        "🎮 جرئت و حقیقت\n━━━━━━━━━━━━━━━━━━\n"
        f"👥 بازیکنان ({n} نفر): {names}\n\n"
        "برای شرکت روی دکمه بزن!\n"
        "وقتی آماده‌اید ▶️ شروع رو بزن"
    )

async def tod_send_vote(context, game, game_id):
    game["status"] = "voting"
    game["votes"] = {}
    game["done_votes"] = {}
    game["next_votes"] = {}
    n = len(game["players"])
    answerer_name = game["players"].get(game["answerer"], "؟")
    asker_name = game["players"].get(game["asker"], "؟") if game["asker"] else None

    if game["mode"] == "group":
        text = (
            "🎮 جرئت و حقیقت\n━━━━━━━━━━━━━━━━━━\n"
            f"👥 {n} نفر در بازی\n\n"
            f"🎯 نوبت: {answerer_name}\n\n"
            "📊 رأی بدید — حقیقت یا جرئت؟\n"
            "وقتی ۷۰٪ رأی دادن، سوال میاد!"
        )
    else:
        text = (
            "🎮 جرئت و حقیقت\n━━━━━━━━━━━━━━━━━━\n"
            f"🎯 جواب‌دهنده: {answerer_name}\n"
            f"❓ پرسشگر: {asker_name}\n\n"
            f"⬇️ {answerer_name} انتخاب کن!"
        )

    await tod_deliver(context, game, text, build_vote_keyboard(game_id))

async def tod_send_question(context, game, game_id, qtype):
    game["status"] = "playing"
    game["current_type"] = qtype
    game["current_q"] = tod_random_question(game, qtype)
    answerer_name = game["players"].get(game["answerer"], "؟")
    asker_name = game["players"].get(game["asker"], "؟") if game["asker"] else None
    emoji = "🟢 حقیقت" if qtype == "truth" else "🔴 جرئت"
    n = len(game["players"])

    if game["mode"] == "group":
        text = (
            f"🎮 جرئت و حقیقت\n━━━━━━━━━━━━━━━━━━\n"
            f"👥 {n} نفر | {emoji}\n\n"
            f"🎯 نوبت: {answerer_name}\n\n"
            f"❓ {game['current_q']}\n\n"
            f"⏰ ۳ دقیقه وقت داری!"
        )
        kb = build_done_keyboard(game_id, qtype)
    else:
        if qtype == "dare":
            text = (
                f"🎮 جرئت و حقیقت\n━━━━━━━━━━━━━━━━━━\n"
                f"🔴 جرئت!\n\n"
                f"🎯 {answerer_name} باید انجام بده:\n"
                f"❓ {game['current_q']}\n\n"
                f"⏰ ۳ دقیقه وقت داری!\n"
                f"✅ {asker_name} باید تأیید کنه"
            )
            kb = build_done_keyboard(game_id, qtype, is_asker=False)
        else:
            text = (
                f"🎮 جرئت و حقیقت\n━━━━━━━━━━━━━━━━━━\n"
                f"🟢 حقیقت!\n\n"
                f"🎯 {answerer_name} جواب بده:\n"
                f"❓ {game['current_q']}\n\n"
                f"⏰ ۳ دقیقه وقت داری!"
            )
            kb = build_done_keyboard(game_id, qtype)

    await tod_deliver(context, game, text, kb)

    # تایمر ۳ دقیقه
    if game["timer_task"]:
        game["timer_task"].cancel()
    game["timer_task"] = asyncio.create_task(tod_timer(context, game, game_id))

async def tod_timer(context, game, game_id):
    try:
        await asyncio.sleep(180)  # ۳ دقیقه
        if game.get("status") == "playing" and tod_games.get(game_id) is game:
            answerer_name = game["players"].get(game["answerer"], "؟")
            await tod_deliver(context, game, f"⏰ زمان {answerer_name} تموم شد! رفتیم دور بعد 😂")
            await tod_next_round(context, game, game_id)
    except asyncio.CancelledError:
        pass

async def tod_next_round(context, game, game_id):
    if len(game["players"]) < 2:
        await tod_deliver(context, game, "😢 بازیکنان کافی نیستن. بازی تموم شد!")
        tod_games.pop(game_id, None)
        return
    game["answerer"], game["asker"] = tod_pick_answerer(game)
    await tod_send_vote(context, game, game_id)

# ─── هندلرهای TOD ───────────────────────────────
async def handle_tod_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    game_id = str(uuid.uuid4())
    game = new_tod_game(chat_id, "group")
    game["players"][user.id] = user.first_name
    tod_games[game_id] = game
    await update.message.reply_text(
        text=tod_status_text(game, game_id),
        reply_markup=build_join_keyboard(game_id)
    )

async def handle_tod_private(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    game_id = str(uuid.uuid4())
    game = new_tod_game(chat_id, "private")
    game["players"][user.id] = user.first_name
    tod_games[game_id] = game
    await update.message.reply_text(
        text=(
            "🎮 جرئت و حقیقت — حالت نفر به نفر\n━━━━━━━━━━━━━━━━━━\n"
            f"👤 {user.first_name} وارد شد!\n\n"
            "منتظر بازیکن دوم...\n"
            "دوستت روی دکمه بزنه تا شروع بشه!"
        ),
        reply_markup=build_join_keyboard(game_id)
    )

async def handle_tod_join(update, context, game_id):
    q = update.callback_query
    user = q.from_user
    game = tod_games.get(game_id)
    if not game: await q.answer("بازی پیدا نشد!", show_alert=True); return
    if game["status"] != "joining": await q.answer("بازی شروع شده!", show_alert=True); return
    if user.id in game["players"]: await q.answer("قبلاً وارد شدی! 😄", show_alert=True); return
    game["players"][user.id] = user.first_name
    await q.answer(f"✅ {user.first_name} وارد بازی شد!")
    try:
        await q.edit_message_text(
            text=tod_status_text(game, game_id),
            reply_markup=build_join_keyboard(game_id)
        )
    except: pass

async def handle_tod_start(update, context, game_id):
    q = update.callback_query
    user = q.from_user
    game = tod_games.get(game_id)
    if not game: await q.answer("بازی پیدا نشد!", show_alert=True); return
    if game["status"] != "joining": await q.answer("بازی شروع شده!", show_alert=True); return
    if len(game["players"]) < 2: await q.answer("حداقل ۲ نفر لازمه! 😅", show_alert=True); return
    await q.answer("🎉 بازی شروع شد!")
    game["answerer"], game["asker"] = tod_pick_answerer(game)
    try:
        await q.edit_message_text(
            text=(
                "🎮 جرئت و حقیقت — بازی شروع شد!\n━━━━━━━━━━━━━━━━━━\n"
                f"👥 {len(game['players'])} بازیکن\n"
                "بریم! 🔥"
            )
        )
    except: pass
    await tod_send_vote(context, game, game_id)

async def handle_tod_vote(update, context, game_id, vtype):
    q = update.callback_query
    user = q.from_user
    game = tod_games.get(game_id)
    if not game: await q.answer("بازی پیدا نشد!"); return
    if game["status"] != "voting": await q.answer("الان وقت رأی نیست!", show_alert=True); return
    if user.id not in game["players"]: await q.answer("تو بازیکن این بازی نیستی!", show_alert=True); return

    if game["mode"] == "private":
        # فقط جواب‌دهنده رأی میده
        if user.id != game["answerer"]: await q.answer("فقط جواب‌دهنده انتخاب می‌کنه!", show_alert=True); return
        await q.answer(f"{'🟢 حقیقت' if vtype=='truth' else '🔴 جرئت'} انتخاب شد!")
        await tod_send_question(context, game, game_id, vtype)
        return

    # حالت گروهی
    if user.id in game["votes"]: await q.answer("قبلاً رأی دادی!", show_alert=True); return
    game["votes"][user.id] = vtype
    await q.answer(f"رأیت ثبت شد! {'🟢' if vtype=='truth' else '🔴'}")

    n = len(game["players"])
    total_votes = len(game["votes"])
    truth_votes = sum(1 for v in game["votes"].values() if v=="truth")
    dare_votes  = sum(1 for v in game["votes"].values() if v=="dare")

    # ۷۰٪ رأی
    threshold = max(1, int(n * 0.7))
    answerer_name = game["players"].get(game["answerer"], "؟")
    if truth_votes >= threshold:
        await tod_send_question(context, game, game_id, "truth")
    elif dare_votes >= threshold:
        await tod_send_question(context, game, game_id, "dare")
    else:
        try:
            await q.edit_message_text(
                text=(
                    "🎮 جرئت و حقیقت\n━━━━━━━━━━━━━━━━━━\n"
                    f"👥 {n} نفر | 🎯 نوبت: {answerer_name}\n\n"
                    f"📊 رأی‌ها: 🟢 {truth_votes}  |  🔴 {dare_votes}\n"
                    f"({total_votes} از {n} نفر رأی دادن)\n\n"
                    "وقتی ۷۰٪ رأی دادن سوال میاد!"
                ),
                reply_markup=build_vote_keyboard(game_id)
            )
        except: pass

async def handle_tod_done(update, context, game_id):
    q = update.callback_query
    user = q.from_user
    game = tod_games.get(game_id)
    if not game: await q.answer("بازی پیدا نشد!"); return
    if game["status"] != "playing": await q.answer("الان وقتش نیست!", show_alert=True); return
    if user.id not in game["players"]: await q.answer("تو بازیکن این بازی نیستی!", show_alert=True); return

    qtype = game["current_type"]
    n = len(game["players"])

    if game["mode"] == "private" and qtype == "dare":
        # فقط پرسشگر تأیید می‌کنه
        if user.id != game["asker"]: await q.answer("فقط پرسشگر می‌تونه تأیید کنه!", show_alert=True); return
        await q.answer("✅ تأیید شد! رفتیم دور بعد 🎉")
        if game["timer_task"]: game["timer_task"].cancel()
        await tod_next_round(context, game, game_id)
        return

    if game["mode"] == "private" and qtype == "truth":
        # جواب‌دهنده تأیید می‌کنه
        if user.id != game["answerer"]: await q.answer("فقط جواب‌دهنده می‌تونه!", show_alert=True); return
        await q.answer("✅ ثبت شد!")
        if game["timer_task"]: game["timer_task"].cancel()
        await tod_next_round(context, game, game_id)
        return

    # حالت گروهی
    if user.id in game["done_votes"]: await q.answer("قبلاً زدی!", show_alert=True); return
    game["done_votes"][user.id] = True
    done_count = len(game["done_votes"])
    threshold = max(1, int(n * 0.5))
    await q.answer(f"✅ ثبت شد! ({done_count}/{n})")

    if done_count >= threshold:
        if game["timer_task"]: game["timer_task"].cancel()
        answerer_name = game["players"].get(game["answerer"], "؟")
        try:
            await q.edit_message_text(
                text=(
                    f"✅ {answerer_name} جواب داد!\n\n"
                    "آماده‌اید برید سوال بعدی؟"
                ),
                reply_markup=build_next_keyboard(game_id)
            )
        except: pass
    else:
        try:
            await q.edit_message_text(
                text=(
                    f"🎮 {game['current_q']}\n\n"
                    f"✅ {done_count} از {n} نفر تأیید کردن\n"
                    f"(نیاز به {threshold} نفر)"
                ),
                reply_markup=build_done_keyboard(game_id, qtype)
            )
        except: pass

async def handle_tod_next(update, context, game_id):
    q = update.callback_query
    user = q.from_user
    game = tod_games.get(game_id)
    if not game: await q.answer("بازی پیدا نشد!"); return
    if user.id not in game["players"]: await q.answer("تو بازیکن این بازی نیستی!", show_alert=True); return
    if user.id in game["next_votes"]: await q.answer("قبلاً زدی!", show_alert=True); return
    game["next_votes"][user.id] = True
    n = len(game["players"])
    next_count = len(game["next_votes"])
    threshold = max(1, int(n * 0.7))
    await q.answer(f"رأیت ثبت شد! ({next_count}/{n})")
    if next_count >= threshold:
        await tod_next_round(context, game, game_id)
    else:
        try:
            await q.edit_message_text(
                text=(
                    "آماده‌اید برید سوال بعدی؟\n"
                    f"({next_count} از {n} نفر موافقن)"
                ),
                reply_markup=build_next_keyboard(game_id)
            )
        except: pass

async def handle_tod_leave(update, context, game_id):
    q = update.callback_query
    user = q.from_user
    game = tod_games.get(game_id)
    if not game: await q.answer("بازی پیدا نشد!", show_alert=True); return
    if user.id not in game["players"]: await q.answer("تو تو این بازی نیستی!", show_alert=True); return
    del game["players"][user.id]
    await q.answer(f"🚪 {user.first_name} از بازی خارج شد")
    await tod_deliver(context, game, f"🚪 {user.first_name} از بازی خارج شد.\n👥 {len(game['players'])} نفر باقی مونده")
    if len(game["players"]) < 2:
        if game.get("timer_task"): game["timer_task"].cancel()
        await tod_deliver(context, game, "😢 بازیکنان کافی نیستن. بازی تموم شد!")
        tod_games.pop(game_id, None)

if __name__ == "__main__":
    main()

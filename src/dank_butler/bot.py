import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dank_butler.config import Config
from dank_butler.meme_engine import MemeEngine

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Global engine instance to be initialized inside run_bot
engine: MemeEngine = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Greetings! I am *Dank Butler*, your personal meme concierge.\n\n"
        "🔍 *Describe a meme* → I'll fetch it from the internet archives.\n"
        "🖼 *Send me a meme image* → I'll explain its origin and context.\n\n"
        "Try: _'that dog sitting in a burning room saying this is fine'_",
        parse_mode="Markdown"
    )


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧐 Analyzing your meme, please give me a moment...")
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)

    # download to memory for python-telegram-bot v20+ compatibility
    out_bytes = bytearray()
    await file.download_to_memory(out_bytes)

    explanation = await engine.explain_meme(bytes(out_bytes))
    await update.message.reply_text(explanation, parse_mode="Markdown")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text.strip()
    if len(description) < 5:
        await update.message.reply_text("Please give your butler a bit more detail to search for! 😅")
        return

    msg = await update.message.reply_text("🕵️ Butler is scouring the web for your meme...")

    result = await engine.find_meme(description)

    if not result:
        await msg.edit_text("😔 I searched far and wide but couldn't find that meme. Try describing it differently!")
        return

    await msg.edit_text(f"✅ Found it! _{result['source']}_", parse_mode="Markdown")

    if result["type"] == "gif":
        await update.message.reply_animation(
            animation=result["url"],
            caption=f"*{result['title']}*\n\n{result.get('explanation', '')}",
            parse_mode="Markdown"
        )
    elif result["type"] == "image":
        await update.message.reply_photo(
            photo=result["url"],
            caption=f"*{result['title']}*\n\n{result.get('explanation', '')}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"*{result['title']}*\n\n{result.get('explanation', '')}\n\n🔗 {result['url']}",
            parse_mode="Markdown"
        )


def run_bot():
    global engine
    config = Config.load()
    engine = MemeEngine(config)

    app = Application.builder().token(config.telegram_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Dank Butler is running...")
    app.run_polling()

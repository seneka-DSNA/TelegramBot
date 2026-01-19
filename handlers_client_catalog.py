from telegram import Update
from telegram.ext import ContextTypes
from pathlib import Path

CATALOG_IMAGE_PATH = Path("Catalogo/catalog_1.png")



async def client_catalog_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not CATALOG_IMAGE_PATH.exists():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Catálogo no disponible en este momento."
        )
        return

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open(CATALOG_IMAGE_PATH, "rb"),
        caption=(
            "📦 *Catálogo de productos*\n\n"
            "Usa los nombres o referencias del catálogo para realizar tu pedido."
        ),
        parse_mode="Markdown"
    )


import asyncio
from datetime import datetime, time, timedelta
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import logging

# --- CONFIGURAÇÕES ---
BOT_TOKEN = "CO8477842120:AAF9qg6-84vhgEpTW_WKlCSqwv135TPRWVI"
SOURCE_CHAT_ID = -4945037700   # grupo onde você coloca os posts prontos
TARGET_CHAT_ID = -1002261068752   # grupo onde o bot vai postar automaticamente
POST_HOUR = 10  # hora da postagem (ex: 10 = 10h da manhã)

# --- LOG ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- FUNÇÕES ---
async def copiar_ultimo_post(bot: Bot):
    """Copia o último post do grupo SOURCE e envia pro grupo TARGET"""
    try:
        mensagens = await bot.get_chat_history(chat_id=SOURCE_CHAT_ID, limit=1)
        if not mensagens:
            print("Nenhuma mensagem encontrada no grupo fonte.")
            return

        msg = mensagens[0]
        caption = msg.caption or msg.text or ""

        # envia conforme o tipo
        if msg.photo:
            await bot.send_photo(chat_id=TARGET_CHAT_ID, photo=msg.photo[-1].file_id, caption=caption)
        elif msg.video:
            await bot.send_video(chat_id=TARGET_CHAT_ID, video=msg.video.file_id, caption=caption)
        else:
            await bot.send_message(chat_id=TARGET_CHAT_ID, text=caption)

        print(f"✅ Postagem enviada para o grupo destino às {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"❌ Erro ao copiar post: {e}")

async def agendar_post(bot: Bot):
    """Agenda a postagem para o horário configurado"""
    while True:
        agora = datetime.now()
        proximo = datetime.combine(agora.date(), time(POST_HOUR))  # hora configurada
        if agora >= proximo:
            proximo += timedelta(days=1)  # joga pra amanhã se já passou

        tempo_espera = (proximo - agora).total_seconds()
        print(f"⏰ Próxima postagem programada para: {proximo.strftime('%H:%M:%S')}")
        await asyncio.sleep(tempo_espera)
        await copiar_ultimo_post(bot)

async def start(update, context):
    await update.message.reply_text("🚀 Bot de postagens automáticas ativo!")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    bot = Bot(BOT_TOKEN)
    asyncio.create_task(agendar_post(bot))  # roda em paralelo

    print("🤖 Bot rodando...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

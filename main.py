from telegram.ext import ApplicationBuilder, ContextTypes
from check import check

try:
    with open("token.txt", "r") as f:
        TOKEN = f.read()
except FileNotFoundError:
    print("Create token.txt for your Telegram token.")
    exit()

try:
    with open("telegram_id.txt", "r") as f:
        USER_ID = f.read()
except FileNotFoundError:
    print("Create telegram_id.txt for your user id.")
    exit()


open("lastFiveMails.txt", "w")
print("lastFiveMails.txt is created.")


async def check_telegram(context: ContextTypes.DEFAULT_TYPE):
    response, messages = check()

    if not response:
        await context.bot.send_message(chat_id=USER_ID, text=messages)
        return

    if messages == "No new mails.":
        print(messages)
        return

    if len(messages) > 0:
        for message in messages:
            text = f"OBS\n\nKonu: {message['subject']}\n\nMesaj: {message['content']}"
            await context.bot.send_message(chat_id=USER_ID, text=text)


if __name__ == '__main__':
    print("Bot is alive.")

    application = ApplicationBuilder().token(TOKEN).build()

    application.job_queue.run_repeating(
        callback=check_telegram, interval=600, first=5)

    application.run_polling()

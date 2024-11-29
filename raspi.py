import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext

# Define a function to handle text messages
async def echo(update: Update, context: CallbackContext) -> None:
    text_received = update.message.text
    await update.message.reply_text(f'You said: {text_received}')

async def main():
    application = Application.builder().token("7773274180:AAFRsZgmMMSGBqABId18P2sEsC9L6bCJtzQ").build()

    # Create a MessageHandler that listens for text messages
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    # Add the handler to the application
    application.add_handler(text_handler)

    # Start the bot to receive updates
    await application.run_polling()

# Start the bot if running in a standard Python environment
if __name__ == '__main__':
    asyncio.run(main())

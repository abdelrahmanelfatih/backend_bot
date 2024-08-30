from telegram import Update, LabeledPrice
from telegram.ext import Application, CommandHandler, ContextTypes
from typing import final
from flask import Flask, request, jsonify
from flask_cors import CORS

KEY: final = '7301010584:AAFRMvnjkI8bKMnkERH3jTUdIYYYmwGIS9c'

app = Flask(__name__)
CORS(app)  # Enable CORS for the app
invoice_data = {}


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    await update.message.reply_text(f'Hello There. I make invoices.\nYour chat ID is: {user_id}')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Use the menu button to make an invoice.'
    )


async def create_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    data = invoice_data.get(chat_id)

    if not data:
        await update.message.reply_text('No invoice data found. Please send the data from the frontend.')
        return

    title = data['title']
    description = data['description']
    currency = data['currency']
    prices = [LabeledPrice(label=item['name'], amount=int(item['price'] * 100)) for item in data['items']]

    await context.bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        payload="invoice_payload",
        provider_token="284685063:TEST:NGZiNDgxNWFjY2I0",
        currency=currency,
        prices=prices,
        start_parameter="start",
    )


# Error handling
async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update "{update}" caused error "{context.error}"')


# Flask route to receive data from frontend
@app.route('/send_invoice_data', methods=['POST'])
def receive_invoice_data():
    data = request.json
    chat_id = data['chat_id']
    invoice_data[chat_id] = data
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    print('Starting the bot...')
    telegram_app = Application.builder().token(KEY).build()

    # Commands
    telegram_app.add_handler(CommandHandler('start', start_command))
    telegram_app.add_handler(CommandHandler('help', help_command))
    telegram_app.add_handler(CommandHandler('createInvoice', create_invoice))

    # Errors
    telegram_app.add_error_handler(handle_error)

    # Polls the bot
    print('Polling...')
    telegram_app.run_polling(poll_interval=1)

    # Start Flask app
    app.run(host='0.0.0.0', port=5000)

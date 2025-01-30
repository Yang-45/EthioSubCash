import logging
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# Replace with your bot token
BOT_TOKEN = "YOUR_BOT_TOKEN"

# Replace with your Telebirr API endpoint
TELEBIRR_API_URL = "https://api.telebirr.com/check_account"

# Minimum withdrawal limit
MIN_WITHDRAWAL_LIMIT = 100  # Example: 100 birr

# In-memory storage for OTPs and user data
user_data = {}
otp_storage = {}

# Logging setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Colors for the interface
COLOR_PRIMARY = "#3498db"  # Blue
COLOR_SECONDARY = "#2ecc71"  # Green

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id] = {"balance": 0, "phone_number": None, "verified": False}

    # Send welcome message with inline keyboard
    keyboard = [
        [InlineKeyboardButton("Register", callback_data="register")],
        [InlineKeyboardButton("Check Balance", callback_data="balance")],
        [InlineKeyboardButton("Withdraw", callback_data="withdraw")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "እንኳን ደህና መጣቹ! 🎉\n\n"
        "Please register to start earning.",
        reply_markup=reply_markup
    )

# Handle button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == "register":
        await query.message.reply_text("Please send your phone number in the format +251XXXXXXXXX.")
    elif query.data == "balance":
        balance = user_data[user_id]["balance"]
        await query.message.reply_text(f"Your current balance is: {balance} birr.")
    elif query.data == "withdraw":
        await handle_withdrawal(update, context)

# Handle phone number submission
async def handle_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    phone_number = update.message.text

    # Check if the phone number has a Telebirr account
    response = requests.post(TELEBIRR_API_URL, json={"phone_number": phone_number})
    if response.status_code == 200 and response.json().get("has_account"):
        # Generate and send OTP
        otp = str(random.randint(100000, 999999))
        otp_storage[user_id] = {"otp": otp, "phone_number": phone_number}

        # Send OTP to the user (simulated here)
        await update.message.reply_text(f"Your OTP is: {otp}\n\nPlease enter the OTP to verify your account.")
    else:
        await update.message.reply_text("This phone number does not have a Telebirr account. Please try again.")

# Handle OTP submission
async def handle_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    otp = update.message.text

    if user_id in otp_storage and otp_storage[user_id]["otp"] == otp:
        user_data[user_id]["phone_number"] = otp_storage[user_id]["phone_number"]
        user_data[user_id]["verified"] = True
        await update.message.reply_text("Your account has been verified! 🎉")
    else:
        await update.message.reply_text("Invalid OTP. Please try again.")

# Handle withdrawal
async def handle_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    balance = user_data[user_id]["balance"]

    if balance >= MIN_WITHDRAWAL_LIMIT:
        # Trigger Telebirr API to send money
        response = requests.post(TELEBIRR_API_URL, json={
            "phone_number": user_data[user_id]["phone_number"],
            "amount": balance
        })

        if response.status_code == 200:
            user_data[user_id]["balance"] = 0
            await update.callback_query.message.reply_text(f"Withdrawal successful! {balance} birr has been sent to your Telebirr account.")
        else:
            await update.callback_query.message.reply_text("Withdrawal failed. Please try again later.")
    else:
        await update.callback_query.message.reply_text(f"Your balance is below the minimum withdrawal limit of {MIN_WITHDRAWAL_LIMIT} birr.")

# Main function
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone_number))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_otp))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
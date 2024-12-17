import asyncio
import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Multiple Admin User IDs
ADMIN_USER_IDS = [5195565978, 6684672526, -1002220761952]
USERS_FILE = 'users.txt'
LOG_FILE = 'log.txt'
attack_in_progress = False
users = set()
user_approval_expiry = {}
TELEGRAM_BOT_TOKEN = '7739259868:AAE5nYLnAiHUROnmFO1fIS7b6FOl61CTeYQ'


def load_users():
    try:
        with open(USERS_FILE) as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()


def save_users(users):
    with open(USERS_FILE, 'w') as f:
        f.writelines(f"{user}\n" for user in users)


def log_command(user_id, target, port, duration):
    with open(LOG_FILE, 'a') as f:
        f.write(f"UserID: {user_id} | Target: {target} | Port: {port} | Duration: {duration} | Timestamp: {datetime.datetime.now()}\n")


def clear_logs():
    try:
        with open(LOG_FILE, 'r+') as f:
            if f.read().strip():
                f.truncate(0)
                return "*✅ Logs cleared successfully.*"
            else:
                return "*⚠️ No logs found.*"
    except FileNotFoundError:
        return "*⚠️ No logs file found.*"


def set_approval_expiry_date(user_id, duration, time_unit):
    current_time = datetime.datetime.now()
    if time_unit in ["hour", "hours"]:
        expiry_date = current_time + datetime.timedelta(hours=duration)
    elif time_unit in ["day", "days"]:
        expiry_date = current_time + datetime.timedelta(days=duration)
    elif time_unit in ["week", "weeks"]:
        expiry_date = current_time + datetime.timedelta(weeks=duration)
    elif time_unit in ["month", "months"]:
        expiry_date = current_time + datetime.timedelta(days=30 * duration)
    else:
        return False
    user_approval_expiry[user_id] = expiry_date
    return True


def get_remaining_approval_time(user_id):
    expiry_date = user_approval_expiry.get(user_id)
    if expiry_date:
        remaining_time = expiry_date - datetime.datetime.now()
        return str(remaining_time) if remaining_time.total_seconds() > 0 else "Expired"
    return "N/A"


async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*👹 MÓÑSTÈR FREE DDOS GROUP 👹*\n\n"
        "*Use /attack <ip> <port> <duration>*\n"
        "*DM TO BUY :- @Mk_ddos*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')


async def add_group(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id not in ADMIN_USER_IDS:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Unauthorized access.*", parse_mode='Markdown')
        return

    args = context.args
    if len(args) < 2:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*⚠️ Usage: /addgroup <group_id> <duration><time_unit>*\nExample: /addgroup -100123456789 30days",
            parse_mode='Markdown'
        )
        return

    group_id = args[0]
    duration_str = args[1]

    try:
        duration = int(duration_str[:-4])
        time_unit = duration_str[-4:].lower()
        if set_approval_expiry_date(group_id, duration, time_unit):
            users.add(group_id)
            save_users(users)
            expiry_date = user_approval_expiry[group_id]
            response = f"*✔️ Group {group_id} added successfully.*\nAccess expires on: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}."
        else:
            response = "*⚠️ Invalid time unit. Use 'hours', 'days', 'weeks', or 'months'.*"
    except ValueError:
        response = "*⚠️ Invalid duration format.*"

    await context.bot.send_message(chat_id=chat_id, text=response, parse_mode='Markdown')


async def view_logs(update: Update, context: CallbackContext):
    if update.effective_chat.id not in ADMIN_USER_IDS:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*⚠️ Unauthorized access.*", parse_mode='Markdown')
        return

    try:
        with open(LOG_FILE, 'r') as f:
            logs = f.read().strip() or "*No logs available.*"
    except FileNotFoundError:
        logs = "*No logs available.*"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"*Logs:*\n\n{logs}", parse_mode='Markdown')


async def clear_logs_command(update: Update, context: CallbackContext):
    if update.effective_chat.id not in ADMIN_USER_IDS:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*⚠️ Unauthorized access.*", parse_mode='Markdown')
        return

    response = clear_logs()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode='Markdown')


async def attack(update: Update, context: CallbackContext):
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id not in users or get_remaining_approval_time(user_id) == "Expired":
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ **APNA PAPA SA APPROVEL LA LA**.*", parse_mode='Markdown')
        return

    if attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️** An attack is already in progress. Please wait**.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /attack <ip> <port> <duration>*", parse_mode='Markdown')
        return

    ip, port, duration = args
    try:
        duration = int(duration)
        if duration > 300:
            response = "*⚠️ Error: Time interval must be less than or equal to 300 seconds.*"
            await context.bot.send_message(chat_id=chat_id, text=response, parse_mode='Markdown')
            return
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Duration must be a valid number.*", parse_mode='Markdown')
        return

    log_command(user_id, ip, port, duration)

    await context.bot.send_message(chat_id=chat_id, text=(
        f"*⚔️ Attack Launched! 👹*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Join: https://t.me/monster_ddos 💥*"
    ), parse_mode='Markdown')

    attack_in_progress = True
    await asyncio.sleep(duration)  # Simulated attack duration
    attack_in_progress = False

    await context.bot.send_message(chat_id=chat_id, text="*✅ Attack finished successfully.*", parse_mode='Markdown')


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addgroup", add_group))
    application.add_handler(CommandHandler("viewlogs", view_logs))
    application.add_handler(CommandHandler("clearlogs", clear_logs_command))
    application.add_handler(CommandHandler("attack", attack))

    application.run_polling()


if __name__ == '__main__':
    users = load_users()
    main()
        

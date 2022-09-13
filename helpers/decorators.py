from functools  import wraps
from datetime   import datetime

from .stdlib import LOG1, LOG2, Colors, utc_to_local, date_to_str
from .sql_funcs  import get_or_create_chat
from .constants  import Constants

from db import db_session


def check_bot_env_in_chats(check_admin_status=True, check_update_delay=True):
    def checker_dec(handler):
        @wraps(handler)
        def checker(update, context):
            if update.message.chat.type == "private":
                LOG1("This message/command is not supported in private chat", color=Colors.RED)
                LOG2(update)

                update.message.reply_text("Данное сообщение или команда не поддерживается в личном диалоге с ботом.", quote=True)
                return

            # If update.message.chat.id not in DB, this call will safety add it to DB before handler work
            get_or_create_chat(db_session.create_session(), update.message.chat.id, update.message.chat.title)

            upd_time = utc_to_local(update.message.date)
            now      = datetime.now()
            delay    = abs((now - upd_time).total_seconds())
            if check_update_delay and delay > Constants.UPD_TIME_DELAY_SEC(update):
                LOG1(
                    f"Detected OLD update. This update will be skipped\n"
                    f"Update  time: '{date_to_str(upd_time)}'\n"
                    f"Current time: '{date_to_str(now)}'\n"
                    f"UPD_DELAY: {Constants.UPD_TIME_DELAY_SEC(update)}; current delay: {delay}",
                    color=Colors.RED
                )
                return

            admins     = context.bot.getChatAdministrators(update.message.chat.id)
            admins_ids = map(lambda admin: admin.user.id, admins)
            if check_admin_status and Constants.BOT_ID__ not in admins_ids:
                LOG1(f"Bot is not administrator in chat '{update.message.chat.title}'({update.message.chat.id})\n"
                     f"Make bot an administrator", color=Colors.RED)
                context.bot.send_message(update.message.chat.id, "Бот не является администратором этой группы. Для работы бота сначала сделайте его администратором.")
                return

            handler(update, context)

        return checker
    return checker_dec


def log_handler(handler):
    @wraps(handler)
    def logger(update, context):
        intro     = f"==================== Handler '{handler.__name__}' start working ===================="
        chat_info = f"Chat '{update.message.chat.title}'({update.message.chat.id})"
        end_text  = f"==================== Handler '{handler.__name__}' end   working ===================="

        spaces    = (len(intro) - len(chat_info)) // 2
        spaces    = spaces if spaces > 0 else 0

        LOG1(intro, color=Colors.ORANGE, skipu=1)
        LOG1(f"{' ' * spaces}{chat_info}{' ' * spaces}", color=Colors.GRAY)

        handler(update, context)

        LOG1(f"{' ' * spaces}{chat_info}{' ' * spaces}", color=Colors.GRAY)
        LOG1(end_text, color=Colors.ORANGE, skipd=1)

    return logger


def private_chat_required(handler):
    @wraps(handler)
    def checker(update, context):
        if update.message.chat.type != "private":
            LOG1(f"This message/command is not supported in this chat (type - '{update.message.chat.type}')", color=Colors.RED)
            LOG2(update)

            if not Constants.SILENCE_IN_CHAT(update):
                update.message.reply_text("Данное сообщение или команда поддерживается только личном диалоге с ботом.")

            return

        handler(update, context)

    return checker

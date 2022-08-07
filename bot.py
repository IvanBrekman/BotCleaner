import random as rd

from environs import Env
from datetime import datetime
from typing   import Dict
from config   import LOG1, LOG2, Colors

from telegram.ext import Updater, MessageHandler, CommandHandler, Filters


class ChatMember:
    def __init__(self, user_id: int, chat: int, join_time: datetime, check_answer: int, del_messages: list = None):
        self.id             = user_id
        self.chat           = chat
        self.join_time      = join_time
        self.answer         = check_answer
        self.tries          = TRIES
        self.msg_for_delete = del_messages or []

    def __str__(self):
        return f"User({self.id}) in chat '{self.chat}', joined {self.join_time}. "  \
               f"Check answer: {self.answer} (tries left: {self.tries}). "          \
               f"Delete messages({len(self.msg_for_delete)}): {[message.text[:10] for message in self.msg_for_delete]}"

    def __repr__(self):
        return self.__str__()

    def add_message(self, message):
        self.msg_for_delete.append(message)


env = Env()
env.read_env()

# ======================================== CONSTANTS ========================================
TOKEN           = env.str("BOT_TOKEN")
CHECK_TIME      = 60
TRIES           = 3
SPAM_KEYWORDS   = ["Купить", "Продать"]
# ===========================================================================================

# ======================================= INIT VALUES =======================================
updater    = Updater(TOKEN, use_context=True)
dispather  = updater.dispatcher
job_queue  = updater.job_queue

check_users: Dict[int, ChatMember] = {}
# ===========================================================================================


# ======================================== Handlers =========================================
def new_member(update, _):
    LOG1("New member detected", color=Colors.BLUE)
    LOG2("Update message: ", update)

    first, second = rd.randint(1, 9), rd.randint(1, 9)
    check_users[update.message.from_user.id] = ChatMember(update.message.from_user.id, update.message.chat.id,
                                                          datetime.now(), first + second, [update.message])
    LOG1("New user info:", check_users, sep="\n", color=Colors.BLUE)

    message = update.message.reply_text(
        f"Приветствую в чате! Чтобы остаться в нем, подтвердите, что вы не бот.\n\n"
        f"Для этого в течении {CHECK_TIME} сек. отправьте в чат решение задачи ниже:\n\n"
        f"{first} + {second} = ?"
    )
    check_users[update.message.from_user.id].add_message(message)

    job_queue.run_once(force_delete, CHECK_TIME)


def check(update, context):
    text      = update.message.text
    from_user = update.message.from_user

    if from_user.id not in check_users:
        check_spam_messages(update, context)

    LOG1("Got message from checked user: ", text, color=Colors.GREEN)
    user = check_users[from_user.id]
    user.add_message(update.message)

    try:
        res = int(text)
        if res != user.answer:
            raise ValueError
    except ValueError:
        message = update.message.reply_text("Неверно!")

        user.add_message(message)

        user.tries -= 1
        if user.tries < 1:
            delete_user(update.message.chat.id, from_user.id, context)

        return

    cleanup_check_messages(from_user.id)


def check_spam_messages(update, context):
    pass
# ===========================================================================================


# ========================================  Helpers  ========================================
def delete_user(chat_id, user_id, context):
    LOG1(f"Delete user ({user_id})", color=Colors.RED)
    context.bot.ban_chat_member(chat_id, user_id)

    cleanup_check_messages(user_id)


def cleanup_check_messages(user_id):
    LOG1(f"Cleanup check messages for user ({user_id})\n", check_users, color=Colors.ORANGE)
    for message in check_users[user_id].msg_for_delete:
        message.delete()

    check_users.pop(user_id)


def force_delete(context):
    for user_id, args in check_users.items():
        timedelta = datetime.now() - args.join_time
        LOG1("Time's up: ", timedelta.total_seconds(), color=Colors.RED)

        if timedelta.total_seconds() >= CHECK_TIME:
            delete_user(args.chat, user_id, context)
            break


def check_bot(update, _):
    LOG1("Check request: successful", color=Colors.GREEN)
    update.message.delete()
# ===========================================================================================


def main():
    dispather.add_handler(CommandHandler("check",                                check_bot))
    dispather.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member, pass_job_queue=True))
    dispather.add_handler(MessageHandler(Filters.text,                           check,      pass_job_queue=True))

    LOG1("Bot start working", color=Colors.GREEN)

    updater.start_polling()
    updater.idle()

    LOG1("Bot end working", color=Colors.GREEN)


if __name__ == '__main__':
    main()

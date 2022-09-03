import random as rd

from datetime           import datetime
from typing             import Dict

from telegram.ext       import Updater, MessageHandler, CommandHandler, Filters

from helpers.classes    import ChatMember, SpamWords
from helpers.constants  import Constants
from helpers.sql_funcs  import get_or_create_chat, get_or_create_user, safety_chat_creating, safety_chat_deleting,\
                               get_association_object
from helpers.stdlib     import LOG1, LOG2, LOGN, NEW_LINE, Colors

from db                 import db_session

from db.models.chat     import Chat
from db.models.user     import User


# ======================================= INIT VALUES =======================================
updater         = Updater(Constants.TOKEN, use_context=True)
dispather       = updater.dispatcher
job_queue       = updater.job_queue

check_users: Dict[int, ChatMember] = {}
# ===========================================================================================


# ======================================== Handlers =========================================
def new_member(update, _):
    LOG1(f"{len(update.message.new_chat_members)} new members detected", color=Colors.BLUE)
    LOG2(f"{NEW_LINE.join(map(str, update.message.new_chat_members))}")
    LOG2("Update message: ", update)

    for user in update.message.new_chat_members:
        if user.id == Constants.BOT_ID:
            LOG1("\nDetected adding bot to chat", color=Colors.BLUE)
            return add_tracked_chat(update)

        first, second = rd.randint(1, 9), rd.randint(1, 9)
        name = user.username or user.first_name
        check_users[user.id] = ChatMember(
            user.id,        name,           update.message.chat.id,
            datetime.now(), first + second, [update.message]
        )
        LOG1("New user info:", check_users, sep="\n", color=Colors.BLUE)

        message = update.message.reply_text(
            f"@{user.username}, приветствую в чате! Чтобы остаться в нем, подтвердите, что вы не бот.\n\n"
            f"Для этого в течении {Constants.CHECK_TIME} сек. отправьте в чат решение задачи ниже:\n\n"
            f"{first} + {second} = ?"
        )
        check_users[user.id].add_message(message)

        job_queue.run_once(force_delete, Constants.CHECK_TIME)


def left_member(update, _):
    LOG2("Member left event:", update, color=Colors.GRAY)

    member = update.message.left_chat_member
    if member.id != Constants.BOT_ID:
        return

    session = db_session.create_session()

    LOG1(f"Bot deleted from chat '{update.message.chat.title}'({update.message.chat.id})", color=Colors.RED)
    del_result = safety_chat_deleting(session, update.message.chat.id)
    LOG1("Successfully deleted" if del_result else "End of left_member function")


def check(update, context):
    text      = update.message.text
    from_user = update.message.from_user

    if from_user.id not in check_users:
        check_spam_messages(update, context)
        return

    LOG1(f"Got message from checked user (@{from_user.username or from_user.first_name} - {from_user.id}):", text,
         color=Colors.GREEN)
    user = check_users[from_user.id]
    user.add_message(update.message)

    try:
        res = int(text)
        if res != user.answer:
            raise ValueError

        session = db_session.create_session()

        chat = session.query(Chat).get(update.message.chat.id)
        user = get_or_create_user(session, from_user.id, from_user.username or from_user.first_name)

        chat.users.append(user)

        session.commit()
    except ValueError:
        message = update.message.reply_text("Неверно!")

        user.add_message(message)

        user.tries -= 1
        if user.tries < 1:
            delete_user(update.message.chat.id, from_user.id, context)

        return

    cleanup_check_messages(from_user.id)


def check_spam_messages(update, context):
    LOG2("Checking message for spam", color=Colors.GRAY)
    LOGN("Message:", update.message.text, color=Colors.GRAY, level=3)

    spam_words = SpamWords(Constants.SPAM_KEYWORDS).check_spam_message(update.message.text)
    if not spam_words:
        return

    LOG1(f"Spam detected! Spam words: {spam_words}", color=Colors.RED)

    update.message.delete()

    from_user = update.message.from_user

    session = db_session.create_session()

    ass_obj = get_association_object(session, update.message.chat.id, from_user.id)
    if ass_obj is None:
        chat = get_or_create_chat(session, update.message.chat.id, update.message.chat.title)

        user = get_or_create_user(session, from_user.id, from_user.username or from_user.first_name)
        chat.users.append(user)

        session.commit()
        ass_obj = get_association_object(session, update.message.chat.id, from_user.id)
        assert ass_obj is not None

    ass_obj.fines += 1

    if ass_obj.fines >= Constants.FINES_LIMIT:
        LOG1(f"User @{ass_obj.user.name}({ass_obj.user.id}) fines exceeded LIMIT ({Constants.FINES_LIMIT})",
             Colors.RED)
        delete_user(update.message.chat.id, update.message.from_user.id, context)

    session.commit()

    if Constants.SEND_MSG_ABOUT_SPAM:
        context.bot.send_message(update.message.chat.id, text=f"Пользователь @{ass_obj.user.name}, "
                                                              f"ваше сообщение было помечено как спам и удалено.")
# ===========================================================================================


# ========================================  Helpers  ========================================
def delete_user(chat_id, user_id, context):
    LOG1(f"Delete user ({user_id})", color=Colors.RED)
    context.bot.ban_chat_member(chat_id, user_id)

    cleanup_check_messages(user_id)


def cleanup_check_messages(user_id):
    LOG1(f"Cleanup check messages for user ({user_id})\n", check_users, color=Colors.ORANGE)

    if user_id not in check_users:
        return

    for message in check_users[user_id].msg_for_delete:
        message.delete()

    check_users.pop(user_id)


def force_delete(context):
    for user_id, args in check_users.items():
        timedelta = datetime.now() - args.join_time
        LOG1("Time's up: ", timedelta.total_seconds(), color=Colors.RED)

        if timedelta.total_seconds() >= Constants.CHECK_TIME:
            delete_user(args.chat, user_id, context)
            break


def check_bot(update, _):
    LOG1("Check request: successful", color=Colors.GREEN)
    update.message.delete()


def add_tracked_chat(update):
    chat_id = update.message.chat.id

    LOG1(f"Add new chat ({chat_id}) for bot", color=Colors.ORANGE)
    session = db_session.create_session()

    new_chat = safety_chat_creating(session, chat_id, update.message.chat.title)

    session.add(new_chat)
    session.commit()

    LOG1(f"Added chat ({chat_id}) in db", color=Colors.ORANGE)
# ===========================================================================================


def main():
    db_session.global_init("db/base.db")

    dispather.add_handler(CommandHandler("check",                                check_bot))
    dispather.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member,    pass_job_queue=True))
    dispather.add_handler(MessageHandler(Filters.status_update.left_chat_member, left_member,   pass_job_queue=True))
    dispather.add_handler(MessageHandler(Filters.text,                           check,         pass_job_queue=True))

    LOG1("Bot start working", color=Colors.GREEN)

    updater.start_polling()
    updater.idle()

    LOG1("Bot end working", color=Colors.GREEN)


if __name__ == '__main__':
    main()

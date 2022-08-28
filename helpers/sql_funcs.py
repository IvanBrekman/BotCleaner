from db import db_session

from db.models.chat import Chat
from db.models.user import User

from .stdlib import LOG2, Colors


def safety_chat_creating(session, chat_id, chat_title):
    chat = session.query(Chat).filter_by(chat_id=chat_id).first()
    if chat is not None:
        LOG2("Something wrong. Chat is already in DB! Clear chat users", color=Colors.RED)
        chat.users = []
        session.commit()

        return chat

    new_chat = Chat(chat_id=chat_id, name=chat_title)

    return new_chat


def safety_chat_deleting(session, chat_id):
    chat = session.query(Chat).filter_by(chat_id=chat_id).first()
    if chat is None:
        LOG2("Something wrong. Chat is not in DB!", color=Colors.RED)
        return False

    session.delete(chat)
    session.commit()

    return True


def get_or_create_user(session, user_id, username):
    user = session.query(User).filter_by(user_id=user_id).first()
    if user is not None:
        return user

    new_user = User(user_id=user_id, name=username)

    session.add(new_user)
    session.commit()

    return new_user

from sqlalchemy.orm import Session

from db.models.chat     import Chat, ChatUserAssociation
from db.models.user     import User
from db.models.setting  import Setting

from .stdlib import LOG2, Colors


def get_or_create_chat(session: Session, chat_id: int, title: str):
    chat = session.query(Chat).get(chat_id)
    if chat is not None:
        return chat

    new_chat = Chat(id=chat_id, name=title)

    for setting in session.query(Setting).all():
        new_chat.settings.append(setting)

    session.add(new_chat)
    session.commit()

    return new_chat


def safety_chat_creating(session: Session, chat_id: int, chat_title: str):
    chat = session.query(Chat).get(chat_id)
    if chat is not None:
        LOG2("Something wrong. Chat is already in DB! Clear chat users", color=Colors.RED)
        chat.users = []
        session.commit()

        return chat

    new_chat = Chat(id=chat_id, name=chat_title)

    return new_chat


def safety_chat_deleting(session: Session, chat_id: int):
    chat = session.query(Chat).get(chat_id)
    if chat is None:
        LOG2("Something wrong. Chat is not in DB!", color=Colors.RED)
        return False

    session.delete(chat)
    session.commit()

    return True


def get_or_create_user(session: Session, user_id: int, username: str):
    user = session.query(User).get(user_id)
    if user is not None:
        return user

    new_user = User(id=user_id, name=username)

    session.add(new_user)
    session.commit()

    return new_user


def get_association_object(session: Session, chat_id: int, user_id: int):
    return session.query(ChatUserAssociation).filter_by(chat_id=chat_id, user_id=user_id).first()

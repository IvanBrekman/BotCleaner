import sqlalchemy

from sqlalchemy                         import orm
from sqlalchemy.ext.associationproxy    import association_proxy

from ..db_session import SqlAlchemyBase


class ChatUserAssociation(SqlAlchemyBase):
    __tablename__ = "chats_to_users"

    chat_id = sqlalchemy.Column("chat_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("chats.id"), primary_key=True)
    user_id = sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), primary_key=True)

    fines   = sqlalchemy.Column("fines",   sqlalchemy.Integer, default=0)

    chat    = orm.relationship("Chat", back_populates="chat_user_associations")
    user    = orm.relationship("User", back_populates="chat_user_associations")

    def __init__(self, user, chat=None, fines=0):
        self.user  = user
        self.chat  = chat
        self.fines = fines


class Chat(SqlAlchemyBase):
    __tablename__ = "chats"

    id      = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name    = sqlalchemy.Column(sqlalchemy.String,  nullable=False)

    chat_user_associations    = orm.relationship("ChatUserAssociation",    back_populates="chat", cascade="all, delete-orphan")
    chat_setting_associations = orm.relationship("ChatSettingAssociation", back_populates="chat", cascade="all, delete-orphan")

    users    = association_proxy("chat_user_associations",    "user")
    settings = association_proxy("chat_setting_associations", "setting")

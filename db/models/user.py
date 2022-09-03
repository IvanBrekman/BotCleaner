import sqlalchemy

from sqlalchemy                         import orm
from sqlalchemy.ext.associationproxy    import association_proxy

from ..db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = "users"

    id      = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name    = sqlalchemy.Column(sqlalchemy.String,  nullable=False)

    chat_user_associations = orm.relationship("ChatUserAssociation", back_populates="user", cascade="all, delete-orphan")

    chats   = association_proxy("chat_user_associations", "chat")

import sqlalchemy

from sqlalchemy   import orm, Table
from ..db_session import SqlAlchemyBase

association_table = Table(
    "chats_to_users",
    SqlAlchemyBase.metadata,

    sqlalchemy.Column("chat_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("chats.id"), primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), primary_key=True)
)


class Chat(SqlAlchemyBase):

    __tablename__ = "chats"

    id      = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False,   unique=True)
    name    = sqlalchemy.Column(sqlalchemy.String,  nullable=False)

    users   = orm.relationship("User", secondary=association_table, back_populates="chats", lazy="dynamic")

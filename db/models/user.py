import sqlalchemy

from sqlalchemy   import orm
from ..db_session import SqlAlchemyBase

from .chat import association_table


class User(SqlAlchemyBase):

    __tablename__ = "users"

    id      = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False,   unique=True)
    name    = sqlalchemy.Column(sqlalchemy.String,  nullable=False)

    chats   = orm.relationship("Chat", secondary=association_table, back_populates="users", lazy="dynamic")


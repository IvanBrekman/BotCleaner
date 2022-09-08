import sqlalchemy

from sqlalchemy                         import orm
from sqlalchemy.ext.associationproxy    import association_proxy

from ..db_session import SqlAlchemyBase


class ChatSettingAssociation(SqlAlchemyBase):
    __tablename__ = "chats_to_settings"

    chat_id    = sqlalchemy.Column("chat_id",    sqlalchemy.Integer, sqlalchemy.ForeignKey("chats.id"),    primary_key=True)
    setting_id = sqlalchemy.Column("setting_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("settings.id"), primary_key=True)

    value      = sqlalchemy.Column("value",      sqlalchemy.String,  nullable=False)

    chat       = orm.relationship("Chat",    back_populates="chat_setting_associations")
    setting    = orm.relationship("Setting", back_populates="chat_setting_associations")

    def __init__(self, setting, chat=None):
        self.setting = setting
        self.chat    = chat
        self.value   = setting.default


class Setting(SqlAlchemyBase):
    __tablename__ = "settings"

    id      = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name    = sqlalchemy.Column(sqlalchemy.String,  nullable=False, unique=True)
    type    = sqlalchemy.Column(sqlalchemy.String,  nullable=False)
    default = sqlalchemy.Column(sqlalchemy.String,  nullable=False)

    chat_setting_associations = orm.relationship("ChatSettingAssociation", back_populates="setting", cascade="all, delete-orphan")

    chats   = association_proxy("chat_setting_associations", "chat")

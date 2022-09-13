import os
import csv

from typing   import Callable
from environs import Env
from telegram import Update

from .stdlib  import LOG1, LOG2, Colors

from db                 import db_session
from db.models.chat     import Chat
from db.models.setting  import Setting, ChatSettingAssociation

env = Env()
env.read_env()


def load_settings_to_db():
    with open(Constants.SETTINGS_LOAD_FILE__, mode="r", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file, delimiter=";", quotechar="'")

        session = db_session.create_session()

        LOG2(f"Setting: {'name':30} | {'type':5} | default", color=Colors.GRAY)
        LOG2("=" * 60, color=Colors.GRAY)
        for i, setting in enumerate(reader, 1):
            LOG2(f"     {i:02}. {setting[0]:30} | {setting[1]:5} | {setting[2]} ", color=Colors.GRAY)
            session.add(Setting(*setting))
        LOG2("=" * 60, color=Colors.GRAY)

        session.commit()
        LOG1("Settings are successfully load to DB", color=Colors.GREEN, skipd=1)


def get_constant(chat_info, setting_name):
    if isinstance(chat_info, int):
        chat_id = chat_info
    elif isinstance(chat_info, Update):
        chat_id = chat_info.message.chat.id
    else:
        raise TypeError(f"Cannot get chat id from instance of type '{type(chat_info)}'")

    session = db_session.create_session()

    setting = session.query(Setting).filter_by(name=setting_name).first()
    if setting is None:
        raise ValueError(f"No setting with name '{setting_name}'")

    chat_setting = session.query(ChatSettingAssociation).filter_by(chat_id=chat_id, setting_id=setting.id).first()
    if chat_setting is None:
        raise ValueError(f"No setting with name '{setting_name}' in chat '{chat_id}'")

    namespace = {"env": env}
    os.environ[setting_name] = chat_setting.value
    exec(f"value = env.{setting.type}('{setting_name}')", namespace)

    return namespace.get("value")


def fixed_setting(name, setting_type):
    namespace = {'env': env}

    exec(f"value = env.{setting_type.__name__}('{name}')", namespace)

    return namespace.get("value")


class Constants:
    SETTINGS_LOAD_FILE__: str = "db/db_settings_info.csv"

    BOT_TOKEN__: str = fixed_setting("BOT_TOKEN", str)
    BOT_ID__:    int = fixed_setting("BOT_ID",    int)
    API_ID__:    int = fixed_setting("API_ID",    int)
    API_HASH__:  str = fixed_setting("API_HASH",  str)

    CHECK_TIME:             Callable[[(int, Update)], int]  = None
    TRIES_FOR_ANSWER:       Callable[[(int, Update)], int]  = None
    FINES_LIMIT:            Callable[[(int, Update)], int]  = None
    SPAM_KEYWORDS:          Callable[[(int, Update)], list] = None
    SILENCE_IN_CHAT:        Callable[[(int, Update)], int]  = None
    UPD_TIME_DELAY_SEC:     Callable[[(int, Update)], int]  = None

    @staticmethod
    def init():
        session  = db_session.create_session()

        settings = session.query(Setting).all()
        chats    = session.query(Chat).all()

        if len(settings) == 0:
            LOG1(f"Settings are not in DB! Loading Settings data from '{Constants.SETTINGS_LOAD_FILE__}'", color=Colors.RED)
            load_settings_to_db()

        for setting in settings:
            exec(f"Constants.{setting.name} = lambda chat_id: get_constant(chat_id, '{setting.name}')")

        for chat in chats:
            if len(chat.settings) < len(settings):
                for setting in settings:
                    if setting not in chat.settings:
                        chat.settings.append(setting)

        session.commit()

import sys
sys.path.insert(0, "C:\\Users\\nikit\\PycharmProjects\\pythonProject")

from db import db_session
from db.models.setting import Setting, ChatSettingAssociation
from db.models.chat import Chat

from environs import Env

env = Env()
env.read_env()


def get_constant(chat_id, setting_name):
    session = db_session.create_session()

    setting_id = Constants.setting_name_to_id.get(setting_name)
    if setting_id is None:
        setting    = session.query(Setting).filter_by(name=setting_name).first()
        if setting is not None:
            Constants.setting_name_to_id[setting_name] = setting.id
        else:
            raise ValueError(f"No setting with name '{setting_name}'")
        setting_id = setting.id

    setting = session.query(ChatSettingAssociation).filter_by(chat_id=chat_id, setting_id=setting_id).first()
    if setting is None:
        raise ValueError(f"No setting with name '{setting_name}' in chat '{chat_id}'")

    return setting.value


def fixed_setting(name, setting_type):
    namespace = {'env': env}

    exec(f"value = env.{setting_type.__name__}('{name}')", namespace)

    return lambda _: namespace.get("value")


class Constants:
    setting_name_to_id = {}

    BOT_TOKEN   = fixed_setting("BOT_TOKEN", str)
    BOT_ID      = fixed_setting("BOT_ID",    int)
    API_ID      = fixed_setting("API_ID",    int)
    API_HASH    = fixed_setting("API_HASH",  str)

    CHECK_TIME          = None
    TRIES_FOR_ANSWER    = None
    FINES_LIMIT         = None
    SPAM_WORDS          = None
    SEND_MSG_ABOUT_SPAM = None
    UPD_TIME_DELAY_SEC  = None

    @staticmethod
    def init():
        session  = db_session.create_session()
        settings = session.query(Setting).all()

        for setting in settings:
            Constants.setting_name_to_id[setting.name] = setting.id
            exec(f"Constants.{setting.name} = lambda chat_id: get_constant(chat_id, '{setting.name}')")


if __name__ == '__main__':
    db_session.global_init("../db/base.db")

    Constants.init()

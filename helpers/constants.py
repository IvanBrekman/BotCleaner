from environs import Env

env = Env()
env.read_env()


class Constants:
    TOKEN               = env.str("BOT_TOKEN")
    CHECK_TIME          = env.int("CHECK_TIME")
    TRIES               = env.int("TRIES")
    BOT_ID              = env.int("BOT_ID")
    FINES_LIMIT         = env.int("FINES_LIMIT")
    SPAM_KEYWORDS       = env.list("SPAM_WORDS")
    SEND_MSG_ABOUT_SPAM = env.bool("SEND_MSG_ABOUT_SPAM")

    API_ID              = env.int("API_ID")
    API_HASH            = env.str("API_HASH")

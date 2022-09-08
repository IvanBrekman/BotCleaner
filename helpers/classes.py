from pymorphy2 import MorphAnalyzer
from datetime import datetime
from typing import List, Tuple

from .constants import Constants


class ChatMember:
    def __init__(self, user_id: int, user_nick: str, chat: int, join_time: datetime, check_answer: int,
                 del_messages: list = None):
        self.id             = user_id
        self.nickname       = user_nick
        self.chat           = chat
        self.join_time      = join_time
        self.answer         = check_answer
        self.tries          = Constants.TRIES_FOR_ANSWER(chat)
        self.msg_for_delete = del_messages or []

    def __str__(self):
        return f"User @{self.nickname}({self.id}) in chat '{self.chat}', joined {self.join_time}. "         \
               f"Check answer: {self.answer} (tries left: {self.tries}). "                                  \
               f"Delete messages({len(self.msg_for_delete)}): "                                             \
               f"{[message.text[:10] if message.text else 'None' for message in self.msg_for_delete]} "

    def __repr__(self):
        return self.__str__()

    def add_message(self, message):
        self.msg_for_delete.append(message)


class SpamWords:
    def __init__(self, words: List[str] = None):
        self._morph = MorphAnalyzer()
        self.words  = [self.to_normal_form(word) for word in words] or []

    def to_normal_form(self, word: str) -> str:
        return self._morph.parse(word)[0].normal_form

    def add_spam_word(self, word: str):
        self.words.append(self.to_normal_form(word))

    def is_spam_word(self, word: str) -> bool:
        return self.to_normal_form(word) in self.words

    def check_spam_list(self, words: List[str]) -> List[Tuple[int, str]]:
        return [(i, word) for i, word in enumerate(words) if self.is_spam_word(word)]

    def check_spam_message(self, message: str) -> List[Tuple[int, str]]:
        clear_message = ""
        for sym in message:
            clear_message += sym if (sym.isalnum() or sym == " ") else " "

        return self.check_spam_list(clear_message.split())

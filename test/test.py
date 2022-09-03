import sys
sys.path.insert(0, "C:\\Users\\nikit\\PycharmProjects\\pythonProject")

from db import db_session

from db.models.chat import Chat, ChatUserAssociation
from db.models.user import User

db_session.global_init("../db/base.db")

session = db_session.create_session()

# chat = Chat(id=100, name="chat")
#
# user1 = User(id=1, name="name1")
# user2 = User(id=2, name="name2")
# user3 = User(id=3, name="name3")
#
# chat.users.extend([user1, user2, user3])
#
# session.add(chat)
# session.commit()

chat = session.query(Chat).get(1)
user = session.query(User).get(2)

ass_obj = session.query(ChatUserAssociation).filter_by(user_id=user.id, chat_id=chat.id).first()
ass_obj.fines += 1

session.commit()
print(ass_obj.fines)

user = session.query(Chat).get(1)

session.delete(user)
session.commit()

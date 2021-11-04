import datetime

from telegram import *
from telegram.ext import *

# {
# "message":{
#     "group_chat_created":false,
#     "delete_chat_photo":false,
#     "channel_chat_created":false,
#     "new_chat_members":[
        
#     ],
#     "photo":[
        
#     ],
#     "supergroup_chat_created":false,
#     "chat":{
#         "first_name":"Paul",
#         "id":350486052,
#         "type":"private",
#         "username":"pth76"
#     },
#     "text":"/grant asd",
#     "entities":[
#         {
#         "offset":0,
#         "type":"bot_command",
#         "length":6
#         }
#     ],
#     "caption_entities":[
        
#     ],
#     "date":1636053115,
#     "new_chat_photo":[
        
#     ],
#     "message_id":1020,
#     "from":{
#         "language_code":"en",
#         "first_name":"Paul",
#         "is_bot":false,
#         "id":350486052,
#         "username":"pth76"
#     }
# },
# "update_id":972077022
# }

def user():
    return User(
        id=999999999,
        first_name="test-user",
        is_bot=False
    )

def chat():
    return Chat(
        id=123456789,
        type="private"
    )

def message(text="placeholder"):
    return Message(
        message_id=1234,
        date=datetime.datetime.now(),
        chat=chat(),
        text=text,
        from_user=user()
    )

if __name__ == '__main__':
    print(message())
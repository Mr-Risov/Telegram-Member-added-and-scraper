import sys
import csv
import time
import random
from telethon.sync import TelegramClient
from telethon import functions, types
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from telethon.errors.rpcerrorlist import ChatAdminRequiredError, UserChannelsTooMuchError, ChatIdInvalidError, InputUserDeactivatedError, UserNotMutualContactError, PeerIdInvalidError, UsersTooMuchError, UserIdInvalidError, UserAlreadyParticipantError, FloodWaitError, PeerFloodError, UserPrivacyRestrictedError, PhoneNumberBannedError, UserDeactivatedBanError

# Prompt user for phone number, API ID, and API hash
phone = input("Enter your phone number: ")
api_id = input("Enter your API ID: ")
api_hash = input("Enter your API hash: ")

try:
    client = TelegramClient(phone, api_id, api_hash)

    client.connect()

    if not client.is_user_authorized():
        client.send_code_request(phone)
        client.sign_in(phone, input('Enter the code: '))

    chats = []
    last_date = None
    chunk_size = 200
    groups = []

    result = client(GetDialogsRequest(
             offset_date=last_date,
             offset_id=0,
             offset_peer=InputPeerEmpty(),
             limit=chunk_size,
             hash = 0
         ))

    chats.extend(result.chats)

    for chat in chats:
      try:
        if chat.megagroup == True or chat.broadcast == True:
            groups.append(chat)
      except:
        continue

    print('Choose a group to scrape members from:')
    i=0
    for group in groups:
        print('(' + str(i) + ') - ' + group.title)
        i+=1

    g_index = input("Enter a Number: ")
    target_group=groups[int(g_index)]
    target_group_entity = client.get_entity(PeerChannel(target_group.id))

    users = []
    for user_scrape in client.iter_participants(target_group_entity):
        user = {}
        if user_scrape.username != None:
            user['username'] = user_scrape.username
        else:
            user['username'] = 'None'

        if user_scrape.id != None:
            user['id'] = int(user_scrape.id)
        else:
            user['id'] = 'None'

        if user_scrape.id != None:
            user['access_hash'] = int(user_scrape.access_hash)
        else:
            user['access_hash'] = 'None'

        if user_scrape.first_name != None:
            if user_scrape.last_name != None:
                user['name'] = user_scrape.first_name+" "+user_scrape.last_name
            else:
                user['name'] = user_scrape.first_name
        else:
            user['name'] = 'None'

        users.append(user)
        open("members.csv", 'a+', encoding='utf-8').write(user['username'] + "," + str(int(user['id'])) + "," + str(int(user['access_hash'])) + "," + user['name'] + "\n")

    print(len(users), "members", "FROM", group.title)

except PhoneNumberBannedError:
    print("The used phone number has been banned from Telegram.")
except UserDeactivatedBanError:
    print("The user has been deleted/deactivated.")
except ChatAdminRequiredError:
    print("Chat admin privileges are required to do that in the specified chat (for example, to send a message in a channel which is not yours), or invalid permissions used for the channel or group.")
except ChatIdInvalidError:
    print("Invalid object ID for a chat. Make sure to pass the right types, for instance making sure that the request is designed for chats (not channels/megagroups) or otherwise look for a different one more suited\nAn example working with a megagroup and AddChatUserRequest, it will fail because megagroups are channels. Use InviteToChannelRequest instead.")
except InputUserDeactivatedError:
    print("The specified user was deleted.")
except PeerIdInvalidError:
    print("An invalid Peer was used. Make sure to pass the right peer type and that the value is valid (for instance, bots cannot start conversations).")
except UsersTooMuchError:
    print("The maximum number of users has been exceeded (to create a chat, for example).")
except UserAlreadyParticipantError:
    print("The authenticated user is already a participant of the chat.")
except UserIdInvalidError:
    print("Invalid object ID for a user. Make sure to pass the right types, for instance making sure that the request is designed for users or otherwise look for a different one more suited.")
except UserNotMutualContactError:
    print("The provided user is not a mutual contact.")
except Exception as e:
    print(e)

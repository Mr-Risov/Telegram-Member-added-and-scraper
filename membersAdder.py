import asyncio
import sys
import csv
import time
import random
from telethon.sync import TelegramClient, events
from telethon import functions, types
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel

from telethon.errors.rpcerrorlist import (ChatAdminRequiredError, UserChannelsTooMuchError, ChatIdInvalidError,
                                          InputUserDeactivatedError, UserNotMutualContactError, PeerIdInvalidError,
                                          UsersTooMuchError, UserIdInvalidError, UserAlreadyParticipantError,
                                          FloodWaitError, PeerFloodError, UserPrivacyRestrictedError,
                                          PhoneNumberBannedError, UserDeactivatedBanError)

async def main_work():
    phone = input("Enter your phone number: ")
    api_id = input("Enter your API ID: ")
    api_hash = input("Enter your API hash: ")

    try:
        async with TelegramClient(phone, api_id, api_hash) as client:
            await client.connect()

            if not await client.is_user_authorized():
                await client.send_code_request(phone)
                client.sign_in(phone, input('Enter the code: '))

            input_file = "members.csv"
            users = []
            with open(input_file, encoding='UTF-8') as f:
                rows = csv.reader(f, delimiter=",", lineterminator="\n")
                next(rows, None)
                for row in rows:
                    user = {}
                    user['username'] = row[0]
                    user['id'] = int(row[1])
                    user['access_hash'] = int(row[2])
                    user['name'] = row[3]
                    users.append(user)

            chats = []
            last_date = None
            chunk_size = 200
            groups = []

            result = await client(GetDialogsRequest(
                offset_date=last_date,
                offset_id=0,
                offset_peer=InputPeerEmpty(),
                limit=chunk_size,
                hash=0
            ))

            chats.extend(result.chats)

            for chat in chats:
                try:
                    if chat.megagroup == True:
                        groups.append(chat)
                except:
                    continue

            print('Choose a group to add members:')
            for i, group in enumerate(groups):
                print('(' + str(i) + ') - ' + group.title)

            g_index = int(input("Enter a Number: "))
            target_group = groups[g_index]
            target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)

            n = 0
            for user in users:
                n += 1
                if n % 50 == 0:
                    print("Sleep for 900 sec for every 50")
                    time.sleep(1800)
                    print(n)

                try:
                    if user['username'] != "None":
                        print("({}) Adding {}".format(n, user['username']))

                        user_to_add = await client.get_entity(user['username'])

                        if user_to_add != "ERROR":
                            try:
                                print("Waiting for 15-30 Seconds before adding...", user['username'], "(", "ID:",
                                      user['id'], ")", user['name'])
                                time.sleep(random.randrange(15, 30))
                                result = await client(InviteToChannelRequest(target_group_entity, [user_to_add]))
                                print(user['username'], "Added or Already in the Group!")
                            except FloodWaitError as e:
                                print(e)
                            except PeerFloodError:
                                print("Too many requests.")
                            except UserChannelsTooMuchError:
                                print("One of the users you tried to add is already in too many channels/supergroups.")
                            except UserPrivacyRestrictedError:
                                print("The user's privacy settings do not allow you to do this.")
                            except Exception as e:
                                print(e)

                        print("Waiting for 15-30 Seconds after adding...")
                        time.sleep(random.randrange(15, 30))

                except ValueError as e:
                    print(e)
                    time.sleep(0.5)
                    if user['username'] == "None":
                        print("{} SKIPPED".format(user['id']))
                    else:
                        print("{} SKIPPED".format(user['username']))

            print("Finished!")

    except PhoneNumberBannedError:
        print("The used phone number has been banned from Telegram.")
    except UserDeactivatedBanError:
        print("The user has been deleted/deactivated.")
    except ChatAdminRequiredError:
        print("Chat admin privileges are required to do that in the specified chat.")
    except ChatIdInvalidError:
        print("Invalid object ID for a chat.")
    except InputUserDeactivatedError:
        print("The specified user was deleted.")
    except PeerIdInvalidError:
        print("An invalid Peer was used.")
    except UsersTooMuchError:
        print("The maximum number of users has been exceeded.")
    except UserAlreadyParticipantError:
        print("The authenticated user is already a participant of the chat.")
    except UserIdInvalidError:
        print("Invalid object ID for a user.")
    except UserNotMutualContactError:
        print("The provided user is not a mutual contact.")
    except Exception as e:
        print(e)

asyncio.run(main_work())

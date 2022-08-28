from telethon import TelegramClient
import asyncio

api_id = 17467734
api_hash = '267e6ccae90d26d7d02ac689976e7961'
session_name = 'test/test'

client = TelegramClient(session_name, api_id, api_hash)
client.start()

loop = asyncio.get_event_loop()
get_users = lambda chat_id: loop.run_until_complete(get_members(chat_id))


async def get_members(chat_id):
    all_members = []

    async with client:
        async for user in client.iter_participants(chat_id):
            all_members.append(user)

    return all_members

print(get_users(-711319459))

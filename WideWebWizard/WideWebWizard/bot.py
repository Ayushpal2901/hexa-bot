from telethon.sync import TelegramClient, events
import asyncio
import os
import random

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

bot_username = '@HeXamonbot'

num_battles = 100
battle_counter = 0
awaiting_defeat_confirmation = False
watchdog_task = None

client = TelegramClient('session', api_id, api_hash)

@client.on(events.NewMessage(from_users=bot_username))
@client.on(events.MessageEdited(from_users=bot_username))
async def handle_bot_message(event):
    global battle_counter, awaiting_defeat_confirmation, watchdog_task
    msg = event.raw_text.lower()
    buttons = event.buttons

    if "a wild" in msg and "appeared" in msg:
        print("🐾 Wild Pokémon appeared!")
        awaiting_defeat_confirmation = True
        await asyncio.sleep(random.uniform(1, 2))
        await click_button(event, "battle")

    elif "current turn" in msg and "hp" in msg:
        print("⚔️ Turn to attack, choosing first move...")
        await asyncio.sleep(random.uniform(1, 2))
        await click_first_button(event)
        if watchdog_task:
            watchdog_task.cancel()
        watchdog_task = asyncio.create_task(hunt_watchdog())

    elif "you defeated" in msg or "pokedollars" in msg:
        print("✅ Pokémon defeated!")
        awaiting_defeat_confirmation = False
        if watchdog_task:
            watchdog_task.cancel()
        await asyncio.sleep(random.uniform(1, 2))
        battle_counter += 1
        print(f"🔥 Battles done: {battle_counter}")

        if battle_counter < num_battles:
            await asyncio.sleep(random.uniform(2, 3))
            print("🎯 Sending /hunt command")
            await client.send_message(bot_username, '/hunt')
        else:
            print("🏁 Target battle count reached.")
            await client.disconnect()

    elif "choose your pokemon" in msg:
        print("🔄 Switching Pokémon (if needed)...")
        await asyncio.sleep(random.uniform(1, 2))
        await click_first_button(event)

    elif "cooldown" in msg:
        print("🕒 Cooldown detected, waiting 10 seconds.")
        awaiting_defeat_confirmation = False
        if watchdog_task:
            watchdog_task.cancel()
        await asyncio.sleep(10)
        await client.send_message(bot_username, '/hunt')

    elif awaiting_defeat_confirmation and ("opponent hp" in msg or "current hp" in msg):
        print("⚠️ Opponent still alive, attacking again...")
        await asyncio.sleep(random.uniform(1, 2))
        await click_first_button(event)
        if watchdog_task:
            watchdog_task.cancel()
        watchdog_task = asyncio.create_task(hunt_watchdog())

    elif buttons:
        for i, row in enumerate(buttons):
            for j, button in enumerate(row):
                if "next" in button.text.lower():
                    print("➡️ Clicking Next Pokémon button")
                    await event.click(i, j)
                    await asyncio.sleep(random.uniform(1, 2))
                    if battle_counter < num_battles:
                        awaiting_defeat_confirmation = False
                        print("🎯 Sending /hunt command after next")
                        await client.send_message(bot_username, '/hunt')
                    return
                elif "battle" in button.text.lower():
                    print("🆚 Re-battle detected, clicking Battle again")
                    await event.click(i, j)
                    return

async def hunt_watchdog():
    await asyncio.sleep(7)
    print("⏱️ Watchdog triggered — no response, retrying /hunt...")
    await client.send_message(bot_username, '/hunt')

async def click_button(event, keyword, default_first=False):
    if event.buttons:
        for i, row in enumerate(event.buttons):
            for j, button in enumerate(row):
                if keyword.lower() in button.text.lower():
                    print(f"[+] Clicking button: {button.text}")
                    await event.click(i, j)
                    return
        if default_first:
            print(f"[!] '{keyword}' not found, clicking first button as fallback.")
            await event.click(0, 0)
    else:
        print("[-] No buttons to click.")

async def click_first_button(event):
    try:
        await event.click(0, 0)
        print("[+] Clicked first available option.")
    except Exception as e:
        print(f"[!] Error clicking first button: {e}")

async def main():
    await client.start()
    print("✅ Logged in! Starting automation...")
    await client.send_message(bot_username, '/hunt')
    await client.run_until_disconnected()

client.loop.run_until_complete(main())

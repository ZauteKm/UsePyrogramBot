#!/usr/bin/env python3
# Copyright (C) @ZauteKm
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import os
import time
from bot import bot, HU_APP
from pyromod import listen
from asyncio.exceptions import TimeoutError

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import (
    SessionPasswordNeeded, FloodWait,
    PhoneNumberInvalid, ApiIdInvalid,
    PhoneCodeInvalid, PhoneCodeExpired, UserNotParticipant
)
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, UsernameNotOccupied, ChatAdminRequired, PeerIdInvalid
from creds import Credentials

API_TEXT = """Hi, {}.
This is Pyrogram's String Session Generator Bot. I will generate String Session of your Telegram Account.

By @ZauteKm [dev]

Now send your `API_ID` same as `APP_ID` to Start Generating Session.

Get `APP_ID` from https://my.telegram.org or @UseTGzKBot."""
HASH_TEXT = "Now send your `API_HASH`.\n\nGet `API_HASH` from https://my.telegram.org Or @UseTGzKBot.\n\nPress /cancel to Cancel Task."
PHONE_NUMBER_TEXT = (
    "Now send your Telegram account's Phone number in International Format. \n"
    "Including Country code. Example: **+14154566376**\n\n"
    "Press /cancel to Cancel Task."
)

UPDATES_CHANNEL = os.environ.get('UPDATES_CHANNEL', 'ZauteKm')

@bot.on_message(filters.private & filters.command("start"))
async def genStr(_, msg: Message):
    if msg.chat.id in Credentials.BANNED_USERS:
        await bot.send_message(
            chat_id=msg.chat.id,
            text="You are Banned 🚫 to use me 🤭. Contact My [Support Group](https://t.me/InFoJosTelGroup)",
            reply_to_message_id=msg.message_id
        )
        return
    ## Doing Force Sub 🤣
    update_channel = UPDATES_CHANNEL
    if update_channel:
        try:
            user = await bot.get_chat_member(update_channel, msg.chat.id)
            if user.status == "kicked":
               await bot.send_message(
                   chat_id=msg.chat.id,
                   text="Sorry Sir, You are Banned!\nNow Your Can't Use Me. Contact my [Support Group](https://t.me/InFoJosTelGroup).",
                   parse_mode="markdown",
                   disable_web_page_preview=True
               )
               return
        except UserNotParticipant:
            await bot.send_message(
                chat_id=msg.chat.id,
                text="**Please Join My Updates Channel to use me! 😎**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Join Updates Channel 😎", url=f"https://t.me/{update_channel}")
                        ]
                    ]
                ),
                parse_mode="markdown"
            )
            return
        except Exception:
            await bot.send_message(
                chat_id=msg.chat.id,
                text="**Something went Wrong 🤪. Contact my [Support Group](https://t.me/InFoJosTelGroup).**",
                parse_mode="markdown",
                disable_web_page_preview=True
            )
            return

    chat = msg.chat
    api = await bot.ask(
        chat.id, API_TEXT.format(msg.from_user.mention)
    )
    if await is_cancel(msg, api.text):
        return
    try:
        check_api = int(api.text)
    except Exception:
        await msg.reply("`APP_ID` is Invalid.\nPress /start to Start again.")
        return
    api_id = api.text
    hash = await bot.ask(chat.id, HASH_TEXT)
    if await is_cancel(msg, hash.text):
        return
    if not len(hash.text) >= 30:
        await msg.reply("`API_HASH` is Invalid.\nPress /start to Start again.")
        return
    api_hash = hash.text
    while True:
        number = await bot.ask(chat.id, PHONE_NUMBER_TEXT)
        if not number.text:
            continue
        if await is_cancel(msg, number.text):
            return
        phone = number.text
        confirm = await bot.ask(chat.id, f'`Is "{phone}" correct? (y/n):` \n\nSend: `y` (If Yes)\nSend: `n` (If No)')
        if await is_cancel(msg, confirm.text):
            return
        if "y" in confirm.text:
            break
    try:
        client = Client("my_account", api_id=api_id, api_hash=api_hash)
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`\nPress /start to Start again.")
        return
    try:
        await client.connect()
    except ConnectionError:
        await client.disconnect()
        await client.connect()
    try:
        code = await client.send_code(phone)
        await asyncio.sleep(1)
    except FloodWait as e:
        await msg.reply(f"You have Floodwait of {e.x} Seconds")
        return
    except ApiIdInvalid:
        await msg.reply("APP ID and API Hash are Invalid.\n\nPress /start to Start again.")
        return
    except PhoneNumberInvalid:
        await msg.reply("Your Phone Number is Invalid.\n\nPress /start to Start again.")
        return
    try:
        otp = await bot.ask(
            chat.id, ("An OTP is sent to your phone number, "
                      "Please enter OTP in `1 2 3 4 5` format. __(Space between each numbers!)__ \n\n"
                      "If Bot not sending OTP then try /restart and Start Task again with /start command to Bot.\n"
                      "Press /cancel to Cancel."), timeout=300)

    except TimeoutError:
        await msg.reply("Time limit reached of 5 min.\nPress /start to Start again.")
        return
    if await is_cancel(msg, otp.text):
        return
    otp_code = otp.text
    try:
        await client.sign_in(phone, code.phone_code_hash, phone_code=' '.join(str(otp_code)))
    except PhoneCodeInvalid:
        await msg.reply("Invalid Code.\n\nPress /start to Start again.")
        return
    except PhoneCodeExpired:
        await msg.reply("Code is Expired.\n\nPress /start to Start again.")
        return
    except SessionPasswordNeeded:
        try:
            two_step_code = await bot.ask(
                chat.id, 
                "Your account have Two-Step Verification.\nPlease enter your Password.\n\nPress /cancel to Cancel.",
                timeout=300
            )
        except TimeoutError:
            await msg.reply("`Time limit reached of 5 min.\n\nPress /start to Start again.`")
            return
        if await is_cancel(msg, two_step_code.text):
            return
        new_code = two_step_code.text
        try:
            await client.check_password(new_code)
        except Exception as e:
            await msg.reply(f"**ERROR:** `{str(e)}`")
            return
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
        return
    try:
        session_string = await client.export_session_string()
        await client.send_message("me", f"***Your Pyrogram Session***\n\n```{session_string}``` \n\nBy [@UsePyrogramBot](tg://openmessage?user_id=1860890017) \n⬆️ This String Session is generated using https://replit.com/@ZauteKm/GenerateStringSession \nPlease subscribe ❤️ [@ZauTeKm](https://telegra.ph/ZauTe-Telegram-Official-Channel--Group-04-18)")
        await client.disconnect()
        text = "String Session is Successfully ✅ Generated.\nClick on Below Button."
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Show String Session ✅", url=f"tg://openmessage?user_id={chat.id}")]]
        )
        await bot.send_message(chat.id, text, reply_markup=reply_markup)
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
        return


@bot.on_message(filters.private & filters.command("restart"))
async def restart(_, msg: Message):
    await msg.reply("Restarted Bot!")
    HU_APP.restart()


@bot.on_message(filters.private & filters.command("help"))
async def restart(_, msg: Message):
    out = f"""
Hi, {msg.from_user.mention}. This is Pyrogram Session String Generator Bot. \
I will give you `STRING_SESSION` for your UserBot.

It needs `APP_ID`, `API_HASH`, Phone Number and One Time Verification Code. \
Which will be sent to your Phone Number.
You have to put **OTP** in `1 2 3 4 5` this format. __(Space between each numbers!)__

**NOTE:** If bot not Sending OTP to your Phone Number than send /restart Command and again send /start to Start your Process. 

Must Join Channel for Bot Updates !!
"""
    reply_markup = InlineKeyboardMarkup(
        [[
              InlineKeyboardButton('🗣️ Feedback', url='https://telegram.me/zautebot'),
              InlineKeyboardButton(' Channel 📢', url='https://telegram.me/TGBotsProJect')
              ],[
              InlineKeyboardButton('🙄 Source', url='https://githup.com/ZauteKm/UsePyrogramBot'),
              InlineKeyboardButton('Bot Lists 🤖', url='https://t.me/BotzListBot'),
              InlineKeyboardButton('Dev 🧑‍🔧', url='https://t.me/ZauteKm')
              ],[
              InlineKeyboardButton('🔻 Subscribe Now 🔻', url='http://t.me/GitHubOpenSource')
       ]]
    )
    await msg.reply(out, reply_markup=reply_markup)


async def is_cancel(msg: Message, text: str):
    if text.startswith("/cancel"):
        await msg.reply("Process Cancelled.")
        return True
    return False

if __name__ == "__main__":
    bot.run()

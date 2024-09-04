import os
import logging
from telegraph import upload_file
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable for the Force Sub Channel ID and Username
force_sub_channel_id = None  # To be set via /set_fsub command
force_sub_channel_username = None  # Store the username for reference

# Variable for authorized users (bot owner IDs)
AUTH_USERS = [6974737899]  # Replace with actual user IDs

Bot = Client(
    "Telegraph Uploader Bot",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH
)

DOWNLOAD_LOCATION = os.environ.get("DOWNLOAD_LOCATION", "downloads/telegraphbot.jpg")

START_TEXT = """👋 Hello {},

I am an under 5MB media or file to telegra.ph link uploader bot.

Made With ❤️‍🔥 by @Moviez_Botz"""

HELP_TEXT = """**About Me**

- Just give me a media under 5MB
- Then I will download it
- I will then upload it to the telegra.ph link

Made With ❤️‍🔥 by @Moviez_Botz
"""

ABOUT_TEXT = """**About Me**

- **Bot :** `Telegraph Uploader`
- **Developer :** @Moviez_Botz
- **Language :** [Python3](https://python.org)
- **Library :** [Pyrogram](https://pyrogram.org)"""

AJAS_TEXT = """👋 hey, iam 𝗣𝗔𝗟𝗔𝗞𝗚𝗔𝗟 𝗔𝗝𝗔𝗦,

Dont be oversmart infront of me🤬

❌ You still need to join our channel to use the bot. Please join the channel and click 'I Subscribed ✅' again."""

START_BUTTONS = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton('📢 UPDATES CHANNEL', url='https://telegram.me/moviez_botz')],
        [
            InlineKeyboardButton('✨ HELP', callback_data='help'),
            InlineKeyboardButton('⚠️ ABOUT', callback_data='about'),
            InlineKeyboardButton('CLOSE ⛔', callback_data='close')
        ]
    ]
)

HELP_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('💸 HOME', callback_data='home'),
            InlineKeyboardButton('⚠️ ABOUT', callback_data='about'),
            InlineKeyboardButton('CLOSE ⛔', callback_data='close')
        ]
    ]
)

ABOUT_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('💸 HOME', callback_data='home'),
            InlineKeyboardButton('⚠️ ABOUT', callback_data='about'),
            InlineKeyboardButton('CLOSE ⛔', callback_data='close')
        ]
    ]
)

async def force_sub(bot, message):
    if not force_sub_channel_id:
        logger.error("Force subscription channel is not set.")
        await message.reply_text("❌ Force subscription channel is not set. Contact the bot owner.")
        return False

    try:
        logger.info(f"Checking if user is a member of the channel with ID: {force_sub_channel_id}")
        user = await bot.get_chat_member(force_sub_channel_id, message.from_user.id)

        if user.status in ["member", "administrator", "creator"]:
            logger.info("User is a member of the channel.")
            return True
    except UserNotParticipant:
        logger.warning("User is not a participant in the channel.")
    except ChatAdminRequired:
        logger.error("Bot needs to be an admin in the channel to generate an invite link.")
        await message.reply_text("❌ I need to be an admin in the channel to generate an invite link.")
        return False
    except Exception as e:
        logger.error(f"Error in force_sub: {e}")
        await message.reply_text(f"An error occurred: {e}")
        return False

    try:
        invite_link = await bot.export_chat_invite_link(force_sub_channel_id)
    except ChatAdminRequired:
        logger.error("Bot needs to be an admin in the channel to generate an invite link.")
        await message.reply_text("❌ I need to be an admin in the channel to generate an invite link.")
        return False

    await message.reply_text(
        text=f"❌ To use this bot, you must join [our channel]({invite_link}) first.",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('Join Channel', url=invite_link)],
                [InlineKeyboardButton('✅ I Subscribed', callback_data='check_subscription')]
            ]
        )
    )
    return False


@Bot.on_message(filters.private & filters.command("set_fsub"))
async def set_fsub(bot, message: Message):
    global force_sub_channel  # Reference the global variable
    
    # Check if the user is authorized (e.g., bot owner or admin)
    if message.from_user.id not in AUTH_USERS:
        await message.reply_text("❌ You are not authorized to use this command.")
        return
    
    # Validate the command input
    if len(message.text.split(" ", 1)) < 2:
        await message.reply_text("❌ Please provide a valid channel username (e.g., /set_fsub @channelusername).")
        return
    
    # Get the new channel from the command arguments
    new_channel = message.text.split(" ", 1)[1].strip()
    if not new_channel.startswith("@"):
        await message.reply_text("❌ Please provide a valid channel username starting with '@'.")
        return
    
    # Resolve the channel ID from the username
    try:
        channel_info = await bot.get_chat(new_channel)
        force_sub_channel = new_channel
        await message.reply_text(f"✅ Force subscription channel updated to: {new_channel}")
    except Exception as e:
        await message.reply_text(f"❌ Error updating channel: {e}")
        return


@Bot.on_callback_query()
async def cb_data(bot, callback_query):
    data = callback_query.data
    message = callback_query.message

    if data == "home":
        await message.edit_text(
            text=START_TEXT.format(callback_query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=START_BUTTONS
        )
    elif data == "help":
        await message.edit_text(
            text=HELP_TEXT,
            disable_web_page_preview=True,
            reply_markup=HELP_BUTTONS
        )
    elif data == "about":
        await message.edit_text(
            text=ABOUT_TEXT,
            disable_web_page_preview=True,
            reply_markup=ABOUT_BUTTONS
        )
    elif data == "check_subscription":
        # Recheck if the u



@Bot.on_message(filters.private & filters.command(["start"]))
async def start(bot, update):
    if not await force_sub(bot, update):
        return
    
    await update.reply_text(
        text=START_TEXT.format(update.from_user.mention),
        disable_web_page_preview=True,
        quote=True,
        reply_markup=START_BUTTONS
    )


@Bot.on_message(filters.private & (filters.media | filters.command(["upload", "other_command"])))
async def getmedia(bot, message: Message):
    if not await force_sub(bot, message):
        return
    
    message_id = message.message_id
    medianame = DOWNLOAD_LOCATION + str(message_id)
    
    try:
        processing_message = await message.reply_text(
            text="`Processing...`",
            disable_web_page_preview=True
        )
        await message.download(file_name=medianame)
        response = upload_file(medianame)
        try:
            os.remove(medianame)
        except:
            pass
    except Exception as error:
        text=f"Error :- <code>{error}</code>"
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('More Help', callback_data='help')]]
        )
        await processing_message.edit_text(
            text=text,
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )
        return
    
    text=f"`https://telegra.ph{response[0]}`"
    reply_markup=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="OPEN LINK ↗️", url=f"https://telegra.ph{response[0]}"),
                InlineKeyboardButton(text="SHARE LINK ↩️", url=f"https://telegram.me/share/url?url=https://telegra.ph{response[0]}")
            ],
            [
                InlineKeyboardButton(text="🔰 JOIN UPDATES CHANNEL 🔰", url=f"https://t.me/{force_sub_channel_username}")
            ]
        ]
    )
    
    await processing_message.edit_text(
        text=text,
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )


Bot.run()

To ensure that users who join the channel after receiving the alert message are able to use the bot without being prompted again, you can modify the code slightly. Specifically, you'll need to store the user ID temporarily once they have clicked the "I Subscribed ✅" button and successfully checked their subscription. Here's how to implement this:

### Updated Code with Persistent User Check

```python
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

# Global variables for the Force Sub Channel
force_sub_channel = None
force_sub_channel_id = None

# Variable for authorized users (bot owner IDs)
AUTH_USERS = [6974737899]  # Replace with actual user IDs

# Temporarily store users who have verified their subscription
verified_users = set()

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
    global force_sub_channel_id

    # Check if the user is already verified
    if message.from_user.id in verified_users:
        return True

    try:
        logger.info(f"Checking if user is a member of the channel with ID: {force_sub_channel_id}")
        user = await bot.get_chat_member(force_sub_channel_id, message.from_user.id)

        # If the user is already a member, allow access and add them to the verified_users set
        if user.status in ["member", "administrator", "creator"]:
            logger.info("User is a member of the channel.")
            verified_users.add(message.from_user.id)  # Add to verified users
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

    # If the user is not subscribed, send the force subscription message
    try:
        invite_link = await bot.export_chat_invite_link(force_sub_channel_id)
    except ChatAdminRequired:
        logger.error("Bot needs to be an admin in the channel to generate an invite link.")
        await message.reply_text("❌ I need to be an admin in the channel to generate an invite link.")
        return False

    # Send a message with a "Check Subscription" button
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
    global force_sub_channel, force_sub_channel_id
    
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
        force_sub_channel_id = channel_info.id
        await message.reply_text(f"✅ Force subscription channel updated to: {new_channel}")
    except Exception as e:
        await message.reply_text(f"❌ Error updating channel: {e}")
        return


@Bot.on_message(filters.private & filters.command("info"))
async def user_info(bot, message: Message):
    user = message.from_user
    user_info_text = f"""
**User Info:**
- **User ID:** `{user.id}`
- **First Name:** `{user.first_name}`
- **Last Name:** `{user.last_name or 'N/A'}`
- **Username:** `{user.username or 'N/A'}`
- **Language Code:** `{user.language_code}`
"""
    
    await message.reply_text(user_info_text)


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
        # Recheck if the user is now subscribed
        if await force_sub(bot, message):
            await message.edit_text(
                text="✅ Thank you for subscribing! You can now use the bot.",
                disable_web_page_preview=True,
                reply_markup=START_BUTTONS
            )
        else:
            # Send an alternate message with a photo if the user hasn't joined the channel
            await message.edit_text(
                text=AJAS_TEXT,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton('Join Channel', url=await bot.export_chat_invite_link(force_sub_channel))],
                        [InlineKeyboardButton('✅ I Subscribed', callback_data='check_subscription')]
                    ]
                )
            )
    else:
        await message.delete()


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
        text = f"Error :- <code>{error}</code>"
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton('More Help', callback_data='help')]]
        )
        await processing_message.edit_text(
            text=text,
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )
        return
    
    text = f"`https://telegra.ph{response[0]}`"
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="OPEN LINK ↗️", url=f"https://telegra.ph{response[0]}"),
                InlineKeyboardButton(text="SHARE LINK ⬆️", url=f"https://telegram.me/share/url?url=https://telegra.ph{response[0]}")
            ],
            [
                InlineKeyboardButton('⚠️ ABOUT', callback_data='about'),
                InlineKeyboardButton('CLOSE ⛔', callback_data='close')
            ]
        ]
    )
    await processing_message.edit_text(
        text=text,
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )


@Bot.on_message(filters.command("restart") & filters.user(AUTH_USERS))
async def restart(bot, message):
    await message.reply_text("Restarting...")
    os.execv(sys.executable, ['python'] + sys.argv)


if __name__ == "__main__":
    Bot.run()

import os
import logging
import asyncio
import aiohttp
import requests
import subprocess
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.constants import ParseMode

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = "8322816910:AAF-2uIjpy1BJTy8xsrCrvgSOrh4yuaEh2s"
ADMIN_ID = 6593860853
CHANNEL_LINK = "https://t.me/animewallperess"
SHRINKEARN_API = "99a63d500ee702637ffd27ec4207e249654e3ff6"
GOFILE_TOKEN = "2wFdfqpRdzSy4SWs99PdhjHdHYuEQAxt"
GOFILE_FOLDER_ID = "f1233e99-86d3-4759-919d-512cec4b7109"

# States for conversation
PREVIEW_FILE, FULL_FILE, ANIMATION_NAME, SUMMARY, CATEGORY, CHANNEL_NAME = range(6)

# Temporary storage
TEMP_DIR = Path('/tmp/motion_bgs')
TEMP_DIR.mkdir(exist_ok=True)

class MotionBgBot:
    def __init__(self):
        self.user_data = {}

    def check_admin(self, user_id):
        return user_id == ADMIN_ID

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        user_id = update.effective_user.id

        if not self.check_admin(user_id):
            await update.message.reply_text("⛔ **Access Denied!**\n\nThis bot is private.", parse_mode=ParseMode.MARKDOWN)
            return

        welcome_text = """
🎬 **Motion Background Bot** 🎨

**Welcome Boss!** 👑

**How to use:**
1️⃣ Send **Preview Video** (Low Quality)
2️⃣ Send **Full 4K Video**
3️⃣ Enter **Animation Name**
4️⃣ Enter **Summary/Description**
5️⃣ Enter **Category**
6️⃣ Enter **Channel Name** (with @)

Bot will:
✅ Upload 4K to GoFile
✅ Shorten link via Shrinkearn
✅ Generate formatted post

**Send /create to start!** 🚀
        """
        await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

    async def create_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start creation process"""
        user_id = update.effective_user.id

        if not self.check_admin(user_id):
            return ConversationHandler.END

        self.user_data[user_id] = {}
        await update.message.reply_text(
            "🎬 **Step 1/6**\n\n"
            "Send me the **Preview Video** (Low Quality):\n"
            "_This will be shown at top of post_",
            parse_mode=ParseMode.MARKDOWN
        )
        return PREVIEW_FILE

    async def receive_preview(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Receive preview video"""
        user_id = update.effective_user.id

        if not update.message.video and not update.message.document:
            await update.message.reply_text("❌ Please send a video file!")
            return PREVIEW_FILE

        try:
            # Get video file
            if update.message.video:
                video = update.message.video
                file_id = video.file_id
            else:
                document = update.message.document
                if not document.mime_type or not document.mime_type.startswith('video/'):
                    await update.message.reply_text("❌ Please send a valid video file!")
                    return PREVIEW_FILE
                file_id = document.file_id

            # Download file
            file = await context.bot.get_file(file_id)
            preview_path = TEMP_DIR / f"preview_{user_id}.mp4"

            await file.download_to_drive(preview_path)
            self.user_data[user_id]['preview_path'] = str(preview_path)

            await update.message.reply_text(
                "✅ **Preview saved!**\n\n"
                "🎬 **Step 2/6**\n"
                "Now send me the **Full 4K Video**:",
                parse_mode=ParseMode.MARKDOWN
            )
            return FULL_FILE

        except Exception as e:
            logger.error(f"Error saving preview: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
            return PREVIEW_FILE

    async def receive_full(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Receive full 4K video"""
        user_id = update.effective_user.id

        if not update.message.video and not update.message.document:
            await update.message.reply_text("❌ Please send a video file!")
            return FULL_FILE

        try:
            # Get video file
            if update.message.video:
                video = update.message.video
                file_id = video.file_id
            else:
                document = update.message.document
                if not document.mime_type or not document.mime_type.startswith('video/'):
                    await update.message.reply_text("❌ Please send a valid video file!")
                    return FULL_FILE
                file_id = document.file_id

            # Download file
            file = await context.bot.get_file(file_id)
            full_path = TEMP_DIR / f"full_{user_id}.mp4"

            await update.message.reply_text("⏳ Downloading 4K video... Please wait!")
            await file.download_to_drive(full_path)
            self.user_data[user_id]['full_path'] = str(full_path)

            await update.message.reply_text(
                "✅ **4K Video saved!**\n\n"
                "🎬 **Step 3/6**\n"
                "Enter the **Animation Name**:\n"
                "_Example: Neon Cyberpunk City_",
                parse_mode=ParseMode.MARKDOWN
            )
            return ANIMATION_NAME

        except Exception as e:
            logger.error(f"Error saving full video: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
            return FULL_FILE

    async def receive_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Receive animation name"""
        user_id = update.effective_user.id
        name = update.message.text.strip()

        if not name:
            await update.message.reply_text("❌ Name cannot be empty! Try again:")
            return ANIMATION_NAME

        self.user_data[user_id]['name'] = name

        await update.message.reply_text(
            "✅ **Name saved!**\n\n"
            "🎬 **Step 4/6**\n"
            "Enter the **Summary/Description**:\n"
            "_Write an attractive bio for this animation_",
            parse_mode=ParseMode.MARKDOWN
        )
        return SUMMARY

    async def receive_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Receive summary"""
        user_id = update.effective_user.id
        summary = update.message.text.strip()

        if not summary:
            await update.message.reply_text("❌ Summary cannot be empty! Try again:")
            return SUMMARY

        self.user_data[user_id]['summary'] = summary

        await update.message.reply_text(
            "✅ **Summary saved!**\n\n"
            "🎬 **Step 5/6**\n"
            "Enter the **Category**:\n"
            "_Example: Cyberpunk, Nature, Abstract, Gaming_",
            parse_mode=ParseMode.MARKDOWN
        )
        return CATEGORY

    async def receive_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Receive category"""
        user_id = update.effective_user.id
        category = update.message.text.strip()

        if not category:
            await update.message.reply_text("❌ Category cannot be empty! Try again:")
            return CATEGORY

        self.user_data[user_id]['category'] = category

        await update.message.reply_text(
            "✅ **Category saved!**\n\n"
            "🎬 **Step 6/6**\n"
            "Enter the **Channel Name** (with @):\n"
            "_Example: @animewallperess_",
            parse_mode=ParseMode.MARKDOWN
        )
        return CHANNEL_NAME

    async def receive_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Receive channel name and process everything"""
        user_id = update.effective_user.id
        channel = update.message.text.strip()

        if not channel.startswith('@'):
            await update.message.reply_text("❌ Channel must start with @! Try again:")
            return CHANNEL_NAME

        self.user_data[user_id]['channel'] = channel

        # Start processing
        processing_msg = await update.message.reply_text(
            "⏳ **Processing...**\n\n"
            "📤 Uploading 4K to GoFile...\n"
            "Please wait, this may take a few minutes!",
            parse_mode=ParseMode.MARKDOWN
        )

        try:
            # Get file paths
            preview_path = self.user_data[user_id]['preview_path']
            full_path = self.user_data[user_id]['full_path']
            name = self.user_data[user_id]['name']
            summary = self.user_data[user_id]['summary']
            category = self.user_data[user_id]['category']

            # Upload to GoFile
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                text="⏳ **Processing...**\n\n"
                     "✅ Files received\n"
                     "📤 Uploading 4K to GoFile...",
                parse_mode=ParseMode.MARKDOWN
            )

            gofile_link = await self.upload_to_gofile(full_path)
            if not gofile_link:
                raise Exception("Failed to upload to GoFile")

            # Shorten link
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                text="⏳ **Processing...**\n\n"
                     "✅ Files received\n"
                     "✅ Uploaded to GoFile\n"
                     "🔗 Shortening link via Shrinkearn...",
                parse_mode=ParseMode.MARKDOWN
            )

            short_link = self.shorten_url(gofile_link)

            # Generate formatted message
            formatted_text = self.generate_format(
                name, summary, category, channel, short_link
            )

            # Delete processing message
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id
            )

            # Send preview video with caption
            keyboard = [[InlineKeyboardButton("🔥 GET 4K VERSION ⬇️ 💎", url=short_link)]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            with open(preview_path, 'rb') as preview_file:
                await update.message.reply_video(
                    video=preview_file,
                    caption=formatted_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )

            # Cleanup
            self.cleanup_files(user_id)

        except Exception as e:
            logger.error(f"Processing error: {e}")
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id,
                text=f"❌ **Error:**\n{str(e)}",
                parse_mode=ParseMode.MARKDOWN
            )
            self.cleanup_files(user_id)

        return ConversationHandler.END

    def generate_format(self, name, summary, category, channel, short_link):
        """Generate the formatted message"""
        # Create hashtag from name
        name_hashtag = '#' + name.replace(' ', '').replace('-', '').replace('_', '')
        category_hashtag = '#' + category.replace(' ', '')

        format_text = f"""┌─────────────────────────────────────────┐
│                                         │
│  🎬 **{name.upper()}** 🔥                │
│                                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                         │
│  📝 _*Summary:*_                        │
│  _{summary}_                            │
│                                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                         │
│  📢 **Channel:** {channel}              │
│                                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                         │
│  🔗 **Download 4K:** [Click Here]({short_link}) │
│                                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                         │
│  🏷️ **Tags:**                           │
│  {name_hashtag} #MotionBackground       │
│  #4K {category_hashtag} #Animation      │
│                                         │
└─────────────────────────────────────────┘"""

        return format_text

    async def upload_to_gofile(self, file_path):
        """Upload file to GoFile"""
        try:
            # Get best server
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.gofile.io/servers') as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('status') == 'ok' and data.get('data', {}).get('servers'):
                            server = data['data']['servers'][0]['name']
                            upload_url = f"https://{server}.gofile.io/uploadFile"
                        else:
                            upload_url = "https://store.gofile.io/uploadFile"
                    else:
                        upload_url = "https://store.gofile.io/uploadFile"

            # Upload file
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'video/mp4')}
                data = {
                    'token': GOFILE_TOKEN,
                    'folderId': GOFILE_FOLDER_ID
                }

                response = requests.post(upload_url, files=files, data=data, timeout=300)

                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'ok':
                        return result['data']['downloadPage']

                logger.error(f"GoFile upload failed: {response.text}")
                return None

        except Exception as e:
            logger.error(f"GoFile upload error: {e}")
            return None

    def shorten_url(self, url):
        """Shorten URL using Shrinkearn"""
        try:
            api_url = "https://shrinkearn.com/api"
            params = {
                'api': SHRINKEARN_API,
                'url': url,
                'format': 'text'
            }

            response = requests.get(api_url, params=params, timeout=30)
            if response.status_code == 200:
                shortened = response.text.strip()
                if shortened and shortened.startswith('http'):
                    return shortened

            logger.warning(f"Shrinkearn failed, using original URL")
            return url

        except Exception as e:
            logger.error(f"Shrinkearn error: {e}")
            return url

    def cleanup_files(self, user_id):
        """Clean up temporary files"""
        try:
            preview_path = TEMP_DIR / f"preview_{user_id}.mp4"
            full_path = TEMP_DIR / f"full_{user_id}.mp4"

            for file_path in [preview_path, full_path]:
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Cleaned up: {file_path}")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel conversation"""
        user_id = update.effective_user.id
        self.cleanup_files(user_id)

        await update.message.reply_text(
            "❌ **Cancelled!**\nAll data cleared.",
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END

# Initialize bot
motion_bot = MotionBgBot()

def main():
    """Start the bot"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('create', motion_bot.create_start)],
        states={
            PREVIEW_FILE: [MessageHandler(filters.VIDEO | filters.Document.VIDEO, motion_bot.receive_preview)],
            FULL_FILE: [MessageHandler(filters.VIDEO | filters.Document.VIDEO, motion_bot.receive_full)],
            ANIMATION_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, motion_bot.receive_name)],
            SUMMARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, motion_bot.receive_summary)],
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, motion_bot.receive_category)],
            CHANNEL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, motion_bot.receive_channel)],
        },
        fallbacks=[CommandHandler('cancel', motion_bot.cancel)],
    )

    application.add_handler(CommandHandler("start", motion_bot.start))
    application.add_handler(conv_handler)

    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

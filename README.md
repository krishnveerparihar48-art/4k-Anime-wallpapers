# 🎬 Motion Background Bot

Telegram bot for creating formatted motion background posts with 4K download links.

## ✨ Features

- 🎥 Upload preview + 4K video
- ☁️ Auto-upload 4K to GoFile
- 🔗 Auto-shorten link via Shrinkearn
- 📱 Generate formatted post with box borders
- 🔒 Private bot (Admin only)

## 🚀 Deployment

### Railway Setup

1. Create new project on Railway
2. Connect GitHub repo
3. Deploy (no env vars needed - hardcoded)

## 🤖 Usage

1. Send `/start` - Check access
2. Send `/create` - Start creation
3. Follow steps:
   - Send preview video
   - Send 4K video
   - Enter name
   - Enter summary
   - Enter category
   - Enter channel name
4. Bot generates formatted post

## 📝 Output Format

```
┌─────────────────────────────────────────┐
│  [PREVIEW VIDEO]                        │
│  🎬 **ANIMATION NAME** 🔥               │
│  📝 _Summary..._                        │
│  📢 **Channel:** @channel               │
│  [🔥 GET 4K VERSION ⬇️ 💎 BUTTON]       │
│  🏷️ #Tags...                            │
└─────────────────────────────────────────┘
```

## ⚙️ Config (Hardcoded)

- Bot Token: Provided
- Admin ID: 6593860853
- GoFile Token: Provided
- Shrinkearn API: Provided

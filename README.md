# Telegram Event Bot

This bot collects event announcements, stores them, and publishes daily digests.

## Development setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Initialize the database:
   ```bash
   python -m db.seed
   ```
3. Run the bot:
   ```bash
   python -m bot.main
   ```

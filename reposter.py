# -*- coding: utf-8 -*-

import asyncpraw
import telegram
import schedule
import asyncio
from dotenv import load_dotenv
import os

load_dotenv('private/.env')

# Reddit API настройки
reddit = asyncpraw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent=os.getenv('REDDIT_USER_AGENT')
)

# Telegram API настройки
bot = telegram.Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))

# Subreddit to Telegram chat ID mapping
subreddit_chat_map = {
    'aww': os.getenv('AWW_CHAT_ID'),
    'memes': os.getenv('MEMES_CHAT_ID'),
    # Add more subreddits and their corresponding chat IDs here
}

# Set to store processed post IDs
processed_posts = set()

# Asynchronous function to get new posts with a timeout
async def get_new_posts(subreddit_name, limit=5):
    print(f"Fetching new posts from subreddit: {subreddit_name}")
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        new_posts = []
        async for post in subreddit.hot(limit=limit):
            if post.id not in processed_posts:
                new_posts.append(post)
                processed_posts.add(post.id)
        print(f"Retrieved {len(new_posts)} new posts")
        return new_posts
    except asyncio.TimeoutError:
        print(f"Timeout fetching posts from subreddit: {subreddit_name}")
    except Exception as e:
        print(f"Failed to fetch posts from subreddit {subreddit_name}: {e}")
    return []

# Asynchronous function to post images to Telegram with a timeout
async def post_images_to_telegram(subreddit_name, chat_id):
    print(f"Starting to post images to Telegram {chat_id}")
    try:
        new_posts = await get_new_posts(subreddit_name, limit=5)
        for post in new_posts:
            if post.url.endswith(('jpg', 'jpeg', 'png')):
                print(f"Posting image: {post.url}")
                try:
                    await bot.send_photo(chat_id=chat_id, photo=post.url)
                except Exception as e:
                    print(f"Failed to send photo to chat ID {chat_id}: {e}")
    except Exception as e:
        print(f"Failed to fetch posts from subreddit {subreddit_name}: {e}")
    print(f"Finished posting images to Telegram {chat_id}")

# Асинхронная функция для запуска задачи по расписанию
async def run_scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

# Schedule the tasks
for subreddit, chat_id in subreddit_chat_map.items():
    schedule.every(1).hour.do(lambda sub=subreddit, chat=chat_id: asyncio.create_task(post_images_to_telegram(sub, chat)))
    print(f"Scheduled task to post images from subreddit {subreddit} to Telegram chat {chat_id} every 1 hour")

# Основная функция
async def main():
    print("Running main function")
    await asyncio.gather(*(post_images_to_telegram(sub, chat) for sub, chat in subreddit_chat_map.items()))
    await run_scheduler()

if __name__ == "__main__":
    print("Starting the script")
    # Run the main event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
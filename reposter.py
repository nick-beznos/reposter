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
chat_id = os.getenv('AWW_CHAT_ID')

# Set to store processed post IDs
processed_posts = set()

# Асинхронная функция для получения новых постов
async def get_new_posts(subreddit_name, limit=5):
    print(f"Fetching new posts from subreddit: {subreddit_name}")
    subreddit = await reddit.subreddit(subreddit_name)
    new_posts = []
    async for post in subreddit.hot(limit=limit):
        if post.id not in processed_posts:
            new_posts.append(post)
            processed_posts.add(post.id)
    print(f"Retrieved {len(new_posts)} new posts")
    return new_posts

# Асинхронная функция для отправки изображений в Telegram
async def post_images_to_telegram():
    print("Starting to post images to Telegram")
    try:
        new_posts = await get_new_posts('aww', limit=5)
        for post in new_posts:
            if post.url.endswith(('jpg', 'jpeg', 'png')):
                print(f"Posting image: {post.url}")
                try:
                    await bot.send_photo(chat_id=chat_id, photo=post.url)
                except Exception as e:
                    print(f"Failed to send photo: {e}")
    except Exception as e:
        print(f"Failed to fetch posts: {e}")
    print("Finished posting images to Telegram")

# Асинхронная функция для запуска задачи по расписанию
async def run_scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

# Настройка расписания (например, каждые 1 минуту)
schedule.every(1).minute.do(lambda: asyncio.create_task(post_images_to_telegram()))
print("Scheduled task to post images every 1 minute")

# Основная функция
async def main():
    print("Running main function")
    await post_images_to_telegram()
    await run_scheduler()

if __name__ == "__main__":
    print("Starting the script")

    # Запуск основного цикла событий
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
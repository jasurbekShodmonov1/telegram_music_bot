import os
from aiogram import Bot, Dispatcher, types
# from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import executor
from googleapiclient.discovery import build

# Telegram Bot token
API_TOKEN = '7171784182:AAHl41PCwqZPVFb-5G4-z1RxX0XZ8pZBtHM'

# YouTube API key
YOUTUBE_API_KEY = 'AIzaSyCt0zmvwXohQ0aj6cnG0OrWyVTulF74dtI'

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Additional options after search
search_options_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
search_options_buttons.add("1. Search Again", "2. Main Menu")

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Hi! I'm a music bot. Please enter your query to search for music:")

@dp.message_handler()
async def process_message(message: types.Message):
    if message.text == "1. Search Again":
        await message.reply("Please enter your query to search for music:", reply_markup=types.ReplyKeyboardRemove())
    elif message.text == "2. Main Menu":
        await send_welcome(message)
    else:
        await search_music(message)

async def search_music(message: types.Message):
    query = message.text
    search_response = youtube.search().list(
        q=query,
        part='id',
        type='video',
        maxResults=5
    ).execute()

    videos = []
    for i, search_result in enumerate(search_response.get('items', []), start=1):
        if search_result['id']['kind'] == 'youtube#video':
            videos.append(search_result['id']['videoId'])
            await bot.send_message(message.chat.id, f"{i}. https://www.youtube.com/watch?v={search_result['id']['videoId']}")

    if videos:
        await bot.send_message(message.chat.id, "What would you like to do next?", reply_markup=search_options_buttons)
    else:
        await message.reply("Sorry, I couldn't find any music matching your query.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
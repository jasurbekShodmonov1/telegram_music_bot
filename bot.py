

from aiogram import executor
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Command
from youtube_search import YoutubeSearch
import youtube_dl

API_TOKEN = '7171784182:AAHl41PCwqZPVFb-5G4-z1RxX0XZ8pZBtHM'
YOUTUBE_API_KEY = 'AIzaSyCt0zmvwXohQ0aj6cnG0OrWyVTulF74dtI'

# Path to save downloaded audio files
SAVE_PATH = "audio_files"
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def get_youtube_dl_options(output_path):
    return {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,  # Turn off quiet mode to see more detailed errors
    }

async def search_music(query, max_results=10):
    results = YoutubeSearch(query, max_results=max_results).to_dict()
    return [{"title": result["title"], "id": result["id"]} for result in results]

async def download_audio(video_id):
    ydl_opts = get_youtube_dl_options(SAVE_PATH)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download(['https://www.youtube.com/watch?v=' + video_id])
        except youtube_dl.utils.DownloadError as e:
            print("Failed to download video:", e)  # Print error message for debugging
            return None
    return os.path.join(SAVE_PATH, f"{video_id}.mp3")

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.reply("Hello! Send me the name of the music you want to search for on YouTube.")

@dp.message_handler()
async def process_message(message: types.Message):
    music_query = message.text
    music_results = await search_music(music_query)
    if music_results:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for result in music_results:
            button_text = result["title"]
            callback_data = f"select_music_{result['id']}"
            keyboard.add(types.InlineKeyboardButton(text=button_text, callback_data=callback_data))
        await message.reply("Here are the search results:", reply_markup=keyboard)
    else:
        await message.reply("Sorry, I couldn't find the music you requested.")

@dp.callback_query_handler(lambda query: query.data.startswith('select_music'))
async def process_callback_select_music(callback_query: types.CallbackQuery):
    video_id = callback_query.data.split('_')[-1]  # Extracting video ID from callback data
    if len(video_id) != 11:
        await bot.send_message(callback_query.from_user.id, "The video ID seems invalid, please try another video.")
        return
    audio_file_path = await download_audio(video_id)
    if audio_file_path:
        with open(audio_file_path, "rb") as audio_file:
            await bot.send_audio(callback_query.from_user.id, audio_file, title="Audio file")
        os.remove(audio_file_path)  # Delete the downloaded audio file after sending
    else:
        await bot.send_message(callback_query.from_user.id, "Failed to download the audio. Please try again.")

# Start the bot
if __name__ == '__main__':

    executor.start_polling(dp, skip_updates=True)


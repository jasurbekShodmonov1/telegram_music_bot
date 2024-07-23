import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from youtubesearchpython import VideosSearch
import yt_dlp as youtube_dl  # Replace youtube_dl with yt_dlp

API_TOKEN = '7171784182:AAHl41PCwqZPVFb-5G4-z1RxX0XZ8pZBtHM'
YOUTUBE_API_KEY = 'AIzaSyCt0zmvwXohQ0aj6cnG0OrWyVTulF74dtI'

# Path to save downloaded audio files
SAVE_PATH = "audio_files"
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


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
        'noplaylist': True,  # Do not download playlists
        'no_warnings': True,  # Suppress warnings
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    }


async def search_music(query, max_results=10):
    videos_search = VideosSearch(query, limit=max_results)
    results = videos_search.result()['result']
    return [{"title": result["title"], "id": result["id"]} for result in results]


async def download_audio(video_id):
    ydl_opts = get_youtube_dl_options(SAVE_PATH)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download(['https://www.youtube.com/watch?v=' + video_id])
        except youtube_dl.DownloadError as e:
            print("Failed to download video:", e)  # Print error message for debugging
            return None
    return os.path.join(SAVE_PATH, f"{video_id}.mp3")


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello! Send me the name of the music you want to search for on YouTube.")


@dp.message()
async def process_message(message: types.Message):
    music_query = message.text
    music_results = await search_music(music_query)
    if music_results:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=result["title"], callback_data=f"select_music_{result['id']}")]
            for result in music_results
        ])
        await message.answer("Here are the search results:", reply_markup=keyboard)
    else:
        await message.answer("Sorry, I couldn't find the music you requested.")


@dp.callback_query()
async def process_callback_select_music(callback_query: types.CallbackQuery):
    video_id = callback_query.data.split('_')[-1]  # Extracting video ID from callback data
    # if len(video_id) != 11:
    #     await callback_query.answer("The video ID seems invalid, please try another video.")
    #     return

    audio_file_path = await download_audio(video_id)
    if audio_file_path:
        with open(audio_file_path, "rb") as audio_file:
            await bot.send_audio(callback_query.from_user.id, audio_file, title="Audio file")
        os.remove(audio_file_path)  # Delete the downloaded audio file after sending
    else:
        await bot.send_message(callback_query.from_user.id, "Failed to download the audio. Please try again.")


# Start the bot
if __name__ == '__main__':
    dp.run_polling(bot, skip_updates=True)

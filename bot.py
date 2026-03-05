import telebot
from telebot import types
import yt_dlp
import os
import glob

# التوكن الخاص بك
BOT_TOKEN = '8497130784:AAG-iBMss_drRkQaWRtPDxdM5nM_Fyx9PWA'
bot = telebot.TeleBot(BOT_TOKEN)

user_links = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🔥 أهلاً بك يا كرار في نسخة الـ Mega PRO المعدلة!\n\n"
        "✅ تم تعديل الكابشن ليظهر باسمك الشخصي.\n"
        "✅ تحميل من انستغرام، تيك توك، ويوتيوب.\n\n"
        "دز الرابط وتوكل على الله! \U0001F602"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    url = message.text.strip()
    if "http" not in url:
        bot.reply_to(message, "يابة دز رابط حقيقي، لا تخليني أرسبك بالإدارة! \U0001F602")
        return

    user_links[message.chat.id] = url
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("منخفضة 360p \U0001F4E6", callback_data="low"),
        types.InlineKeyboardButton("متوسطة 720p \U0001F4FA", callback_data="med"),
        types.InlineKeyboardButton("عالية High \U0001F31F", callback_data="high"),
        types.InlineKeyboardButton("صوت فقط MP3 🎵", callback_data="audio")
    )
    
    bot.reply_to(message, "📥 تم استلام الرابط بنجاح! اختار الجودة المطلوبة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def process_download(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    
    if not url: return

    bot.delete_message(chat_id, call.message.message_id)
    wait_msg = bot.send_message(chat_id, "⏳ جاري التحميل التكتيكي... انتظرني يا بطل! \U0001F602")

    format_map = {
        "low": "best[height<=360]/worst",
        "med": "best[height<=720]/best",
        "high": "best",
        "audio": "bestaudio/best"
    }
    
    selected_format = format_map.get(call.data)

    ydl_opts = {
        'format': selected_format,
        'outtmpl': f'krar_{chat_id}_%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
            files = glob.glob(f"krar_{chat_id}_*")
            if files:
                file_path = files[0]
                bot.send_chat_action(chat_id, 'upload_video')
                
                with open(file_path, 'rb') as f:
                    # هنا التعديل اللي طلبته: الكتابة اللي تظهر تحت الفيديو
                    custom_caption = "✅ تم التحميل بواسطة كرار بنجاح \U0001F60E"
                    
                    if call.data == "audio":
                        bot.send_audio(chat_id, f, caption=custom_caption)
                    else:
                        bot.send_video(chat_id, f, caption=custom_caption)
                
                os.remove(file_path)
            else:
                bot.send_message(chat_id, "❌ لم يتم العثور على الملف، جرب دقة أخرى.")

        bot.delete_message(chat_id, wait_msg.id)

    except Exception as e:
        bot.edit_message_text(f"❌ صار خطأ: {str(e)[:40]}...", chat_id=chat_id, message_id=wait_msg.id)
        for f in glob.glob(f"krar_{chat_id}_*"): os.remove(f)

print("✅ بوت كرار المطور شغال الآن!")
bot.infinity_polling()


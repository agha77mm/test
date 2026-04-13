import telebot
import time
from datetime import datetime
import yt_dlp
import os

TOKEN = "8736519494:AAFW81mpdCBXKg4Bom-juJ9-vh3PXWC4IOU"
bot = telebot.TeleBot(TOKEN)

# داتابەیسێکی سادە بۆ پاشەکەوتکردنی یاسا و ژمارەی نامەکان
group_data = {
    'rules': "یاساکان دیاری نەکراون.",
    'users': {}
}

def get_user_data(user_id):
    if user_id not in group_data['users']:
        group_data['users'][user_id] = {
            'messages': {'text': 0, 'photo': 0, 'video': 0, 'voice': 0, 'link': 0},
            'join_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'nicknames': []
        }
    return group_data['users'][user_id]

@bot.message_handler(func=lambda m: True)
def track_messages(message):
    user = get_user_data(message.from_user.id)
    if message.text:
        if "http" in message.text: user['messages']['link'] += 1
        else: user['messages']['text'] += 1
    elif message.content_type == 'photo': user['messages']['photo'] += 1
    elif message.content_type == 'video': user['messages']['video'] += 1
    elif message.content_type == 'voice': user['messages']['voice'] += 1
    
    # جێبەجێکردنی فەرمانەکان لەناو ئەم فانکشنەدا
    handle_commands(message)

def handle_commands(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    is_admin = bot.get_chat_member(chat_id, user_id).status in ['administrator', 'creator']

    # ١. بەخێرهاتن
    if message.content_types == ['new_chat_members']:
        for member in message.new_chat_members:
            welcome_msg = (
                f"سڵاو، بەخێربێیت بۆ گرووپ\n\n"
                f"ناوت: {member.first_name}\n"
                f"یوزەر: @{member.username if member.username else 'نییە'}\n"
                f"کاتی جۆین: {datetime.now().strftime('%H:%M')}\n\n"
                f"هیوای کاتێکی خۆش"
            )
            bot.send_message(chat_id, welcome_msg)

    # ٢. یاسا و سەیڤکردنی
    if message.text:
        cmd = message.text.lower()
        
        if cmd.startswith("یاسا:") and is_admin:
            group_data['rules'] = message.text.replace("یاسا:", "").strip()
            bot.reply_to(message, "یاساکان بە سەرکەوتوویی نوێ کرانەوە")
            
        elif cmd == "یاسا":
            bot.reply_to(message, f"یاساکانی گرووپ:\n\n{group_data['rules']}")

        # ٣. فەرمانی دەرچۆ و باند
        if message.reply_to_message:
            target_id = message.reply_to_message.from_user.id
            if cmd == "دەرچۆ" and is_admin:
                bot.kick_chat_member(chat_id, target_id)
                bot.unban_chat_member(chat_id, target_id)
                bot.reply_to(message, "ئەندامەکە دەرکرا")
            
            elif cmd == "باند" and is_admin:
                bot.kick_chat_member(chat_id, target_id)
                bot.reply_to(message, "ئەندامەکە باند کرا")

            # ٤. مویت (Mute)
            elif cmd.startswith("مویت") and is_admin:
                parts = cmd.split()
                duration = 7200 # ٢ سەعات وەک دیفۆڵت
                if len(parts) > 1 and parts[1].isdigit():
                    duration = int(parts[1]) * 60
                
                bot.restrict_chat_member(chat_id, target_id, until_date=time.time() + duration)
                bot.reply_to(message, f"ئەندامەکە بێدەنگ کرا بۆ ماوەی دیاریکراو")

            # ٥. ڕۆڵی شیرین یان نازناو
            elif cmd.startswith("ڕۆڵی") and is_admin:
                nickname = cmd.replace("ڕۆڵی", "").strip()
                target_user = message.reply_to_message.from_user
                user_info = get_user_data(target_id)
                user_info['nicknames'].append(nickname)
                bot.reply_to(message, f"نازناوی ({nickname}) بەخشرا بە {target_user.first_name}")

            # ٦. زانیاری
            elif cmd == "زانیاری":
                u = get_user_data(target_id)
                info = (
                    f"زانیاری ئەندام:\n"
                    f"ناو: {message.reply_to_message.from_user.first_name}\n"
                    f"یوزەر: @{message.reply_to_message.from_user.username}\n"
                    f"کاتی جۆین بۆ یەکەمجار: {u['join_date']}\n"
                    f"نازناوەکانی: {', '.join(u['nicknames']) if u['nicknames'] else 'نییە'}"
                )
                bot.reply_to(message, info)

        # ٧. نامەکانم
        if cmd == "نامەکانم":
            u = get_user_data(user_id)['messages']
            msg = (
                f"ئاماری چالاکییەکانت:\n\n"
                f"دەق: {u['text']}\n"
                f"وێنە: {u['photo']}\n"
                f"ڤیدیۆ: {u['video']}\n"
                f"ڤۆیس: {u['voice']}\n"
                f"لینک: {u['link']}"
            )
            bot.reply_to(message, msg)

        # ٨. یوتیوب (YT)
        if cmd.startswith(("yt ", "yt", "yt")):
            search_query = message.text[3:].strip()
            if not search_query: return
            
            m = bot.reply_to(message, "خەریکی گەڕانم...")
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'song.mp3',
                'quiet': True,
                'default_search': 'ytsearch1'
            }
            with yt_dl_app.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_query, download=True)
                title = info['entries'][0]['title']
                bot.send_audio(chat_id, open('song.mp3', 'rb'), caption=title)
                os.remove('song.mp3')
                bot.delete_message(chat_id, m.message_id)

        # ٩. فەرمانەکان
        if cmd == "فەرمانەکان":
            help_text = (
                "فەرمانەکانی بۆت:\n"
                "١. یاسا (بینینی یاساکان)\n"
                "٢. یاسا: (بۆ ئەدمین - دانانی یاسا)\n"
                "٣. نامەکانم (ئاماری نامەکان)\n"
                "٤. زانیاری (بە ڕیپلەی)\n"
                "٥. مویت، باند، دەرچۆ (بە ڕیپلەی - ئەدمین)\n"
                "٦. yt + ناوی گۆرانی (داگرتن لە یوتیوب)\n"
                "٧. ڕۆڵی [ناو] (بە ڕیپلەی - ئەدمین)"
            )
            bot.reply_to(message, help_text)

print("بۆتەکە بە سەرکەوتوویی کاری پێ کرا")
bot.infinity_polling()
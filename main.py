import telebot
import time
from datetime import datetime
import yt_dlp
import os

TOKEN = "8736519494:AAFW81mpdCBXKg4Bom-juJ9-vh3PXWC4IOU"
bot = telebot.TeleBot(TOKEN)

# داتابەیس بۆ پاشەکەوتکردنی زانیارییەکان
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

# بەشی بەخێرهاتن (بە جیا دانراوە بۆ ئەوەی باشتر کار بکات)
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    chat_id = message.chat.id
    group_name = message.chat.title
    for member in message.new_chat_members:
        welcome_msg = (
            f"سڵاو، بەخێربێیت بۆ گرووپی {group_name}\n\n"
            f"ناوت: {member.first_name}\n"
            f"یوزەر: @{member.username if member.username else 'نییە'}\n"
            f"کاتی جۆین: {datetime.now().strftime('%H:%M')}\n\n"
            f"هیوای کاتێکی خۆش و پابەندبوون بە یاساکان"
        )
        bot.send_message(chat_id, welcome_msg)

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'voice'])
def track_and_handle(message):
    user_id = message.from_user.id
    user = get_user_data(user_id)
    
    # تۆمارکردنی ئاماری نامەکان
    if message.text:
        if "http" in message.text: user['messages']['link'] += 1
        else: user['messages']['text'] += 1
    elif message.content_type == 'photo': user['messages']['photo'] += 1
    elif message.content_type == 'video': user['messages']['video'] += 1
    elif message.content_type == 'voice': user['messages']['voice'] += 1
    
    handle_commands(message)

def handle_commands(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # پشکنینی ئەدمین بوون
    try:
        member_status = bot.get_chat_member(chat_id, user_id).status
        is_admin = member_status in ['administrator', 'creator']
    except:
        is_admin = False

    if message.text:
        cmd = message.text.lower()
        
        # یاسا
        if cmd.startswith("یاسا:") and is_admin:
            group_data['rules'] = message.text.replace("یاسا:", "").strip()
            bot.reply_to(message, "یاساکان بە سەرکەوتوویی نوێ کرانەوە")
        elif cmd == "یاسا":
            bot.reply_to(message, f"یاساکانی گرووپ:\n\n{group_data['rules']}")

        # فەرمانەکانی ڕیپلەی
        if message.reply_to_message:
            target_id = message.reply_to_message.from_user.id
            target_name = message.reply_to_message.from_user.first_name
            
            if cmd == "دەرچۆ" and is_admin:
                bot.unban_chat_member(chat_id, target_id)
                bot.reply_to(message, f"ئەندام {target_name} دەرکرا")
            
            elif cmd == "باند" and is_admin:
                bot.kick_chat_member(chat_id, target_id)
                bot.reply_to(message, f"ئەندام {target_name} باند کرا")

            elif cmd.startswith("مویت") and is_admin:
                parts = cmd.split()
                duration = 7200 
                if len(parts) > 1 and parts[1].isdigit():
                    duration = int(parts[1]) * 60
                bot.restrict_chat_member(chat_id, target_id, until_date=time.time() + duration)
                bot.reply_to(message, f"ئەندام {target_name} بێدەنگ کرا")

            elif cmd.startswith("ڕۆڵی") and is_admin:
                nickname = message.text.replace("ڕۆڵی", "").strip()
                u_info = get_user_data(target_id)
                u_info['nicknames'].append(nickname)
                bot.reply_to(message, f"نازناوی ({nickname}) بەخشرا بە {target_name}")

            elif cmd == "زانیاری":
                u = get_user_data(target_id)
                info = (
                    f"زانیاری ئەندام:\n"
                    f"ناو: {target_name}\n"
                    f"یوزەر: @{message.reply_to_message.from_user.username}\n"
                    f"کاتی جۆین: {u['join_date']}\n"
                    f"نازناوەکان: {', '.join(u['nicknames']) if u['nicknames'] else 'نییە'}"
                )
                bot.reply_to(message, info)

        # نامەکانم
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

        # یوتیوب
        if cmd.startswith(("yt ", "yt", "yt")):
            search_query = message.text[3:].strip()
            if not search_query: return
            
            m = bot.reply_to(message, "خەریکی گەڕانم لە یوتیوب...")
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'song.mp3',
                'quiet': True,
                'default_search': 'ytsearch1',
                'nocheckcertificate': True
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(search_query, download=True)
                    title = info['entries'][0]['title']
                    bot.send_audio(chat_id, open('song.mp3', 'rb'), caption=title)
                    os.remove('song.mp3')
                    bot.delete_message(chat_id, m.message_id)
            except Exception as e:
                bot.edit_message_text("کێشەیەک لە دۆزینەوەی گۆرانییەکە هەبوو", chat_id, m.message_id)

        # فەرمانەکان
        if cmd == "فەرمانەکان":
            help_text = "لیستی فەرمانەکان:\n1. یاسا\n2. یاسا: [دەق]\n3. نامەکانم\n4. زانیاری (ڕیپلەی)\n5. مویت، باند، دەرچۆ (ڕیپلەی)\n6. yt [ناو]\n7. ڕۆڵی [ناو] (ڕیپلەی)"
            bot.reply_to(message, help_text)

print("بۆتەکە چالاکە...")
bot.infinity_polling()
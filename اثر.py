import telebot
from telebot import types
import json
import os

# --- الإعدادات الأساسية (تم وضع بياناتك هنا) ---
TOKEN = '8862106054:AAEOOIlmCoKGvll4a31WUjTO_0HxJauIkHY'
ADMIN_ID = 8709434061
bot = telebot.TeleBot(TOKEN)

# اسم ملف قاعدة البيانات البسيطة
DB_FILE = "athar_data.json"

# تحميل البيانات من الملف عند التشغيل لضمان عدم الضياع
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        data_storage = json.load(f)
else:
    data_storage = {'books': {}, 'guides': {}}

def save_to_db():
    with open(DB_FILE, "w") as f:
        json.dump(data_storage, f)

# --- المواد الدراسية ---
SUBJECTS = ['العربي', 'الانجليزي', 'الكيمياء', 'الفيزياء', 'الاحياء', 'الاسلامية', 'الرياضيات']

# --- لوحات المفاتيح ---
def main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add('📚 الكتب', '📋 الملازم', '📝 الاختبارات', '📓 الكراسة')
    return markup

def subjects_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*SUBJECTS, '🔙 العودة')
    return markup

# --- رسالة الترحيب ---
@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "مرحباً في بوت أثر\n\n"
        "\"مساحتكم الدراسية المتكاملة.. ملازم، ملخصات، ونصائح للتفوق. خُلقنا لنترك أثراً.\""
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_markup())

# --- نظام الرفع (أنت فقط تستخدمه بالرد على الملف) ---
@bot.message_handler(func=lambda m: m.reply_to_message is not None and m.from_user.id == ADMIN_ID)
def handle_upload(message):
    text = message.text.split()
    # الصيغة المعتمدة: "رفع ملزمة العربي" أو "رفع كتاب الفيزياء"
    if len(text) >= 3 and text[0] == 'رفع':
        category = 'guides' if text[1] == 'ملزمة' else 'books' if text[1] == 'كتاب' else None
        subject = text[2]

        if category and subject in SUBJECTS:
            file_id = None
            if message.reply_to_message.document:
                file_id = message.reply_to_message.document.file_id
            elif message.reply_to_message.photo:
                file_id = message.reply_to_message.photo[-1].file_id
            
            if file_id:
                data_storage[category][subject] = file_id
                save_to_db() # حفظ التغييرات فوراً في الملف
                bot.reply_to(message, f"✅ تم الرفع بنجاح لـ {text[1]} {subject}.")
            else:
                bot.reply_to(message, "❌ يرجى الرد على ملف أو صورة.")
        else:
            bot.reply_to(message, "❌ خطأ في الصيغة أو اسم المادة.")

# --- معالجة الضغط على الأزرار ---
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    uid = message.chat.id
    
    if message.text == '📚 الكتب':
        bot.send_message(uid, "اختر المادة لتحميل الكتاب المنهجي:", reply_markup=subjects_markup())
        bot.set_state(uid, "books", message.chat.id) # لتحديد القسم المطلوب
        
    elif message.text == '📋 الملازم':
        bot.send_message(uid, "اختر المادة لعرض المدرسين:", reply_markup=subjects_markup())
        bot.set_state(uid, "guides", message.chat.id)

    elif message.text == '🔙 العودة':
        bot.send_message(uid, "القائمة الرئيسية:", reply_markup=main_markup())

    elif message.text in SUBJECTS:
        # البحث عن القسم الذي اختاره المستخدم (كتب أم ملازم)
        current_state = bot.get_state(uid, message.chat.id)
        section = 'guides' if current_state == "guides" else 'books'
        
        file_id = data_storage[section].get(message.text)
        
        if file_id:
            bot.send_document(uid, file_id, caption=f"إليك {message.text} - أثر 🎓")
        else:
            bot.send_message(uid, "⚠️ لم يتم رفع هذا الملف بعد.")

    elif message.text == '📓 الكراسة':
        bot.send_message(uid, "هذا القسم قيد التطوير، يمكنك إرسال ملاحظتك وسنسجلها قريباً.")

# تشغيل البوت
if __name__ == '__main__':
    print("🚀 بوت أثر يعمل الآن بالآيدي والتوكن الخاص بك...")
    bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))
    bot.polling(none_stop=True)

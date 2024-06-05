import os
import json
import time
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Загрузка переменных из config.json файла
with open('config.json', 'r') as config_file:
    config = json.load(config_file)
TOKEN = config['BOT_TOKEN']
YOUR_TELEGRAM_ID = '345192124'
CODES_DIR = 'codes'
NAMES_FILE = 'names.json'
REQUEST_NAME, RECEIVE_NAME = range(2)

if not os.path.exists(CODES_DIR):
    os.makedirs(CODES_DIR)

# Инициализация names.json, если файл не существует или пуст
if not os.path.exists(NAMES_FILE) or os.path.getsize(NAMES_FILE) == 0:
    with open(NAMES_FILE, 'w') as f:
        json.dump({}, f)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Отправьте мне файл с кодом для проверки на плагиат.')


def save_code_file(file_path: str, code: str) -> None:
    with open(file_path, 'w') as f:
        f.write(code)


def check_plagiarism(new_code: str, existing_codes: list) -> list:
    codes = [new_code] + existing_codes
    vectorizer = TfidfVectorizer().fit_transform(codes)
    vectors = vectorizer.toarray()
    cosine_matrix = cosine_similarity(vectors)
    similarity_scores = cosine_matrix[0][1:]
    return similarity_scores


async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    document = update.message.document
    file = await context.bot.get_file(document.file_id)
    timestamp = int(time.time())
    file_path = f'{CODES_DIR}/{timestamp}_{document.file_name}'
    await file.download_to_drive(file_path)

    context.user_data['file_path'] = file_path

    # Добавляем проверку на идентификацию отправителя файла
    user_id = update.message.from_user.id
    if str(user_id) == YOUR_TELEGRAM_ID:
        await update.message.reply_text(f'Файл {document.file_name} получен. Пожалуйста, укажите фамилию автора.')
        return REQUEST_NAME
    else:
        await update.message.reply_text("Недостаточно прав для загрузки файла.")
        return ConversationHandler.END


async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    author_name = update.message.text
    file_path = context.user_data.get('file_path')

    if file_path:
        file_name = os.path.basename(file_path)

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            new_code = f.read()

        # Безопасное чтение файла names.json
        try:
            with open(NAMES_FILE, 'r') as f:
                names = json.load(f)
        except json.JSONDecodeError:
            names = {}

        existing_codes = []
        file_names = []

        for file in os.listdir(CODES_DIR):
            if file != file_name:
                with open(f'{CODES_DIR}/{file}', 'r', encoding='utf-8', errors='ignore') as f:
                    existing_codes.append(f.read())
                file_names.append(file)

        similarity_scores = check_plagiarism(new_code, existing_codes)

        top_matches = sorted(zip(file_names, similarity_scores), key=lambda x: x[1], reverse=True)[:3]

        result = "Топ 3 совпадения:\n"
        for match in top_matches:
            match_file = match[0]
            match_score = match[1] * 100  # Преобразование в процент
            match_author = next((author for author, files in names.items() if match_file in files), 'Unknown')
            result += f'{match_author}: {match_score:.2f}%\n'

        await update.message.reply_text(result)

        # Ассоциируем файл с автором
        if author_name not in names:
            names[author_name] = []
        names[author_name].append(file_name)

        # Безопасное сохранение файла names.json
        try:
            with open(NAMES_FILE, 'w') as f:
                json.dump(names, f)
            await update.message.reply_text('Фамилия автора сохранена.')
        except Exception as e:
            await update.message.reply_text(f'Ошибка при сохранении имени: {str(e)}')

    return ConversationHandler.END


def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Document.ALL, receive_file)],
        states={
            REQUEST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()

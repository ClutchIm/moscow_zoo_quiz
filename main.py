import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import random
from collections import Counter
from resources import *


bot = telebot.TeleBot(BOT_TOKEN)

# Store user progress and answers
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    """Send a welcome message and start the quiz."""
    user_id = message.chat.id

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Начать", callback_data="start_quiz"))

    bot.send_message(user_id, "Привет! Давайте узнаем ваше тотемное животное. Готовы начать?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "start_quiz")
def handle_start_quiz(call):
    """Start the quiz by sending the first question."""
    user_id = call.message.chat.id
    selected_questions = random.sample(questions_pool, 20)



    user_data[user_id] = {"answers": [], "current_question": 0, "questions": selected_questions,}

    user_data[user_id]["current_question"] = 0
    user_data[user_id]["answers"] = []
    send_question(call)

def send_question(call):
    """Send the current question with photo."""
    user_id = call.message.chat.id

    question_index = user_data[user_id]["current_question"]
    question_data = user_data[user_id]["questions"][question_index]

    photo_url = 'images/' + user_data[user_id]['questions'][question_index]["image"] + '.jpg'

    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(option, callback_data=f"answer_{index}")
        for index, option in enumerate(question_data["options"])
    ]
    markup.add(*buttons)

    with open(photo_url, "rb") as photo:
        bot.edit_message_media(
            media=InputMediaPhoto(media=photo, caption=question_data["question"]),
            chat_id=user_id,
            message_id=call.message.message_id,
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith("answer_"))
def handle_answer(call):
    """Handle the user's answer and move to the next question or show the result."""
    user_id = call.message.chat.id
    answer_index = int(call.data.split("_")[1])

    # Save the answer weight
    current_question = user_data[user_id]["current_question"]
    question_data = user_data[user_id]["questions"][current_question]
    animal = question_data["weights"][answer_index]
    user_data[user_id]["answers"].append(animal)

    # Move to the next question or finish the quiz
    user_data[user_id]["current_question"] += 1
    if user_data[user_id]["current_question"] < 10:
        send_question(call)
    else:
        show_result(call)

def show_result(call):
    """Calculate and display the quiz result."""
    user_id = call.message.chat.id

    # Find the most common animal in answers
    answers = user_data[user_id]["answers"]
    most_common_animal = Counter(answers).most_common(1)[0][0]

    # Show the result
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Узнать больше о программе опеки", url="https://moscowzoo.ru/about/guardianship"))
    markup.add(InlineKeyboardButton("Пройти снова", callback_data="start_quiz"))
    photo_url = 'images/' + most_common_animal + '.jpg'


    with open(photo_url, "rb") as photo:
        bot.edit_message_media(
            media=InputMediaPhoto(media=photo, caption=results[most_common_animal]),
            chat_id=user_id,
            message_id=call.message.message_id,
            reply_markup=markup
        )

if __name__ == "__main__":
    bot.polling(none_stop=True)

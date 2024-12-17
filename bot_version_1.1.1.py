from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, filters, ContextTypes, MessageHandler, CallbackQueryHandler
import openai
import os

BOT_TOKEN: Final = os.getenv('YOUR_BOT_TOKEN')
BOT_USERNAME: Final = '@Mr_dottu_bot'
openai.api_key = os.getenv('OPENAI_API_KEY')


# Start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("KEAM Question Papers",
                                 callback_data="keam_papers")
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Hi! I'm Mr.Dottu!! your Study Guide Bot. Here's what I can do:\n"
        "- Clear your doubts about topics.\n"
        "- Share study materials.\n\n"
        "Use /help for detailed instructions."
        "\n/about for more info"
        "Select an option:",
        reply_markup=reply_markup)


# Help Command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Here's how to use the bot:\n"
        "- Ask me any question, and I'll try to answer it.\n"
        "- Use /notes to request study materials.\n"
        "- For a list of available subjects, type /subjects.")


# about Command
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_text = """
Welcome to Franklin's Luctures!
Email : connect@franklinslectures.com
📞 Contact: +919074745741
🌐 Website: https://franklinslectures.in
  """
    keyboard = [[
        InlineKeyboardButton("Visit Website",
                             url="https://franklinslectures.in")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(info_text,
                                    reply_markup=reply_markup,
                                    parse_mode="Markdown")


# Responses


def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return "Hey There!"
    if 'hi' in processed:
        return "Hey There!"
    if 'how are you' in processed:
        return "I am good!"
    if "franklin's lectures" in processed:
        return "Website: https://franklinslectures.in"
    return get_gpt_response(text)


def get_gpt_response(query: str) -> str:
    try:
        # Request GPT response
        ai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": "You are a helpful assistant."
            }, {
                "role": "user",
                "content": query
            }],
            max_tokens=100)
        # Proper indentation of the response extraction
        response = ai_response['choices'][0]['message']['content'].strip()
        return response
    except Exception as e:
        return f"Sorry, something went wrong: {str(e)}"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
    print('Bot:', response)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'update {update} caused error{context.error}')

# Directory for KEAM question papers
keam_papers = {
    "2014": {
        "paper1": "1hPvQoMKd67Px2YvF1Nmr0teFAYOn8QMe",
        "paper2": "17r8Q3IAZHccHHO3vPFcoLLTgnIc1NLfo"
    },
    "2015": {
        "paper1": "1Qb5X4nw4fFb6rXud0BW8-oMugvEw_3GQ",
        "paper2": "1A5KS5-SoeowWv56FD0PCmQ5e_hICbJrT"
    },
    "2016": {
        "paper1": "1NdrZBtFP1HyZygHnJ8-ZS90qbPcMIlav",
        "paper2": "154pUyo0HU9l6cUleU2QHBiPBRivfkKhH"
    },
    "2017": {
        "paper1": "1mjI_RKTkSdWABnkKLuLJ5Z-mderXzqv7",
        "paper2": "1DbptLDbIGoH7e8v5GwSz6mmWkPptW39Z"
    },
    "2018": {
        "paper1": "1ZR6SQC_xp-hjroLhGTEKi7xxQbkEN0MT",
        "paper2": "1305CeuprFHV3TD-yhLuXoDANXp1nZLWY"
    },
    "2019": {
        "paper1": "1VlaF1S-8n1n_dhthol1RGqPO_QGbA72_",
        "paper2": "14mQDX-Bv6qmqaBYRLuFf1kIRSOpT49z-"
    },
    "2020": {
        "paper1": "17Oq8r0fqC08tkZ-IFztjoPDRIY87bNzn",
        "paper2": "1ZrULjDmvrMTyX4JMm0zIq4_D8lsdEI6s"
    },
}


# Function to generate Google Drive download link
def generate_drive_link(file_id: str) -> str:
    return f"https://drive.google.com/uc?id={file_id}&export=download"


# Function to capture file_id
async def get_file_id(update: Update,
                      context: ContextTypes.DEFAULT_TYPE) -> None:
    file = update.message.document
    await update.message.reply_text(
        f"File Name: {file.file_name}\nFile ID: {file.file_id}")


# KEAM Papers handler
async def keam_handler(update: Update,
                       context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Display year selection buttons
    keyboard = [
        [
            InlineKeyboardButton(year, callback_data=f"keam_{year}")
            for year in keam_papers.keys()
        ],
        [InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Select a year:", reply_markup=reply_markup)


# Year and paper selection handler
async def year_handler(update: Update,
                       context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    year = query.data.split("_")[1]  # Extract the year (e.g., '2014')
    papers = keam_papers.get(year, {})

    # Create buttons for paper selection
    keyboard = [
        [
            InlineKeyboardButton("Paper 1",
                                 url=generate_drive_link(papers["paper1"]))
        ],
        [
            InlineKeyboardButton("Paper 2",
                                 url=generate_drive_link(papers["paper2"]))
        ],
        [InlineKeyboardButton("Back to Years", callback_data="keam_papers")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"Select a file for {year}:",
                                  reply_markup=reply_markup)


# Main menu handler
async def main_menu(update: Update,
                    context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await start(update, context)


if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('about', about_command))
    app.add_handler(MessageHandler(filters.Document.ALL,
                                   get_file_id))  # For capturing file_id
    app.add_handler(CallbackQueryHandler(keam_handler,
                                         pattern="^keam_papers$"))
    app.add_handler(CallbackQueryHandler(year_handler, pattern="^keam_\\d+$"))
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    # Errors

app.add_error_handler(error)
print('Polling...')
app.run_polling(poll_interval=3)




"""
predefined_answers = {
  "thermodynamics": [
      "what is thermodynamics",
      "explain thermodynamics",
      "define thermodynamics",
      "what does thermodynamics mean"
  ]
}

answer = "Thermodynamics is the branch of physics concerned with heat and temperature and their relation to energy and work."

def get_answer(question):
  question = question.lower()
  for key, questions in predefined_answers.items():
      if question in questions:
          return answer
  return "Sorry, I don't know the answer to that."

# Example usage
user_question = input("Ask a question: ")
print(get_answer(user_question))
"""

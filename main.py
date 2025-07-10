import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv
from PyPDF2 import PdfReader, PdfWriter, PdfMerger

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Define states for the conversation
ASKING_UNLOCK_PASSWORD = 1
ASKING_PASSWORD = 2

# Dictionary to store user-uploaded files and their context
user_files = {}
password_attempts = {}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name  
    await update.message.reply_text(
        f"Hello! <b>{user_name}</b> Welcome to PDF Master Bot. I can assist you with various PDF operations, including merging, splitting, locking, unlocking, and compressing PDFs. Type /help to see what I can do.",
        parse_mode="HTML"
    )

# Help command
async def helps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '''
        Hi there! I'm PDF Master Bot, created by Sankalp Kumar (@sankalpkumar111). Here are the commands you can use:

        /start - Start interacting with the bot
        /content - Get tips on effectively managing and working with PDFs
       
        /merge - Send me multiple PDF files, and I will merge them into one
        /split - Split a PDF file into separate documents based on the pages you choose
        /lock - Lock a PDF with a password
        /unlock - Unlock a PDF by providing the password
        /compress - Compress a PDF to reduce its size
        /help - Show this help menu

        Need help with PDF operations? Just send me a PDF and I’ll guide you through the process!
        '''
    )

# Content command
async def content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '''
        PDF Management Tips:

        1. Organize: Keep your PDFs organized in folders based on categories.
        2. Security: Use password protection for sensitive PDF files.
        3. Optimization: Compress PDFs to reduce file size without compromising quality.
        4. Conversion: Convert PDFs to other formats (e.g., Word, Excel) for easier editing.
        5. Backup: Regularly back up your PDFs to avoid data loss.

        Use the bot to easily manage and manipulate your PDF files!
        '''
    )



# Handle PDF uploads
async def handle_pdf_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_files:
        user_files[user_id] = []

    file = await update.message.document.get_file()
    file_path = f"{user_id}_{file.file_id}.pdf"
    await file.download_to_drive(file_path)
    user_files[user_id].append(file_path)

    await update.message.reply_text(
        "PDF received! Send more or use /merge, /split, /lock, /unlock, or /compress."
    )

# Merge PDFs
async def merge_pdfs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_files or len(user_files[user_id]) < 2:
        await update.message.reply_text("Please upload at least two PDFs before merging.")
    else:
        merger = PdfMerger()
        for pdf in user_files[user_id]:
            merger.append(pdf)

        merged_pdf_path = f"{user_id}_merged.pdf"
        with open(merged_pdf_path, "wb") as merged_pdf:
            merger.write(merged_pdf)

        await update.message.reply_document(document=open(merged_pdf_path, "rb"), filename="merged.pdf")
        merger.close()

        for pdf in user_files[user_id]:
            os.remove(pdf)
        os.remove(merged_pdf_path)
        user_files[user_id] = []

# Lock a PDF
async def lock_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_files or len(user_files[user_id]) != 1:
        await update.message.reply_text("Please upload a single PDF to lock and use /lock again.")
        return ConversationHandler.END
    await update.message.reply_text("Enter the password to lock this PDF:")
    return ASKING_PASSWORD

async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_files and len(user_files[user_id]) == 1:
        password = update.message.text
        pdf_reader = PdfReader(user_files[user_id][0])
        pdf_writer = PdfWriter()

        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

        pdf_writer.encrypt(user_pwd=password)
        locked_pdf_path = f"{user_id}_locked.pdf"
        with open(locked_pdf_path, "wb") as locked_pdf:
            pdf_writer.write(locked_pdf)

        await update.message.reply_document(document=open(locked_pdf_path, "rb"), filename="locked.pdf")
        os.remove(user_files[user_id][0])
        os.remove(locked_pdf_path)
        user_files[user_id] = []

    return ConversationHandler.END

# Unlock a PDF
async def unlock_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_files or len(user_files[user_id]) != 1:
        await update.message.reply_text("Upload a single PDF to unlock and use /unlock again.")
        return ConversationHandler.END
    await update.message.reply_text("Enter the password to unlock this PDF:")
    password_attempts[user_id] = 0
    return ASKING_UNLOCK_PASSWORD

async def handle_unlock_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    password = update.message.text
    try:
        pdf_reader = PdfReader(user_files[user_id][0])
        pdf_reader.decrypt(password)

        pdf_writer = PdfWriter()
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

        unlocked_pdf_path = f"{user_id}_unlocked.pdf"
        with open(unlocked_pdf_path, "wb") as unlocked_pdf:
            pdf_writer.write(unlocked_pdf)

        await update.message.reply_document(document=open(unlocked_pdf_path, "rb"), filename="unlocked.pdf")
        os.remove(user_files[user_id][0])
        os.remove(unlocked_pdf_path)
        user_files[user_id] = []
        del password_attempts[user_id]

    except Exception:
        password_attempts[user_id] += 1
        if password_attempts[user_id] < 2:
            await update.message.reply_text("Incorrect password. Try again.")
            return ASKING_UNLOCK_PASSWORD
        else:
            await update.message.reply_text("Too many failed attempts. Operation aborted.")
            del password_attempts[user_id]

    return ConversationHandler.END

# Compress a PDF
async def compress_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_files or len(user_files[user_id]) != 1:
        await update.message.reply_text("Upload a single PDF to compress and use /compress again.")
        return
    input_pdf_path = user_files[user_id][0]
    output_pdf_path = f"{user_id}_compressed.pdf"

    pdf_reader = PdfReader(input_pdf_path)
    pdf_writer = PdfWriter()

    for page in pdf_reader.pages:
        pdf_writer.add_page(page)

    with open(output_pdf_path, "wb") as compressed_pdf:
        pdf_writer.write(compressed_pdf)

    await update.message.reply_document(document=open(output_pdf_path, "rb"), filename="compressed.pdf")
    os.remove(input_pdf_path)
    os.remove(output_pdf_path)
    user_files[user_id] = []

# Create the bot application
application = Application.builder().token(TOKEN).build()

# Register handlers
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('help', helps))
application.add_handler(CommandHandler('content', content))
application.add_handler(MessageHandler(filters.Document.PDF, handle_pdf_upload))
application.add_handler(CommandHandler('merge', merge_pdfs))
application.add_handler(CommandHandler('compress', compress_pdf))

# Conversation handlers
application.add_handler(ConversationHandler(
    entry_points=[CommandHandler('lock', lock_pdf)],
    states={ASKING_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password)]},
    fallbacks=[]
))
application.add_handler(ConversationHandler(
    entry_points=[CommandHandler('unlock', unlock_pdf)],
    states={ASKING_UNLOCK_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unlock_password)]},
    fallbacks=[]
))

# Start polling
application.run_polling()

import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv
from PyPDF2 import PdfReader, PdfWriter, PdfMerger

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Define conversation states
ASKING_UNLOCK_PASSWORD = 1
ASKING_PASSWORD = 2

# Dictionaries to track users and file states
user_files = {}
password_attempts = {}
user_hit_count = {}

# Track user activity
def log_user_hit(user):
    user_id = user.id
    username = user.username or user.first_name
    user_hit_count[user_id] = user_hit_count.get(user_id, 0) + 1
    print(f"User {username} (ID: {user_id}) hit count: {user_hit_count[user_id]}")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_hit(update.effective_user)
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Hello! <b>{user_name}</b> Welcome to PDF Genie Bot. I can assist you with various PDF operations like merging, splitting, locking, unlocking, and compressing PDFs.\n\nType /help to see what I can do.",
        parse_mode="HTML"
    )

# Help command
async def helps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_hit(update.effective_user)
    await update.message.reply_text(
        '''
Hi there! I'm PDF Genie Bot, created by Sankalp Kumar (@sankalpkumar111). Here are the commands you can use:

/start - Start interacting with the bot  
/content - Get tips on managing your PDFs  
/merge - Merge multiple PDFs  
/split - (Coming soon!)  
/lock - Lock a PDF with a password  
/unlock - Unlock a password-protected PDF  
/compress - Compress a PDF  
/stats - Show your usage count  
/help - Show this help menu
        '''
    )

# Content command
async def content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_hit(update.effective_user)
    await update.message.reply_text(
        '''
PDF Management Tips:

1. Organize: Keep your PDFs in folders by category.  
2. Security: Use passwords to protect sensitive files.  
3. Optimize: Compress large PDFs without losing quality.  
4. Convert: Change PDF to Word/Excel when needed.  
5. Backup: Store copies in cloud or external storage.
        '''
    )

# Stats command
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_hit(update.effective_user)
    user_id = update.effective_user.id
    count = user_hit_count.get(user_id, 0)
    await update.message.reply_text(f"You’ve used PDF Genie {count} times!")

# Handle PDF uploads
async def handle_pdf_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_hit(update.effective_user)
    user_id = update.effective_user.id
    if user_id not in user_files:
        user_files[user_id] = []

    file = await update.message.document.get_file()
    file_path = f"{user_id}_{file.file_id}.pdf"
    await file.download_to_drive(file_path)
    user_files[user_id].append(file_path)

    await update.message.reply_text(
        "PDF received! You can now use /merge, /split, /lock, /unlock, or /compress."
    )

# Merge PDFs
async def merge_pdfs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_hit(update.effective_user)
    user_id = update.effective_user.id
    if user_id not in user_files or len(user_files[user_id]) < 2:
        await update.message.reply_text("Please upload at least two PDFs to merge.")
        return

    merger = PdfMerger()
    for pdf in user_files[user_id]:
        merger.append(pdf)

    merged_path = f"{user_id}_merged.pdf"
    with open(merged_path, "wb") as merged_pdf:
        merger.write(merged_pdf)

    await update.message.reply_document(document=open(merged_path, "rb"), filename="merged.pdf")
    merger.close()

    for pdf in user_files[user_id]:
        os.remove(pdf)
    os.remove(merged_path)
    user_files[user_id] = []

# Lock PDF
async def lock_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_hit(update.effective_user)
    user_id = update.effective_user.id
    if user_id not in user_files or len(user_files[user_id]) != 1:
        await update.message.reply_text("Upload a single PDF to lock, then use /lock again.")
        return ConversationHandler.END
    await update.message.reply_text("Enter the password to lock this PDF:")
    return ASKING_PASSWORD

async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_hit(update.effective_user)
    user_id = update.effective_user.id
    password = update.message.text

    pdf_reader = PdfReader(user_files[user_id][0])
    pdf_writer = PdfWriter()

    for page in pdf_reader.pages:
        pdf_writer.add_page(page)

    pdf_writer.encrypt(user_pwd=password)
    locked_path = f"{user_id}_locked.pdf"
    with open(locked_path, "wb") as locked_file:
        pdf_writer.write(locked_file)

    await update.message.reply_document(document=open(locked_path, "rb"), filename="locked.pdf")
    os.remove(user_files[user_id][0])
    os.remove(locked_path)
    user_files[user_id] = []

    return ConversationHandler.END

# Unlock PDF
async def unlock_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_hit(update.effective_user)
    user_id = update.effective_user.id
    if user_id not in user_files or len(user_files[user_id]) != 1:
        await update.message.reply_text("Upload a single locked PDF and then use /unlock.")
        return ConversationHandler.END
    await update.message.reply_text("Enter the password to unlock the PDF:")
    password_attempts[user_id] = 0
    return ASKING_UNLOCK_PASSWORD

async def handle_unlock_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_hit(update.effective_user)
    user_id = update.effective_user.id
    password = update.message.text
    try:
        pdf_reader = PdfReader(user_files[user_id][0])
        if not pdf_reader.decrypt(password):
            raise ValueError("Wrong password")

        pdf_writer = PdfWriter()
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

        unlocked_path = f"{user_id}_unlocked.pdf"
        with open(unlocked_path, "wb") as unlocked_pdf:
            pdf_writer.write(unlocked_pdf)

        await update.message.reply_document(document=open(unlocked_path, "rb"), filename="unlocked.pdf")
        os.remove(user_files[user_id][0])
        os.remove(unlocked_path)
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

# Compress PDF
async def compress_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_hit(update.effective_user)
    user_id = update.effective_user.id
    if user_id not in user_files or len(user_files[user_id]) != 1:
        await update.message.reply_text("Upload a single PDF to compress, then use /compress.")
        return

    input_path = user_files[user_id][0]
    output_path = f"{user_id}_compressed.pdf"

    pdf_reader = PdfReader(input_path)
    pdf_writer = PdfWriter()
    for page in pdf_reader.pages:
        pdf_writer.add_page(page)

    with open(output_path, "wb") as compressed_pdf:
        pdf_writer.write(compressed_pdf)

    await update.message.reply_document(document=open(output_path, "rb"), filename="compressed.pdf")
    os.remove(input_path)
    os.remove(output_path)
    user_files[user_id] = []

# Application setup
application = Application.builder().token(TOKEN).build()

# Register all command handlers
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('help', helps))
application.add_handler(CommandHandler('content', content))
application.add_handler(CommandHandler('stats', stats))
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

# Start the bot
application.run_polling()

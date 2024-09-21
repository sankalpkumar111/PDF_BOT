import telegram.ext
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv
import os
from PyPDF2 import PdfReader, PdfWriter

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Define states for the conversation
ASKING_UNLOCK_PASSWORD = 1

# Dictionary to store user-uploaded files and their context
user_files = {}
# Dictionary to store the number of password attempts
password_attempts = {}

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
        /contact - Get in touch with us
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
        **PDF Management Tips:**

        1. **Organize:** Keep your PDFs organized in folders based on categories.
        2. **Security:** Use password protection for sensitive PDF files.
        3. **Optimization:** Compress PDFs to reduce file size without compromising quality.
        4. **Conversion:** Convert PDFs to other formats (e.g., Word, Excel) for easier editing.
        5. **Backup:** Regularly back up your PDFs to avoid data loss.

        Use the bot to easily manage and manipulate your PDF files!
        '''
    )

# Contact command
async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '''
        **Contact Us:**

        * **Phone:** +91 987 654 3210
        * **Email:** support@pdfmaster.com
        * **Address:** PDF Master Solutions, New Delhi, India

        **Follow Us:**
        * **Twitter:** @PDFMaster
        * **LinkedIn:** PDF Master Solutions

        **Support Hours:** Mon-Fri 9:00 AM - 6:00 PM IST
        '''
    )

# Handle PDF uploads
async def handle_pdf_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_files:
        user_files[user_id] = []

    file = await update.message.document.get_file()
    file_path = f"{user_id}_{file.file_id}.pdf"
    
    # Download the file to the specified path
    await file.download_to_drive(file_path)
    
    user_files[user_id].append(file_path)

    await update.message.reply_text("PDF received! Send more or type /merge to merge the PDFs, /split to split the PDF, /lock to lock the PDF with a password, /unlock to unlock the PDF, or /compress to compress the PDF.")

# Start the unlocking process and ask for the password
async def unlock_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_files or len(user_files[user_id]) != 1:
        await update.message.reply_text(
            "Please send a single PDF file that you would like to unlock. When you are done, use the /unlock command again."
        )
        return ConversationHandler.END
    else:
        password_attempts[user_id] = 0  # Initialize the attempt counter
        await update.message.reply_text("Please enter the password used to lock this PDF.")
        return ASKING_UNLOCK_PASSWORD

# Handle password input and unlock the PDF
async def handle_unlock_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_files and len(user_files[user_id]) == 1:
        password = update.message.text

        # Read the PDF and attempt to unlock it
        try:
            pdf_reader = PdfReader(user_files[user_id][0])
            pdf_reader.decrypt(password)
            
            pdf_writer = PdfWriter()
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

            unlocked_pdf_path = f"{user_id}_unlocked.pdf"
            with open(unlocked_pdf_path, "wb") as unlocked_pdf:
                pdf_writer.write(unlocked_pdf)

            # Send the unlocked PDF to the user
            await update.message.reply_document(document=open(unlocked_pdf_path, "rb"), filename="unlocked.pdf")

            # Clean up
            os.remove(user_files[user_id][0])
            os.remove(unlocked_pdf_path)
            user_files[user_id] = []
            del password_attempts[user_id]  # Remove the attempt counter

            return ConversationHandler.END

        except Exception as e:
            # Increment the attempt counter
            password_attempts[user_id] += 1
            if password_attempts[user_id] < 2:
                await update.message.reply_text(
                    "The password you entered is incorrect. Please try again."
                )
                return ASKING_UNLOCK_PASSWORD
            else:
                await update.message.reply_text(
                    "The password you entered is incorrect. You've reached the maximum number of attempts."
                )
                del password_attempts[user_id]  # Remove the attempt counter
                return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Please upload a PDF file first and then use the /unlock command."
        )
        return ConversationHandler.END

# Compress PDF function
async def compress_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_files or len(user_files[user_id]) != 1:
        await update.message.reply_text(
            "Please send a single PDF file that you would like to compress. When you are done, use the /compress command again."
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text("Compressing your PDF, please wait...")

        try:
            input_pdf_path = user_files[user_id][0]
            output_pdf_path = f"{user_id}_compressed.pdf"

            pdf_reader = PdfReader(input_pdf_path)
            pdf_writer = PdfWriter()

            # Copy all pages from the reader to the writer
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

            # Reduce the quality of the images (if any) in the PDF
            with open(output_pdf_path, "wb") as output_pdf:
                pdf_writer.write(output_pdf)

            # Send the compressed PDF back to the user
            await update.message.reply_document(document=open(output_pdf_path, "rb"), filename="compressed.pdf")

            # Clean up
            os.remove(input_pdf_path)
            os.remove(output_pdf_path)
            user_files[user_id] = []

        except Exception as e:
            await update.message.reply_text("An error occurred while compressing the PDF.")
        
        return ConversationHandler.END

# Create the bot application
application = Application.builder().token(TOKEN).build()

# Register handlers
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('help', helps))
application.add_handler(CommandHandler('content', content))
application.add_handler(CommandHandler('contact', contact))
application.add_handler(MessageHandler(filters.Document.PDF, handle_pdf_upload))

# Conversation handler for unlocking PDFs
unlock_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('unlock', unlock_pdf)],
    states={
        ASKING_UNLOCK_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unlock_password)],
    },
    fallbacks=[],
)

application.add_handler(unlock_conv_handler)

# Register compress command handler
application.add_handler(CommandHandler('compress', compress_pdf))

# Start polling
application.run_polling()

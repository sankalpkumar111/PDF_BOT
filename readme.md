# PDF Genie

PDF Genie is a Telegram bot designed in assisting users with a variety of PDF operations, including merging, splitting, locking, unlocking, and compressing PDF files. This bot is built using Python and the `python-telegram-bot` library.

## Features

- Merge PDFs: Combine multiple PDF files into a single document.
- Split PDFs: Separate a PDF file into individual documents based on specified pages.
- Lock PDFs: Secure your PDF with a password.
- Unlock PDFs: Remove password protection from a PDF by providing the correct password.
- Compress PDFs: Decrease the file size of a PDF.
- PDF Content Management Tips: Receive helpful tips for effective PDF management.
- Contact Information: Get in touch for support or inquiries.

## Commands

- `/start`: Begin interacting with the bot.
- `/help`: Display a list of available commands.
- `/content`: Obtain tips for managing and working with PDFs.
- `/contact`: View contact information for support.
- `/merge`: Upload multiple PDF files to merge them into one.
- `/split`: Provide a PDF file to split into multiple documents based on page selection.
- `/lock`: Lock a PDF with a password for security.
- `/unlock`: Unlock a password-protected PDF.
- `/compress`: Compress a PDF to reduce its size.

## Setup Instructions

To set up and run the bot locally, please follow the instructions below:

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/pdf-master-bot.git
```

### 2. Install Dependencies

Ensure you have Python installed, then install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory of the project and add the following content:

```bash
TOKEN=your-telegram-bot-token
ADMIN_ID=your-telegram-user-id
```

- Replace `your-telegram-bot-token` with the API token provided by [BotFather](https://t.me/botfather).
- Replace `your-telegram-user-id` with your Telegram user ID for administrative purposes.

### 4. Run the Bot

Start the bot by executing:

```bash
python main.py
```

### 5. Deploying on PythonAnywhere (Optional)

For deployment in the cloud, follow the instructions on [PythonAnywhere](https://www.pythonanywhere.com/).

## Technologies Used

- Python: The programming language used to develop the bot.
- python-telegram-bot: A library for interacting with the Telegram Bot API.
- PyPDF2: A library for manipulating PDF files (merging, splitting, locking, unlocking, and compressing).
- python-dotenv: A package for managing environment variables securely.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Implement your changes.
4. Submit a pull request for review.

## License

This project is licensed under the MIT License.

## Contact

For any inquiries, suggestions, or support, please reach out via:

- Email: sankalpkumar911@gmail.com
- Telegram Bot: [PDF Genie](https://t.me/PDFGeniebot) (@PDFGeniebot)
- LinkedIn: [Sankalp Kumar](https://www.linkedin.com/in/sankalpkumar111)


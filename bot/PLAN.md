# Development Plan

I will build this bot in several small and testable steps. First, I will create a clean project structure inside the bot directory. It will include an entry point file, a handlers package, and a dependency file. The main goal of this stage is to separate command-processing logic from the Telegram transport layer. This makes the code easier to test and maintain. It also allows me to run commands locally in CLI mode with uv run bot.py --test "/command" without requiring a live Telegram bot connection.

Second, I will implement the required commands such as /start, /help, /health, /labs, and /scores <lab>. At the beginning, some commands may return placeholder text, but they must never crash. Third, I will connect the handlers to the LMS backend API and format readable responses for users. After that, I will add natural language routing through the LLM API. Finally, I will containerize the bot, deploy it on the VM, test it in Telegram, and improve logging and error handling.

## Backend integration note
The bot reads labs and scores from the deployed LMS backend API.

## Intent routing note
The bot can route natural-language requests to backend-powered tools and summaries.

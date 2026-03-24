def handle_command(text: str) -> str:
    text = (text or "").strip()

    if text == "/start":
        return "Welcome to LMS Bot! Use /help to see available commands."

    if text == "/help":
        return "Available commands: /start, /help, /health, /labs, /scores <lab>"

    if text == "/health":
        return "Health check is not implemented yet."

    if text == "/labs":
        return "Labs list is not implemented yet."

    if text.startswith("/scores"):
        return "Scores command is not implemented yet."

    return "Unknown command. Use /help."

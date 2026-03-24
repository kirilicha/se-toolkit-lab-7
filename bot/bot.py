import argparse
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from config import Settings
from handlers import handle_command
from llm_router import route_natural_language


settings = Settings()


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Labs", callback_data="labs"),
                InlineKeyboardButton(text="Health", callback_data="health"),
            ],
            [
                InlineKeyboardButton(text="Scores Lab 4", callback_data="scores_lab_04"),
                InlineKeyboardButton(text="Scores Lab 1", callback_data="scores_lab_01"),
            ],
        ]
    )


async def run_test_mode(text: str) -> None:
    if text.startswith("/"):
        result = await handle_command(text)
    else:
        result = await route_natural_language(text)
    print(result)


async def telegram_main() -> None:
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start_handler(message: Message) -> None:
        text = (
            "Welcome to LMS Bot!\n"
            "Use buttons below or type a question in natural language."
        )
        await message.answer(text, reply_markup=main_menu_keyboard())

    @dp.message(Command("help"))
    async def help_handler(message: Message) -> None:
        await message.answer(await handle_command("/help"), reply_markup=main_menu_keyboard())

    @dp.message(Command("health"))
    async def health_handler(message: Message) -> None:
        await message.answer(await handle_command("/health"), reply_markup=main_menu_keyboard())

    @dp.message(Command("labs"))
    async def labs_handler(message: Message) -> None:
        await message.answer(await handle_command("/labs"), reply_markup=main_menu_keyboard())

    @dp.message(Command("scores"))
    async def scores_handler(message: Message) -> None:
        await message.answer(await handle_command(message.text or "/scores"), reply_markup=main_menu_keyboard())

    @dp.callback_query(F.data == "labs")
    async def callback_labs(callback: CallbackQuery) -> None:
        await callback.message.answer(await handle_command("/labs"), reply_markup=main_menu_keyboard())
        await callback.answer()

    @dp.callback_query(F.data == "health")
    async def callback_health(callback: CallbackQuery) -> None:
        await callback.message.answer(await handle_command("/health"), reply_markup=main_menu_keyboard())
        await callback.answer()

    @dp.callback_query(F.data == "scores_lab_04")
    async def callback_scores_04(callback: CallbackQuery) -> None:
        await callback.message.answer(await handle_command("/scores lab-04"), reply_markup=main_menu_keyboard())
        await callback.answer()

    @dp.callback_query(F.data == "scores_lab_01")
    async def callback_scores_01(callback: CallbackQuery) -> None:
        await callback.message.answer(await handle_command("/scores lab-01"), reply_markup=main_menu_keyboard())
        await callback.answer()

    @dp.message()
    async def natural_language_handler(message: Message) -> None:
        try:
            answer = await route_natural_language(message.text or "")
        except Exception as e:
            answer = f"LLM error: {e}"
        await message.answer(answer, reply_markup=main_menu_keyboard())

    await dp.start_polling(bot)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, default=None)
    args = parser.parse_args()

    if args.test is not None:
        asyncio.run(run_test_mode(args.test))
        return 0

    asyncio.run(telegram_main())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

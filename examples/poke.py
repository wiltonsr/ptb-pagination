import json
import logging
import math
import os

from urllib.request import urlopen, Request

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler, Application
)
from ptb_pagination import InlineKeyboardPaginator

POKE_API_URL = 'https://pokeapi.co/api/v2/pokemon?offset={offset}&limit={limit}'
MAX_PAGE_SIZE = 10
MAX_POKES = 151

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    paginator = InlineKeyboardPaginator(
        math.ceil(MAX_POKES / MAX_PAGE_SIZE),
        data_pattern='page#{page}'
    )

    msg = poke_html_msg(read_pokes())

    await update.message.reply_text(
        text=msg,
        reply_markup=paginator.markup,
        parse_mode=ParseMode.HTML
    )


async def page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    await query.answer()

    page = int(query.data.split('#')[1])

    paginator = InlineKeyboardPaginator(
        math.ceil(MAX_POKES / MAX_PAGE_SIZE),
        current_page=page,
        data_pattern='page#{page}'
    )

    msg = poke_html_msg(
        read_pokes(
            offset=(page - 1) * MAX_PAGE_SIZE,
            limit=MAX_PAGE_SIZE
        )
    )

    await query.edit_message_text(
        text=msg,
        reply_markup=paginator.markup,
        parse_mode=ParseMode.HTML
    )


def read_pokes(offset: int = 0, limit: int = MAX_PAGE_SIZE) -> list:
    req = Request(
        url=POKE_API_URL.format(offset=offset, limit=limit),
        headers={'User-Agent': 'Mozilla/5.0'}
    )

    response = urlopen(req)
    data_json = json.loads(response.read())

    return data_json['results']


def poke_html_msg(poke_list: list) -> str:
    msg = ''
    for poke in poke_list:
        name = poke['name']
        msg = msg + f'<b>Name:</b> {name.capitalize()}\n'

    return msg


application = (
    Application.builder()
    .token(os.getenv('BOT_TOKEN'))
    .build()
)

application.add_handler(CommandHandler('start', start))
application.add_handler(CallbackQueryHandler(
    page_callback, pattern='^page#'))

application.run_polling()

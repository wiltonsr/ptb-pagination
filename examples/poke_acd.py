import json
import logging
import math
import os

from urllib.request import urlopen, Request

from telegram import Update, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler, Application
)
from ptb_pagination import InlineKeyboardPaginator

from pokemon import Pokemon

POKE_API_URL = 'https://pokeapi.co/api/v2/pokemon?offset={offset}&limit={limit}'
MAX_PAGE_SIZE = 10
MAX_POKES = 151
COLUMNS_NUMBER = 2

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

    ilkb_list = poke_ilkb_list(read_pokes())

    paginator.add_before(ilkb_list)

    await update.message.reply_text(
        text="Who's That Pokémon?",
        reply_markup=paginator.markup,
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

    ilkb_list = poke_ilkb_list(
        read_pokes(
            offset=(page - 1) * MAX_PAGE_SIZE,
            limit=MAX_PAGE_SIZE
        )
    )

    paginator.add_before(ilkb_list)

    await query.edit_message_text(
        text="Who's That Pokémon?",
        reply_markup=paginator.markup,
    )


async def poke_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    await query.answer()

    poke = query.data

    await query.edit_message_text(
        text=(poke.poke_html_msg()),
        parse_mode=ParseMode.HTML,
    )


def read_pokes(offset: int = 0, limit: int = MAX_PAGE_SIZE) -> list:
    if offset + MAX_PAGE_SIZE > MAX_POKES:
        limit = MAX_POKES - offset

    req = Request(
        url=POKE_API_URL.format(offset=offset, limit=limit),
        headers={'User-Agent': 'Mozilla/5.0'}
    )

    response = urlopen(req)
    data_json = json.loads(response.read())

    return data_json['results']


# InlineKeyboardButton List of Pokemons
def poke_ilkb_list(poke_list: list) -> list:
    ilkb = []
    for poke_sub_list in chunks(poke_list, COLUMNS_NUMBER):
        sub_ilkb = []
        for poke in poke_sub_list:
            p = Pokemon(poke['name'], poke['url'])
            sub_ilkb.append(
                InlineKeyboardButton(
                    p.name.capitalize(), callback_data=p
                )
            )
        ilkb.append(sub_ilkb)

    return ilkb


def chunks(lst, n):
    """
    Yield successive n-sized chunks from lst.
    https://stackoverflow.com/a/312464
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


application = (
    Application.builder()
    .token(os.getenv('BOT_TOKEN'))
    .arbitrary_callback_data(True)
    .build()
)

application.add_handler(CommandHandler('start', start))
application.add_handler(CallbackQueryHandler(
    page_callback, pattern='^page#'))
application.add_handler(CallbackQueryHandler(
    poke_callback, pattern=Pokemon))

application.run_polling()

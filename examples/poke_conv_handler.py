import json
import logging
import math
import os

from urllib.request import urlopen, Request

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes, CommandHandler, Application,
    ConversationHandler, CallbackQueryHandler
)
from ptb_pagination import InlineKeyboardPaginator

from pokemon import Pokemon

POKE_API_URL = 'https://pokeapi.co/api/v2/pokemon?offset={offset}&limit={limit}'
MAX_PAGE_SIZE = 12
MAX_POKES = 151
COLUMNS_NUMBER = 3

CHOOSING, BACK, END = range(3)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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

    return CHOOSING


async def page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query

    await query.answer()

    page = int(query.data.split('#')[1])
    callback_data = f'page#{page}'
    context.user_data['PAGE'] = callback_data

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

    return CHOOSING


async def poke_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query

    await query.answer()

    poke = query.data

    if context.user_data.get('PAGE'):
        callback_data = context.user_data.get('PAGE')
    else:
        callback_data = 'page#1'

    keyboard = [
        [
            InlineKeyboardButton("« Go Back", callback_data=callback_data),
            InlineKeyboardButton("Finish", callback_data=poke)
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=(poke.poke_html_msg()),
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

    return BACK


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query

    if query:
        await query.answer()

        poke = query.data

        await query.edit_message_text(
            text=(poke.poke_html_msg()),
            parse_mode=ParseMode.HTML,
        )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Okay, bye."
    )

    """Completely end conversation from within nested conversation."""
    return ConversationHandler.END


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


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSING: [
            CallbackQueryHandler(page_callback, pattern='^page#'),
            CallbackQueryHandler(poke_callback, pattern=Pokemon)
        ],
        BACK: [
            CallbackQueryHandler(page_callback, pattern='^page#'),
            CallbackQueryHandler(stop, pattern=Pokemon),
        ]
    },
    fallbacks=[CommandHandler("cancel", stop)],
)

application.add_handler(conv_handler)

application.run_polling()

# ptb-pagination

Python inline keyboard pagination for Telegram Bot API.

Provide an easy way to create number pagination with [Telegram Inline Keyboards](https://core.telegram.org/bots/2-0-intro#new-inline-keyboards) for [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot).

![Telegram Pagination Docs Example](https://core.telegram.org/file/811140217/1/NkRCCLeQZVc/17a804837802700ea4)

This project is very based on [python-telegram-bot-pagination](https://github.com/ksinn/python-telegram-bot-pagination), thanks [ksinn](https://github.com/ksinn/).

The main difference it's supposed to only work with the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) library and provide full support to [Arbitrary callback_data](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Arbitrary-callback_data).

## Installation

```bash
pip install ptb-pagination
```

## Usage

```python
from ptb_pagination import InlineKeyboardPaginator

paginator = InlineKeyboardPaginator(
    page_count,
    current_page=page,
    data_pattern='page#{page}'
)

bot.send_message(
    chat_id,
    text,
    reply_markup=paginator.markup,
)
```

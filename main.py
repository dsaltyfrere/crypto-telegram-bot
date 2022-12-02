#!/usr/bin/env python
import logging
import os

from telegram import __version__ as TG_VER
from telegram.ext import Application, CommandHandler
from telegram.ext.filters import Filters

from commands.start import start as start
from commands.fear import fear as fear
from commands.feeds.list_feeds import list_feeds as list
from commands.feeds.add_feed import add_feed as add
from commands.feeds.remove_feed import remove_feed as remove
from commands.feeds.edit_feed import edit_feed as edit, change_preview as preview
from commands.whalepool.symbol.add_whalepool_symbol import add_whalepool_symbol
from commands.whalepool.symbol.list_whalepool_symbol import list_whalepool_symbol
from commands.whalepool.symbol.remove_whalepool_symbol import remove_whalepool_symbol
from commands.whalepool.type.add_whalepool_transaction_type import add_whalepool_transaction_type
from commands.whalepool.type.list_whalepool_transaction_type import list_whalepool_transaction_type
from commands.whalepool.type.remove_whalepool_transaction_type import remove_whalepool_transaction_type
from commands.jobs.list_jobs import list_jobs
from commands.jobs.update_job import update_job

from models.base_model import db
from models.feeds.feed import Feed
from models.feeds.entry import FeedEntry

from models.whalepool.symbol import WhalepoolTransactionSymbol
from models.whalepool.transaction import WhalepoolTransaction
from models.whalepool.transaction_type import WhalepoolTransactionType
from models.whalepool.high_low import HighLow
from models.whalepool.olhc import Olhc
from models.whalepool.ticker import Ticker

from jobs.rss_monitor import rss_monitor
from jobs.whalepool import whalepool_alert
from jobs.olhc import olhc

from utils import error_handler

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

#Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger()

db.create_tables([
    Feed,
    FeedEntry,
    HighLow,
    Olhc,
    Ticker,
    WhalepoolTransactionType,
    WhalepoolTransaction,
    WhalepoolTransactionSymbol,
])

def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", None)
    if token is None:
        raise RuntimeError(
            f"No TELEGRAM_BOT_TOKEN specified"
        )

    application = Application.builder().token(token).build()
    filter = Filters.user(username=('@phyrxia'))

    #Add handlers
    application.add_handler(CommandHandler(["start", "help"], start, filters=filter))
    application.add_handler(CommandHandler(["fear", "f"], fear, filters=filter))
    #RSS
    application.add_handler(CommandHandler(["list_feeds", "lf"], list, filters=filter))
    application.add_handler(CommandHandler(["remove_feed", "rf"], remove, filters=filter))
    application.add_handler(CommandHandler(["edit_feed", "ef"], edit, filters=filter))
    application.add_handler(CommandHandler(["add_feed", "af"], add, filters=filter))
    application.add_handler(CommandHandler(["set_feed_preview", "sfp"], preview, filters=filter))

    # Whalepool
    application.add_handler(CommandHandler(["add_whalepool_symbol", "aws"], add_whalepool_symbol, filters=filter))
    application.add_handler(CommandHandler(["list_whalepool_symbol", "lws"], list_whalepool_symbol, filters=filter))
    application.add_handler(CommandHandler(["remove_whalepool_symbol", "rws"], remove_whalepool_symbol, filters=filter))
    application.add_handler(CommandHandler(["add_whalepool_transaction_type", "awtt"], add_whalepool_transaction_type, filters=filter))
    application.add_handler(CommandHandler(["list_whalepool_transaction_type", "lwtt"], list_whalepool_transaction_type, filters=filter))
    application.add_handler(CommandHandler(["remove_whalepool_transaction_type", "rwtt"], remove_whalepool_transaction_type, filters=filter))

    # Jobs
    application.add_handler(CommandHandler(["list_jobs", "lj"], list_jobs, filters=filter))
    application.add_handler(CommandHandler(["update_job", "uj"], update_job, filters=filter))

    # Error handler
    application.add_error_handler(error_handler)

    # Job queue
    job_queue = application.job_queue

    job_queue.run_repeating(rss_monitor, int(os.getenv("RSS_INTERVAL", 90)), name='rss-monitor')
    job_queue.run_repeating(whalepool_alert, int(os.getenv("WHALEPOOL_DELAY", 90)), name="whalepool-alert")
    job_queue.run_repeating(olhc, int(os.getenv("HILO_DELAY", 90)), name='olhc')

    application.run_polling()

if __name__ == "__main__":
    main()
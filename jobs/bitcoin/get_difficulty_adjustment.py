import requests
import logging
import os


from models.bitcoin.difficulty_adjustment import BitcoinDifficultyAdjustment
from telegram.constants import ParseMode
from datetime import datetime

logger = logging.getLogger(__name__)
BASE_URL = "https://mempool.space/api/v1"

async def get_difficulty_adjustment(context):
    logger.info(f"Fetching bitcoin difficulty adjustment")
    url = f"{BASE_URL}/difficulty-adjustment"
    try:
        response = requests.get(url)

        if response.status_code == 200:
            json_response = response.json()

            bda = BitcoinDifficultyAdjustment.create(
                progress_percent = json_response['progressPercent'],
                difficulty_change = json_response['difficultyChange'],
                estimated_retarget_date = json_response['estimatedRetargetDate'],
                remaining_blocks = json_response['remainingBlocks'],
                remaining_time = json_response['remainingTime'],
                previous_retarget = json_response['previousRetarget'],
                next_retarget_height = json_response['nextRetargetHeight'],
                time_average = json_response['timeAvg'],
                time_offset = json_response['timeOffset']
            )
            bda.save()
            response = f"<b>฿ mining difficulty progress:</b> {round(bda.progress_percent, 2)}%\n<b>฿ mining difficulty change:</b> {round(bda.difficulty_change)}%\n<b>Estimated retarget date:</b> {datetime.fromtimestamp(bda.estimated_retarget_date / 1000)}"
            await context.bot.send_message(
                chat_id = os.getenv("CHAT_ID", None),
                text = response,
                parse_mode = ParseMode.HTML
            )
        else:
            logger.error(f"Response.status_code for {url} was {response.status_code}")
    except Exception as exc:
        logger.error(exc, exc_info=True)
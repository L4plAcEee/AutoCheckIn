import logging
import os

# pip install serverchan-sdk
from serverchan_sdk import sc_send; 

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

try:
    import dotenv
    dotenv.load_dotenv()
except Exception:
    logger.debug("未安装或无法加载 python-dotenv，跳过 .env 加载")

key = os.environ.get('SCKEY', '')

title = "Github@L4place 的 AutoCheckInTools 提醒你"

def server_chan_push_normal(msg: str):
    if not key:
        logger.info('未配置ServerChan推送！')
        return
    logger.debug(sc_send(key, title , msg, {"tags": "Normal"}))

def server_chan_push_error(msg: str):
    if not key:
        logger.info('未配置ServerChan推送！')
        return
    logger.debug(sc_send(key, title , msg, {"tags": "Error"}))
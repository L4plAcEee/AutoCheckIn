import json, os, time, random, logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    logging.warning("未安装 python-dotenv，跳过加载 .env 文件")

# 搜索关键词
KEYWORDS = [
    "best programming languages 2025", "python vs javascript",
    "machine learning tutorials", "how ChatGPT works",
    "Bitcoin price prediction", "healthy breakfast ideas",
    "funny cat videos", "best travel destinations 2025",
    "zodiac sign personality", "cats vs dogs"
]
SEARCH_TIMES = 40
WAIT_TIME = (2, 5)

# 从 GitHub Secrets 读取 cookie
cookies = json.loads(os.environ["BING_COOKIES"])

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

try:
    # 先打开一次 Bing（必须先访问才能 add_cookie）
    driver.get("https://www.bing.com")
    time.sleep(1)

    # 注入 cookie
    for cookie in cookies:
        # 如果 sameSite 值不在允许列表，直接删除这个字段
        if "sameSite" in cookie and cookie["sameSite"] not in ["Strict", "Lax", "None"]:
            cookie.pop("sameSite")

        # Selenium 要求有 domain/path
        if "domain" not in cookie:
            cookie["domain"] = ".bing.com"
        if "path" not in cookie:
            cookie["path"] = "/"

        driver.add_cookie(cookie)


    driver.refresh()
    time.sleep(2)

    # 开始搜索
    for i in range(SEARCH_TIMES):
        kw = random.choice(KEYWORDS)
        logging.info(f"[{i+1}/{SEARCH_TIMES}] Searching: {kw}")
        try:
            box = driver.find_element(By.NAME, "q")
            box.clear()
            box.send_keys(kw)
            box.submit()
        except Exception as e:
            logging.warning(f"搜索失败：{e}")
            driver.get("https://www.bing.com")
        time.sleep(random.uniform(*WAIT_TIME))

finally:
    driver.quit()

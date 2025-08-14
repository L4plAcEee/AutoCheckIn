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
    # 技术 & 编程
    "best programming languages 2025", "python vs javascript", "machine learning tutorials",
    "what is cloud computing", "how to build a website", "C++ smart pointers", "Git vs SVN",
    "docker vs virtual machine", "REST vs GraphQL", "how does blockchain work", "WebAssembly tutorial",

    # ChatGPT & AI
    "how ChatGPT works", "latest OpenAI news", "future of artificial intelligence", "AI tools for productivity",
    "ChatGPT for coding", "DALL·E image generation", "prompt engineering tips",

    # 金融 & 投资
    "Tesla stock news", "Bitcoin price prediction", "how to invest in ETFs", "stock market news today",
    "is gold a good investment", "S&P 500 index meaning", "cryptocurrency tax rules",

    # 健康 & 生活方式
    "healthy breakfast ideas", "how to sleep better", "how to reduce stress", "is coffee healthy",
    "benefits of drinking water", "best home workouts", "intermittent fasting benefits",

    # 娱乐 & 热门文化
    "Game of Thrones recap", "best Netflix shows 2025", "funny cat videos", "Marvel vs DC",
    "upcoming movies 2025", "Oscars best picture winners", "top YouTubers 2025", "Twitch vs Kick",

    # 教育 & 学习
    "top universities in the world", "best online courses", "how to learn English fast",
    "study tips for exams", "what is the GRE test", "is SAT required in 2025",

    # 旅游 & 地理
    "best travel destinations 2025", "how to get cheap flights", "top 10 cities to live in",
    "weather in Tokyo", "hiking trails near me", "digital nomad lifestyle",

    # 社会热点 & 新闻
    "Ukraine conflict explained", "US presidential election", "global warming facts",
    "climate change solutions", "latest tech news", "AI replacing jobs", "privacy concerns with smartphones",

    # 商业 & 创业
    "how to start a business", "make money online", "passive income ideas", "top e-commerce platforms",
    "dropshipping vs Amazon FBA", "remote work trends", "freelancing vs full-time job",

    # 游戏 & 电竞
    "best PC games 2025", "Valorant tips and tricks", "how to get better at Fortnite",
    "Steam summer sale", "Nintendo Switch 2 rumors", "top esports teams",

    # 杂项 & 轻松话题
    "zodiac sign personality", "meaning of dreams", "fun trivia questions", "weird facts about space",
    "does pineapple belong on pizza", "best memes of 2025", "how to cook pasta",
    "coffee vs tea", "cats vs dogs", "funny dad jokes", "TikTok trends 2025"
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

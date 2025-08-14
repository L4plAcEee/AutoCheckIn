import json
import os
import shutil
import time
import random
import logging
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException

try:
    import dotenv
    dotenv.load_dotenv()
except Exception:
    logging.debug("未安装或无法加载 python-dotenv，跳过 .env 加载")

# 日志配置
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

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

def find_browser_binary():
    # 优先读取环境变量
    candidates = [
        os.environ.get("CHROME_BIN"),
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/google-chrome",
    ]
    for p in candidates:
        if p and os.path.exists(p):
            logging.info(f"找到浏览器二进制: {p}")
            return p
    # 再尝试 PATH 查找
    for name in ("chromium-browser", "chromium", "google-chrome-stable", "google-chrome"):
        p = shutil.which(name)
        if p:
            logging.info(f"在 PATH 中找到浏览器二进制: {p}")
            return p
    return None

def find_chromedriver():
    # 优先环境变量，再常见路径，再 PATH
    candidates = [
        os.environ.get("CHROMEDRIVER_PATH"),
        "/usr/bin/chromedriver",
        "/usr/local/bin/chromedriver",
    ]
    for p in candidates:
        if p and os.path.exists(p):
            logging.info(f"找到 chromedriver: {p}")
            return p
    p = shutil.which("chromedriver") or shutil.which("chromium-chromedriver")
    if p:
        logging.info(f"在 PATH 中找到 chromedriver: {p}")
        return p
    return None

def build_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1366,768")
    # 尝试找到浏览器二进制
    bin_path = find_browser_binary()
    if bin_path:
        options.binary_location = bin_path
    else:
        raise RuntimeError(
            "未找到浏览器二进制（Chrome/Chromium）。"
            " 在 CI 上请先安装 chromium 或 google-chrome，并设置 CHROME_BIN 指向二进制。"
        )

    chromedriver_path = find_chromedriver()
    service = Service(chromedriver_path) if chromedriver_path else None
    if not chromedriver_path:
        logging.warning("未找到 chromedriver，可让 Selenium 在 PATH 中查找或在 workflow 中安装 chromedriver。")

    try:
        if service:
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
        return driver
    except WebDriverException as e:
        logging.error("创建 webdriver 失败，请检查 chrome/chromedriver 是否安装且版本匹配。")
        raise

def load_cookies_from_env():
    """
    尝试多种格式解析 BING_COOKIES:
    1. 严格 JSON （首选）
    2. Python literal（使用单引号或 Python 列表形式）
    3. Netscape cookie 文件格式（关键字域值对，多行）
    4. 简单 name=value;name2=value2 字符串（作为最后手段，转换成单个 cookie）
    返回 list of dict（Selenium add_cookie 可接受的字典列表）
    """
    raw = os.environ.get("BING_COOKIES")
    if not raw:
        raise RuntimeError("环境变量 BING_COOKIES 未设置。请将 cookies.json 内容放到 Secrets/BING_COOKIES。")

    # 1) 尝试严格 JSON
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            # 如果是单个 dict，把它包成列表
            return [parsed]
        if isinstance(parsed, list):
            return parsed
        raise ValueError("解析后类型不是 list/dict")
    except Exception:
        pass

    # 2) 尝试 Python literal（比如使用单引号的列表）
    try:
        import ast
        parsed = ast.literal_eval(raw)
        if isinstance(parsed, dict):
            return [parsed]
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass

    # 3) 尝试解析 Netscape 格式或多行 "name<TAB>value" 等（宽松解析）
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    # 如果每行看起来像 "name<tab>value" 或 "domain\tpath\texpire\tname\tvalue"，尝试抽取 name/value
    parsed_list = []
    for ln in lines:
        # 常见 Netscape: 域、flag、path、expiry、name、value（以空白分隔）
        parts = ln.split()
        if len(parts) >= 6:
            name = parts[-2]
            value = parts[-1]
            parsed_list.append({"name": name, "value": value, "domain": ".bing.com", "path": "/"})
            continue
        # 如果是简单的 name=value
        if "=" in ln and ";" not in ln:
            k, v = ln.split("=", 1)
            parsed_list.append({"name": k.strip(), "value": v.strip(), "domain": ".bing.com", "path": "/"})
            continue
        # 如果是 header-like "Set-Cookie: name=value; Path=/; ..."，抽 name=value
        if "Set-Cookie:" in ln:
            try:
                seg = ln.split("Set-Cookie:", 1)[1].strip()
                kv = seg.split(";", 1)[0]
                k, v = kv.split("=", 1)
                parsed_list.append({"name": k.strip(), "value": v.strip(), "domain": ".bing.com", "path": "/"})
            except Exception:
                pass

    if parsed_list:
        return parsed_list

    # 4) 尝试 name=value; name2=value2 形式（单行多个 cookie）
    if ";" in raw and "=" in raw:
        items = [p.strip() for p in raw.split(";") if "=" in p]
        parsed_list = []
        for it in items:
            k, v = it.split("=", 1)
            parsed_list.append({"name": k.strip(), "value": v.strip(), "domain": ".bing.com", "path": "/"})
        if parsed_list:
            return parsed_list

    # 都失败：抛出友好错误并把前 200 字显示（便于调试本地）
    snippet = raw[:200].replace("\n", "\\n")
    raise RuntimeError(f"无法解析 BING_COOKIES（支持 JSON/ Python-literal / Netscape / name=value;...）。"
                       f" 前200字符: {snippet}")


def normalize_cookie(c):
    """
    兼容各种浏览器导出格式，返回 Selenium 可接受的 cookie dict。
    保留字段： name, value, domain, path, secure, httpOnly, expiry
    """
    cookie = dict(c)  # shallow copy
    # 允许不同大小写导出
    if "name" not in cookie and "Name" in cookie:
        cookie["name"] = cookie.pop("Name")
    if "value" not in cookie and "Value" in cookie:
        cookie["value"] = cookie.pop("Value")

    if "name" not in cookie or "value" not in cookie:
        raise ValueError("cookie 缺少 name 或 value 字段")

    # sameSite: 如果为 None 或 非法值，删除该字段
    if "sameSite" in cookie:
        v = cookie.get("sameSite")
        if v is None or (v not in ["Strict", "Lax", "None"]):
            cookie.pop("sameSite", None)

    # expiry 兼容
    if "expiry" not in cookie:
        # 常见字段名: expirationDate / expires
        for k in ("expirationDate", "expires"):
            if k in cookie:
                try:
                    cookie["expiry"] = int(float(cookie.pop(k)))
                except Exception:
                    cookie.pop(k, None)

    # domain / path fallback
    cookie.setdefault("domain", ".bing.com")
    cookie.setdefault("path", "/")

    # 删除不被 selenium 支持的额外字段
    allowed = {"name", "value", "path", "domain", "secure", "httpOnly", "expiry"}
    for k in list(cookie.keys()):
        if k not in allowed:
            cookie.pop(k, None)

    return cookie


def main():
    try:
        raw_cookies = load_cookies_from_env()
    except Exception as e:
        logging.error(e)
        return

    # 规范化 cookies
    normalized = []
    for c in raw_cookies:
        try:
            normalized.append(normalize_cookie(c))
        except Exception as e:
            logging.warning(f"忽略无法解析的 cookie: {e}")

    driver = None
    try:
        driver = build_driver()
        driver.get("https://www.bing.com")
        time.sleep(1)

        # 注入 cookie（先访问域以便 add_cookie 生效）
        for ck in normalized:
            try:
                driver.add_cookie(ck)
            except AssertionError as ae:
                # Selenium 对 sameSite/expiry 有严格断言，尝试删除并重试
                ck2 = dict(ck)
                ck2.pop("expiry", None)
                try:
                    driver.add_cookie(ck2)
                except Exception as e2:
                    logging.warning(f"添加 cookie 失败，跳过：{e2}")
            except Exception as e:
                logging.warning(f"添加 cookie 失败，跳过：{e}")

        driver.refresh()
        time.sleep(2)

        # 执行搜索任务
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
                try:
                    driver.get("https://www.bing.com")
                except Exception:
                    pass
            time.sleep(random.uniform(*WAIT_TIME))

        logging.info("任务完成。")

    except Exception as e:
        logging.error("运行出错：%s", e)
        traceback.print_exc()
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

if __name__ == "__main__":
    main()
import os, json, logging
import requests as r

from core.utility.server_chan import server_chan_push_normal

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

try:
    import dotenv
    dotenv.load_dotenv()
except Exception:
    logger.debug("未安装或无法加载 python-dotenv，跳过 .env 加载")

sign_url = 'https://n.cg.163.com/api/v2/sign-today'
current = 'https://n.cg.163.com/api/v2/client-settings/@current'


cookies = os.environ.get('WYYCG_COOKIES', '').split('#')
assert cookies, logger.info('[网易云游戏自动签到]未设置cookie，正在退出……')

class ScriptRunError(Exception):
    logger.info("[网易云游戏自动签到]脚本运行错误，具体请参见日志！")


def signin(url, cookie):
    header = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja-JP;q=0.6,ja;q=0.5',
        'Authorization': str(cookie),
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Host': 'n.cg.163.com',
        'Origin': 'https://cg.163.com',
        'Referer': 'https://cg.163.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'X-Platform': '0'
    }

    result = r.post(url=url, headers=header)
    return result


def getme(url, cookie):
    header = {
        'Host': 'n.cg.163.com',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'X-Platform': '0',
        'Authorization': str(cookie),
        'Origin': 'https://cg.163.com',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://cg.163.com/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja-JP;q=0.6,ja;q=0.5'
    }
    result = r.get(url=url, headers=header)
    return result


if __name__ == "__main__":
    logger.info('检测到{}个账号，即将开始签到！'.format(len(cookies)))
    success = []
    failure = []
    msg = []
    for i in cookies:
        cookie = i
        autherror = False
        signerror = False
        sign_return = None
        me = None
        try:
            me = getme(current, cookie)
        except:
            message = '第{}个账号验证失败！请检查Cookie是否过期！或者附上报错信息到 https://github.com/GamerNoTitle/wyycg-autosignin/issues 发起issue'.format(
                cookies.index(i) + 1)
            failure.append(cookie)
            msg.append(message)
            autherror = True

        if me is not None and me.status_code != 200 and not autherror:
            message = '第{}个账号验证失败！请检查Cookie是否过期！或者附上报错信息到 https://github.com/GamerNoTitle/wyycg-autosignin/issues 发起issue'.format(
                cookies.index(i) + 1)
            failure.append(cookie)
            msg.append(message)
        elif me is not None and me.status_code == 200:
            try:
                sign_return = signin(sign_url, cookie)
            except:
                if sign_return is not None:
                    message = '第{}个账号签到失败，回显状态码为{}，具体错误信息如下：{}'.format(cookies.index(i) + 1, sign_return.status_code, sign_return.text)
                else:
                    message = '第{}个账号签到失败，未获取到返回结果。'.format(cookies.index(i) + 1)
                failure.append(cookie)
                msg.append(message)
                signerror = True

            if sign_return is not None and sign_return.status_code == 200:
                message = '第{}个账号签到成功！'.format(cookies.index(i) + 1)
                success.append(cookie)
                msg.append(message)
            elif not signerror and sign_return is not None:
                message = '第{}个账号签到失败，回显状态码为{}，具体错误信息如下：{}'.format(cookies.index(i) + 1, sign_return.status_code, sign_return.text)
                failure.append(cookie)
                msg.append(message)
            elif not signerror and sign_return is None:
                message = '第{}个账号签到失败，未获取到返回结果。'.format(cookies.index(i) + 1)
                failure.append(cookie)
                msg.append(message)
    outputmsg = str(msg).replace("[", '').replace(']', '').replace(',', '<br>').replace('\'', '')
    scinfomsg = '''
    网易云游戏自动签到脚本运行结果：\n
    成功数量：{0}/{2}\n
    失败数量：{1}/{2}\n
    具体情况如下：\n
    {3}\n
    原作者信息: \n
    GamerNoTitle: https://bili33.top \n
    网易云游戏自动签到脚本: https://github.com/GamerNoTitle/wyycg-autocheckin \n
    '''.format(len(success), len(failure), len(cookies), outputmsg)

    server_chan_push_normal(scinfomsg)
    if (len(failure) != 0):
        raise ScriptRunError

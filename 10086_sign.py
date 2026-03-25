# -*- coding: utf-8 -*-
"""
中国移动签到脚本 (河南移动)
支持青龙面板或本地运行。

功能:
  1. 签到赢好礼   (wap.ha.10086.cn)
  2. 金币乐园打卡  (wap.ha.10086.cn)

环境变量:
  export HNCM_COOKIE="hncmjsSSOCookie=xxx; WutoO1RTtc1XP=xxx"
  # 多账号用 @ 分割
  # export HNCM_COOKIE="cookie1@cookie2"
"""

import os
import sys
import ssl
import time
from datetime import datetime
from random import uniform

try:
    import httpx
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx"])
    import httpx

# 创建兼容旧版 SSL 的上下文 (10086 服务器需要)
def _make_ssl_ctx():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
    ctx.options |= getattr(ssl, "OP_LEGACY_SERVER_CONNECT", 0x4)
    return ctx

SSL_CTX = _make_ssl_ctx()

# 通知内容收集
msg_info = []

def log(msg):
    """打印并记录日志"""
    print(msg)
    msg_info.append(msg)

def send_notify(title, content):
    """尝试调用青龙面板通知 (如果有 sendNotify 模块)"""
    try:
        from sendNotify import send  # 青龙内置
        send(title, content)
    except Exception:
        pass  # 非青龙环境忽略


# ======================= [1. 签到赢好礼] =======================
def sign_in_gift(cookie_str, index):
    """
    河南移动 - 签到赢好礼
    Step 1: POST /h5-act/signIn/init   → 初始化/查询签到状态
    Step 2: POST /h5-act/signIn/click  → 执行签到动作
    """
    log(f"--- 账号 {index} [签到赢好礼] ---")

    auth_value = ""
    for part in cookie_str.split(";"):
        part = part.strip()
        if part.startswith("hncmjsSSOCookie="):
            auth_value = part
            break

    headers = {
        "Host": "wap.ha.10086.cn",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://wap.ha.10086.cn",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148/wkwebview leadeon/12.0.8/CMCCIT",
        "Referer": "https://wap.ha.10086.cn/hnmccClientWap/act_h5/html/h5/signNew/index?channel=channel_WD",
        "Cookie": cookie_str,
    }
    if auth_value:
        headers["Authorization"] = auth_value

    payload_init = {
        "channel": "channel_WD",
        "recommend": "",
        "optno": "",
        "optcity": "",
        "subchannel": "",
        "appId": ""
    }

    payload_click = payload_init.copy()
    payload_click["taskId"] = ""  # click 请求多了一个空 taskId

    try:
        with httpx.Client(verify=SSL_CTX, timeout=15) as client:
            # Step 1: 初始化，检查今日是否已签到
            init_url = "https://wap.ha.10086.cn/h5-act/signIn/init"
            resp = client.post(init_url, headers=headers, json=payload_init)
            data = resp.json()
            inner = data.get("data", {}) or {}
            code = inner.get("code")
            sign_today = inner.get("signToday", "0")

            if data.get("code") == "1" and code == "10" and str(sign_today) == "1":
                sign_num = inner.get("signNum", "?")
                log(f"  ℹ️ 今日已签到, 本月累计 {sign_num} 天")
                return
            elif data.get("code") == "1" and code == "10" and str(sign_today) == "0":
                log("  [DEBUG] 检测到未签到，准备执行签到...")
            else:
                log(f"  ❌ 初始化异常返回: {resp.text[:300]}")
                return

            # Step 2: 执行签到动作
            sign_url = "https://wap.ha.10086.cn/h5-act/signIn/click"
            time.sleep(uniform(0.5, 1.5))
            resp2 = client.post(sign_url, headers=headers, json=payload_click)
            data2 = resp2.json()
            inner2 = data2.get("data", {}) or {}
            code2 = inner2.get("code")

            if data2.get("code") == "1" and code2 == "10":
                sign_num = inner2.get("signNum", "?")
                prize = inner2.get("prizeName", "未知奖品")
                log(f"  ✅ 签到成功! 本月累计 {sign_num} 天, 获得: {prize}")
            elif data2.get("code") == "1" and code2 == "11":
                log(f"  ℹ️ 今日已签到")
            elif data2.get("code") == "0" and "已" in data2.get("msg", ""):
                log(f"  ℹ️ {data2.get('msg', '今日已签到')}")
            else:
                log(f"  ❌ 签到失败: {resp2.text[:300]}")
    except Exception as e:
        log(f"  ❌ 请求出错: {e}")

    time.sleep(uniform(1, 3))


# ======================= [2. 金币乐园打卡] =======================
def coin_park(cookie_str, index):
    """
    河南移动 - 金币乐园签到
    POST https://wap.ha.10086.cn/h5-act/goldSignIn/signIn
    """
    log(f"--- 账号 {index} [金币乐园打卡] ---")

    url = "https://wap.ha.10086.cn/h5-act/goldSignIn/signIn"

    auth_value = ""
    for part in cookie_str.split(";"):
        part = part.strip()
        if part.startswith("hncmjsSSOCookie="):
            auth_value = part
            break

    headers = {
        "Host": "wap.ha.10086.cn",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://wap.ha.10086.cn",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148/wkwebview leadeon/12.0.8/CMCCIT",
        "Referer": "https://wap.ha.10086.cn/hnmccClientWap/act_h5/html/h5/goldService/index?channel=channel_JT",
        "Cookie": cookie_str,
    }
    if auth_value:
        headers["Authorization"] = auth_value

    payload = {
        "channel": "channel_JT",
        "phone": "",
        "optno": "",
        "optcity": "",
        "subchannel": "",
        "appId": ""
    }

    try:
        with httpx.Client(verify=SSL_CTX, timeout=15) as client:
            resp = client.post(url, headers=headers, json=payload)
            data = resp.json()
            inner = data.get("data", {}) or {}
            code = inner.get("code")
            if data.get("code") == "1" and code == "10":
                prize = inner.get("prizeName", "未知")
                sign_num = inner.get("signInNum", "?")
                log(f"  ✅ 打卡成功! 奖励: {prize}, 累计打卡 {sign_num} 天")
            elif data.get("code") == "1" and code == "11":
                log(f"  ℹ️ 今日已打卡")
            elif data.get("code") == "0" and "已完成" in data.get("msg", ""):
                log(f"  ℹ️ {data.get('msg', '今日已打卡')}")
            else:
                log(f"  ❌ 异常返回: {resp.text[:300]}")
    except Exception as e:
        log(f"  ❌ 请求出错: {e}")

    time.sleep(uniform(1, 3))


# ======================= 主入口 =======================
def main():
    log("=" * 50)
    log("中国移动签到脚本 v2.2")
    log(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 50)

    # ---- 读取河南移动 cookie (签到赢好礼 + 金币乐园) ----
    hncm_cookie = os.environ.get("HNCM_COOKIE", "")
    if not hncm_cookie:
        hncm_cookie = os.environ.get("10086_COOKIE", "")

    if hncm_cookie:
        hncm_accounts = [c.strip() for c in hncm_cookie.split("@") if c.strip()]
        log(f"\n河南移动: 检测到 {len(hncm_accounts)} 个账号")
        for i, cookie in enumerate(hncm_accounts, 1):
            sign_in_gift(cookie, i)
            coin_park(cookie, i)
    else:
        log("\n⚠️ 未设置 HNCM_COOKIE, 跳过签到")
        log('  设置方法: export HNCM_COOKIE="hncmjsSSOCookie=xxx; WutoO1RTtc1XP=xxx"')

    log("\n" + "=" * 50)
    log("全部任务执行完毕!")
    log("=" * 50)

    # 青龙通知
    send_notify("中国移动签到", "\n".join(msg_info))


if __name__ == "__main__":
    main()

# 中国移动自动签到脚本

这是一个用于自动完成中国移动（河南地区）相关签到活动的 Python 脚本。
目前支持以下活动 (当前版本 Version: v2.2)：
1. **签到赢好礼** (`wap.ha.10086.cn/h5-act/signIn/click`) - *已经修复最新版强制打卡动作*
2. **金币乐园打卡** (`wap.ha.10086.cn/h5-act/goldSignIn/signIn`)

*(注：由于全国版“签到有礼”活动采用了强依赖 APP 内部 SDK 及极短过期周期的动态 Token，目前已从脚本中移除。)*

## 特性

- ✅ 支持原生的 SSL 配置，完美解决 10086 服务器 `SSLV3_ALERT_HANDSHAKE_FAILURE` 握手失败问题
- ✅ 支持青龙面板部署
- ✅ 支持多账号并发（通过 `@` 符号分割）
- ✅ 青龙面板自动消息通知推送

## 环境要求

- Python 3.6+
- 依赖包: `httpx` (脚本运行时会自动检测并尝试安装)

## 抓包指南

此脚本仅需要抓取 **河南移动** 域名的网页 Cookie。

1. 打开抓包软件（如 Stream、HttpCanary、Thor 等），开启 HTTPS 解密
2. 打开中国移动 APP
3. 进入 **签到赢好礼** 或 **金币乐园** 活动页面
4. 在抓包历史中找到域名为 `wap.ha.10086.cn` 的请求
5. 查看请求头 (Request Headers) 中的 `Cookie` 字段
6. 提取需要的两个关键值：
   - `hncmjsSSOCookie=...` (这个最重要，用于生成 Authorization)
   - `WutoO1RTtc1XP=...` (防护相关)
   > 最好直接复制包含这两个键值的完整 Cookie 字符串。

## 使用方法

### 方式一：青龙面板配置 (推荐)

1. 登录您的青龙面板
2. 进入 **环境变量** 页面
3. 添加新的环境变量：
   - **名称**: `HNCM_COOKIE`
   - **值**: 填入你抓到的 Cookie，格式如：`hncmjsSSOCookie=xxx; WutoO1RTtc1XP=xxx`
4. 如果有多个手机号账号，使用 `@` 符号连接不同的 Cookie：
   - 示例: `cookie1@cookie2@cookie3`
5. 在青龙面板的“脚本管理”中新建脚本 `10086_sign.py`，粘贴代码。
6. 添加定时任务，建议每天上午运行一次，如 `0 9 * * *`。

### 方式二：本地直接运行

在命令行/终端中设置环境变量并运行脚本：

```bash
# Windows (PowerShell)
$env:HNCM_COOKIE="hncmjsSSOCookie=xxxx; WutoO1RTtc1XP=xxxx"
python 10086_sign.py

# Linux / macOS
export HNCM_COOKIE="hncmjsSSOCookie=xxxx; WutoO1RTtc1XP=xxxx"
python3 10086_sign.py
```

## 免责声明

本脚本仅供学习与交流使用，禁止用于任何商业用途。使用者因违规使用产生的任何风险和责任由使用者自行承担。

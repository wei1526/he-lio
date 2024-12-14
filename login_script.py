from playwright.sync_api import sync_playwright
import os
import requests

def send_telegram_message(message):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    return response.json()

def login_heliohost(email, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        page = context.new_page()

        # 加载登录页面
        page.goto("https://www.heliohost.org/login", wait_until="networkidle")

        # 等待输入框并填写表单
        page.wait_for_selector('input[name="email"]', timeout=60000)
        page.fill('input[name="email"]', email)
        page.fill('input[name="password"]', password)
        page.fill('input[name="redirect"]', "/dashboard/")  # 填写隐藏字段

        # 提交表单
        page.evaluate("document.querySelector('form').submit()")

        # 等待登录结果
        try:
            # 检查是否跳转到仪表板
            page.wait_for_url("https://heliohost.org/dashboard", timeout=10000)
            return f"账号 {email} 登录成功!"
        except:
            # 检查是否有错误消息
            error_message = page.locator('.MuiAlert-message').first
            if error_message.is_visible():
                error_text = error_message.inner_text()
                return f"账号 {email} 登录失败: {error_text}"
            else:
                return f"账号 {email} 登录失败: 未知错误"
        finally:
            browser.close()

if __name__ == "__main__":
    accounts = os.environ.get('WEBHOST', '').split()
    login_statuses = []

    for account in accounts:
        email, password = account.split(':')
        status = login_heliohost(email, password)
        login_statuses.append(status)
        print(status)

    if login_statuses:
        message = "HelioHost登录状态:\n\n" + "\n".join(login_statuses)
        result = send_telegram_message(message)
        print("消息已发送到Telegram:", result)
    else:
        error_message = "没有配置任何账号"
        send_telegram_message(error_message)
        print(error_message)

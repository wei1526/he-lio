from playwright.sync_api import sync_playwright
import os
import requests

def send_telegram_message(message):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()

def login_heliohost(email, password):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()

        # 访问登录页面
        page.goto("https://heliohost.org/login")

        # 输入邮箱和密码
        page.fill('input[placeholder="Email Address/Username"]', email)
        page.fill('input[placeholder="Password"]', password)
    
        # 点击登录按钮
        page.click('button:has-text("Login")')

        # 等待页面加载或错误消息
        try:
            # 检查错误消息
            error_message = page.wait_for_selector('.MuiAlert-message', timeout=15000)
            if error_message:
                error_text = error_message.inner_text()
                return f"账号 {email} 登录失败: {error_text}"
        except:
            # 如果没有找到错误消息，检查是否登录成功
            try:
                page.wait_for_url("https://heliohost.org/dashboard", timeout=15000)
                return f"账号 {email} 登录成功!"
            except:
                return f"账号 {email} 登录失败: 未能跳转到仪表板页面"
        finally:
            browser.close()

if __name__ == "__main__":
    accounts = os.environ.get('WEBHOST', '').split()
    login_statuses = []

    if not accounts:
        error_message = "没有配置任何账号"
        send_telegram_message(error_message)
        print(error_message)
    else:
        for account in accounts:
            email, password = account.split(':')
            status = login_heliohost(email, password)
            login_statuses.append(status)
            print(status)

        # 发送状态到 Telegram
        message = "HelioHost登录状态:\n\n" + "\n".join(login_statuses)
        result = send_telegram_message(message)
        print("消息已发送到Telegram:", result)

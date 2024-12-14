from requests import post, get
from os import getenv
from time import strftime, gmtime

# Environment variables
# TELEGRAM_BOT_TOKEN - The token for the Telegram bot
# TELEGRAM_CHAT_ID - The chat ID to send the message to
# HELIOSHOST_USER - The username of the HelioHost account
# HELIOSHOST_PWD - The password of the HelioHost account


def run(username: str, password: str, user_agent: str = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36") -> bool:
    # Perform login by POST request
    login_response = post(
        "https://www.heliohost.org/login/",
        headers={
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Origin": "https://www.heliohost.org",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://www.heliohost.org/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        },
        data={
            "email": username,
            "password": password
        }
    )
    
    # After login, check if we are successfully redirected to the dashboard
    if login_response.ok:
        dashboard_response = get("https://heliohost.org/dashboard/", headers={
            "User-Agent": user_agent,
        })
        
        # If the response contains a known string that appears only when logged in (e.g., username), consider it successful
        if "HelioHost Dashboard" in dashboard_response.text:  # Adjust this based on the actual page content
            return True  # Successfully logged in and redirected to dashboard
        else:
            return False  # Failed to log in or dashboard page didn't load properly
    else:
        return False  # Login failed


def send_telegram_message(message):
    bot_token = getenv('TELEGRAM_BOT_TOKEN')
    chat_id = getenv('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()


def automatic_execution():
    now = gmtime()
    print(f"\nScript running @ \33[36m{strftime('%Y-%m-%dT%H:%M:%SZ', now)}\33[0m...", end=' ', flush=True)
    
    # Run the login check
    login_success = run(getenv("HELIOSHOST_USER"), getenv("HELIOSHOST_PWD"))
    
    if login_success:
        print("\33[32mlogged in successfully.\33[0m")
    else:
        print("\33[31mlogin failed.\33[0m")
    
    # Don't print too much information to the console, because unauthorized eyes might see it
    if login_success:
        message = f"""HelioHost

{' ' if not now else f' ({strftime("%Y-%m-%dT%H:%M:%SZ", now)})'} 尝试登录, 登陆成功.

"""
    else:
        message = f"""HelioHost

{' ' if not now else f' ({strftime("%Y-%m-%dT%H:%M:%SZ", now)})'} 尝试登录, 登陆失败.

"""
    
    # Send Telegram message
    if getenv("TELEGRAM_BOT_TOKEN") and getenv("TELEGRAM_CHAT_ID"):
        print(f"Sending message to Telegram bot...", end=' ', flush=True)
        send_telegram_message(message)
        print("\33[32mdone.\33[0m")
    else:
        print(
            "No Telegram bot token or chat ID specified.",
            "Not sending any messages.",
            sep='\n'
        )
    
    print("\33[42mAutomatic script execution completed.\33[0m")


if __name__ == '__main__':
    automatic_execution()

from requests import post
import requests  # Make sure to import the entire requests module
from os import getenv
from time import strftime, gmtime

# Environment variables
# TELEGRAM_BOT_TOKEN - The token for the Telegram bot
# TELEGRAM_CHAT_ID - The chat ID to send the message to
# HELIOSHOST_USER -  The username of the HelioHost account
# HELIOSHOST_PWD -  The password of the HelioHost account

def run(username: str,
        password: str,
        user_agent: str = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
        ) -> str:
    r = post(
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
    
    cookies = r.headers.get('Set-Cookie')
    
    if cookies:
        return cookies
    else:
        return "No cookies returned from login."


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
    
    cookie_response = run(getenv("HELIOSHOST_USER"), getenv("HELIOSHOST_PWD"))
    
    print("\33[32mlogged in.\33[0m")
    
    # Don't print too much information to the console, because unauthorized eyes might see it
    print("Server Response (trimmed):", cookie_response[0:11])
    
    if getenv("TELEGRAM_BOT_TOKEN") and getenv("TELEGRAM_CHAT_ID"):
        print(f"Sending message to Telegram bot...", end=' ', flush=True)
        
        message = f"""Hello there!

Thanks for using the HelioHost Auto Login Bot!

We recently{' ' if not now else f' ({strftime("%Y-%m-%dT%H:%M:%SZ", now)})'} attempted a login into your account.

Here is your session cookie for Heliohost:
{cookie_response.strip()}

Sincerely,
HelioHost Auto Login Bot."""
        
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

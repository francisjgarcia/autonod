#!/usr/bin/env python

from dotenv import load_dotenv
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import requests
import os
import re
import time

# Load variables through .env file
load_dotenv()
# Telegram tokens and chat id
telegram_bot = telepot.Bot(os.getenv("TELEGRAM_TOKEN_NOTIFY"))
telegram_alert_bot = telepot.Bot(os.getenv("TELEGRAM_TOKEN_ALERT"))
telegram_id = os.getenv("TELEGRAM_ID_NOTIFY")
telegram_alert_id = os.getenv("TELEGRAM_ID_ALERT")
# Scraping URL
web_url = os.getenv("WEB_URL")
# Database connection
database_directory = os.getenv("DATABASE_DIRECTORY")
database = os.getenv("DATABASE")
table = os.getenv("TABLE")
field = os.getenv("FIELD")
# Telegram alerts messages
message_error_1 = os.getenv("MESSAGE_ERROR_1")
message_error_2 = os.getenv("MESSAGE_ERROR_2")

def main():
    try:
        sqlite3.connect(database_directory + "/" + database + ".db")
        connection = sqlite3.connect(database_directory + "/" + database + ".db")
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS " + table + " (" + field + " VARCHAR(24) NOT NULL PRIMARY KEY)")
        connection.commit()
        cursor.close()
        connection.close()
    except:
        print(message_error_1)
        raise

    while 1:
        web_status_code = requests.get(web_url).status_code
        if web_status_code == 200:
            r = requests.get(web_url, stream=True)
            for line in r.iter_lines():
                regex = re.findall(r'[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}', line.decode('ISO-8859-1'))
                for serial in regex:
                    try:
                        connection = sqlite3.connect(database_directory + "/" + database + ".db")
                        cursor = connection.cursor()
                        cursor.execute("SELECT " + field + " FROM " + table + " WHERE " + field + " = ?", [serial])
                        data=cursor.fetchone()
                        if data is None:
                            cursor.execute("INSERT INTO " + table + " VALUES(?)", [serial])
                            connection.commit()
                            print("["+time.strftime("%d/%m/%Y %H:%M:%S")+"] " + str(serial))
                            telegram_bot.sendMessage(telegram_id, serial, parse_mode='HTML')
                        cursor.close()
                        connection.close()
                    except:
                        print("["+time.strftime("%d/%m/%Y %H:%M:%S")+"] " + message_error_2)
                        telegram_bot.sendMessage(telegram_alert_id, message_error_2, parse_mode='HTML')
                    time.sleep(5)
        time.sleep(3600)

# Run application
main()

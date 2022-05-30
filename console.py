from telebot import TeleBot as tb
from settings import token, admin_id, port, password, host
from threading import Thread
import sqlite3 as sql
import os
import subprocess
import time
import mcrcon

rcon = mcrcon.MCRcon(host,password,port)
def console(chat_id):
    os.chdir('Server')
    cmd = [r"start.bat"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', shell=True)
    for line in iter(p.stdout.readline, b''):
        time.sleep(0.7)
        if line.rstrip() == '': continue
        print(line.rstrip())
        bot.send_message(chat_id, line.rstrip())

status = False

mainDir = os.getcwd()
if not os.path.isdir('Database'):
    os.mkdir('Database')
db = sql.connect('Database/admins.db', check_same_thread=False)
db.row_factory = sql.Row
cur = db.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS admins (
    admin_id INT PRIMARY KEY,
    name VARCHAR,
    permission_level INT
)''')
db.commit()

bot = tb(token)

@bot.message_handler(content_types=['text'])
def serverstart(message):
    global status
    user_id = message.from_user.id
    command = message.text
    chat_id = -1001751748072
    if command == '/add':
        for i in admin_id:
            if user_id == admin_id[i]:
                cur.execute(f"SELECT admin_id FROM admins WHERE admin_id = {admin_id[i]}")
                if cur.fetchone() is None:
                    bot.send_message(chat_id, f'Администратор {admin_id[i]} добавлен в бд / {message.from_user.first_name}')
                    cur.execute(f"INSERT INTO admins VALUES (?,?,?)", (admin_id[i],message.from_user.first_name,5))
                    db.commit()
                else:
                    print(f'{admin_id[i]} уже добавлен в базу.')
            else:
                print(f'{user_id} вызвал команду {command}')
    elif command == '/startserver':
        if status == False:
            bot.send_message(chat_id, 'Инициализация запуска...')
            try:
                status = True
                global consoleThread
                consoleThread = Thread(target=console(chat_id))
                consoleThread.start()
                consoleThread.join()
            except Exception as error:
                print(f'Возникла ошибка: {error}')
                
        elif status == True:
            bot.send_message(chat_id, 'Сервер уже включен!')
    elif command == '/stopserver':
        if status == True:
            status = False
            bot.send_message(chat_id, 'Выключаем...')
            rcon.connect()
            rcon.command('stop')
            rcon.disconnect()
        else:
            bot.send_message(chat_id, 'Сервер и так выключен!')

    
try:
    bot.polling(True)
except Exception as error:
    print(f'Telegram API: {error}')

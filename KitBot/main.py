import asyncio
import ctypes
import telebot
from telebot import types
from config import TOKEN
import json
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3

bot = telebot.TeleBot(token=TOKEN)
const = {}
with open("const.json", "r", encoding="utf-8") as file:
    const = json.load(file)

business_withdrawal_markup = types.InlineKeyboardMarkup()
business_withdrawal_markup.add(types.InlineKeyboardButton(text="📥 Снять", callback_data="business_withdrawal"))
farm_withdrawal_markup = types.InlineKeyboardMarkup()
farm_withdrawal_markup.add(types.InlineKeyboardButton(text="📥 Снять", callback_data="farm_withdrawal"))
city_withdrawal_markup = types.InlineKeyboardMarkup()
city_withdrawal_markup.add(types.InlineKeyboardButton(text="📥 Снять", callback_data="city_withdrawal"))

menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=False)
menu_markup.row(types.KeyboardButton("🪪Профиль"), types.KeyboardButton("..."), types.KeyboardButton("..."))
menu_markup.row(types.KeyboardButton("💼Бизнес"), types.KeyboardButton("🔋Ферма"), types.KeyboardButton("🌃Город"))
menu_markup.row(types.KeyboardButton("..."), types.KeyboardButton("..."), types.KeyboardButton("🎁Бонус"))
def balance_display_mod(balance):
    balance = int(balance)
    return "{:,}".format(balance).replace(',', '.')

def check_person(message):
    db = sqlite3.connect("kitbot.db")
    c = db.cursor()
    c.execute("SELECT chat_id FROM profile")
    items = c.fetchall()
    for el in items:
        if el[0] == message.chat.id:
            return True
    return False

@bot.message_handler(commands=["start"])
def check_registered(message):
    if check_person(message) is False:
        new_profile(message)
        print_profile(message)
    else:
        print_profile(message)

def new_profile(message):
    db = sqlite3.connect("kitbot.db")
    c = db.cursor()
    user_profile = (int(message.chat.id), 0, False, 'Player', str(datetime.datetime.today()), 100000, 1000000, 0, 'None', 0, 0, 'None', 0, 0, 0, 'None', 0, 50000, 0)
    c.execute("INSERT INTO profile VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", user_profile)
    db.commit()
    c.execute("SELECT * FROM profile")
    print(c.fetchall())
    db.close()

    # profile_base["profile"].append(
    #     {
    #         "chat_id": str(message.chat.id),
    #         "id": id,
    #         "admin_lvl": 0,
    #         "status": "Игрок",
    #         "banned": "False",
    #         "register_date": str(datetime.datetime.today()),
    #         "bonus_limit": 100000,
    #         "balance": 10000000,
    #         "balance_btc": 0,
    #         "business": {
    #             "name": "None",
    #             "profit": 0,
    #             "balance": 0
    #         },
    #         "farm": {
    #             "name": "None",
    #             "profit": 0,
    #             "x": 0,
    #             "balance": 0
    #         },
    #         "city": {
    #             "name": "None",
    #             "lvl": 0,
    #             "profit": 50000,
    #             "balance": 0
    #         }
    #     }
    # )
    #
    # with open("profile_base.json", "w", encoding="utf-8") as file:
    #     json.dump(profile_base, file, indent=4, ensure_ascii=False)

    print(f"[INFO] New player(ID: {message.chat.id})!")
def print_profile(message):
    db = sqlite3.connect("kitbot.db")
    c = db.cursor()
    person = c.execute(f"SELECT rowid, * FROM profile WHERE chat_id={message.chat.id}").fetchone()
    db.close()
    profile = f"""🪪 {message.from_user.full_name} твой профиль:\n\n🔑 id: {person[0]}\n"""
    profile += f"""👑Статус: {person[4]}\n"""
    profile += f"""\n💸 Баланс: {balance_display_mod(person[7])}\n💹 Биткоины: {balance_display_mod(person[8])}\n"""
    profile += f"""🌏 Имущество:\n"""
    if person[9] != "None":
        profile += f"""\n    💼 Бизнес: {person[9]}\n"""
    else:
        profile += f"""\n    💼 Бизнес: НЕТ\n"""
    if person[12] != "None":
        profile += f"""    🔋 Ферма: {person[12]} x{person[13]}\n"""
    else:
        profile += f"""    🔋 Ферма: НЕТ\n"""
    if person[16] != "None":
        profile += f"""    🌃 Город: {person[16]}\n"""
    else:
        profile += f"""    🌃 Город: НЕТ\n"""
    profile += f"""\n⌛ Регистрация: {person[5]}"""
    bot.send_message(message.chat.id, profile, reply_markup=menu_markup)

def print_business(message):
    db = sqlite3.connect("kitbot.db")
    c = db.cursor()
    person = c.execute(f"SELECT rowid, bussnes, bussnes_profit, bussnes_balance FROM profile WHERE chat_id={message.chat.id}").fetchone()
    db.close()
    business = ""
    if person[1] != "None":
        business += f"""
💼Твой бизнес:\n
📌Название: {person[1]}
📊Доход: {balance_display_mod(person[2])}$ в час
💵Баланс: {balance_display_mod(person[3])}$"""
        bot.send_message(message.chat.id, business, reply_markup=business_withdrawal_markup)
    else:
        business += f"""У тебя ещё нет бизнеса! Посмотреть список бизнесов: бизнесы"""
        bot.send_message(message.chat.id, business)
        bussiness_list(message)

def print_farm(message):
    db = sqlite3.connect("kitbot.db")
    c = db.cursor()
    person = c.execute(f"SELECT rowid, farm, farm_count, farm_profit, farm_balance FROM profile WHERE chat_id={message.chat.id}").fetchone()
    db.close()
    farm = ""
    if person[1] != "None":
        farm += f"""
🔋Твоя ферма:\n
📌Название: {person[1]} x{person[2]}
📊Доход: {balance_display_mod(person[3] * person[2])}₿ в час
💵Баланс: {balance_display_mod(person[4])}₿"""
        bot.send_message(message.chat.id, farm, reply_markup=farm_withdrawal_markup)
    else:
        farm += f"""У тебя ещё нет фермы! Посмотреть список ферм: фермы"""
        bot.send_message(message.chat.id, farm)
        farm_list(message)

def print_city(message):
    db = sqlite3.connect("kitbot.db")
    c = db.cursor()
    person = c.execute(f"SELECT rowid, city, city_lvl, city_profit, city_balance FROM profile WHERE chat_id={message.chat.id}").fetchone()
    db.close()
    city = ""
    if person[1] != "None":
        city += f"""
🌃Твой город:\n
📌Название: {person[1]}
📶Уровень: {person[2]}
📊Доход: {balance_display_mod(person[2] * person[3])}$ в час
💵Баланс: {balance_display_mod(person[4])}$"""
        bot.send_message(message.chat.id, city, reply_markup=city_withdrawal_markup)
    else:
        city +="""У тебя ещё нет города! Чтобы создать город написши: город создать"""
    bot.send_message(message.chat.id, city)

def bussiness_list(message):
    business = f"""🎩 Список доступных бизнесов:\n"""
    for b in const["BUSINESS_LIST"]:
        business += f"""
{b["NUMBER"]} {b["NAME"]}.
   💹 Доход: {balance_display_mod(b["PROFIT"])}$ в час.
   💵 Цена: {balance_display_mod(b["BUY"])}$.\n"""
    business += f"Купить бизнес: бизнесы [номер]"
    bot.send_message(message.chat.id, business)

def farm_list(message):
    farm = f"""🎩 Список доступных ферм:\n"""
    for b in const["FARM_LIST"]:
        farm += f"""
{b["NUMBER"]} {b["NAME"]}.
   🔋 Доход: {balance_display_mod(b["PROFIT"])}₿ в час.
   💵 Цена: {balance_display_mod(b["BUY"])}$.\n"""
    bot.send_message(message.chat.id, farm)

def businnes_money_withdrawal(message):
    db = sqlite3.connect("kitbot.db")
    c = db.cursor()
    person = c.execute(f"SELECT rowid, balance, bussnes_balance FROM profile WHERE chat_id={message.chat.id}").fetchone()
    if person[2] != 0:
        c.execute(f"UPDATE profile SET balance={int(person[1]) + person[2]} WHERE chat_id={message.chat.id}")
        c.execute(f"UPDATE profile SET bussnes_balance=0 WHERE chat_id={message.chat.id}")
        bot.delete_message(message.chat.id, message.id)
        bot.send_message(text="✅ Вы успешно сняли с бизнеса свои сбережения🤑", chat_id=message.chat.id)

    else:
        bot.send_message(message.chat.id, "⛔️У вас нет сбережений для снятия 😕")
    db.commit()
    db.close()


def farm_btc_withdrawal(message):
    db = sqlite3.connect("kitbot.db")
    c = db.cursor()
    person = c.execute(f"SELECT rowid, balance, farm_balance FROM profile WHERE chat_id={message.chat.id}").fetchone()
    if person[2] != 0:
        c.execute(f"UPDATE profile SET balance={int(person[1]) + person[2]} WHERE chat_id={message.chat.id}")
        c.execute(f"UPDATE profile SET farm_balance=0 WHERE chat_id={message.chat.id}")
        bot.delete_message(message.chat.id, message.id)
        bot.send_message(text="✅ Вы успешно сняли с бизнеса свои сбережения🤑", chat_id=message.chat.id)

    else:
        bot.send_message(message.chat.id, "⛔️У вас нет сбережений для снятия 😕")
    db.commit()
    db.close()

def city_money_withdrawal(message):
    db = sqlite3.connect("kitbot.db")
    c = db.cursor()
    person = c.execute(f"SELECT rowid, balance, city_balance FROM profile WHERE chat_id={message.chat.id}").fetchone()
    if person[2] != 0:
        c.execute(f"UPDATE profile SET balance={int(person[1]) + person[2]} WHERE chat_id={message.chat.id}")
        c.execute(f"UPDATE profile SET city_balance=0 WHERE chat_id={message.chat.id}")
        bot.delete_message(message.chat.id, message.id)
        bot.send_message(text="✅ Вы успешно сняли с бизнеса свои сбережения🤑", chat_id=message.chat.id)

    else:
        bot.send_message(message.chat.id, "⛔️У вас нет сбережений для снятия 😕")
    db.commit()
    db.close()

def business_mining():
    db = sqlite3.connect("kitbot.db")
    c = db.cursor()
    c.execute(f"UPDATE profile SET bussnes_balance=bussnes_balance+bussnes_profit")
    db.commit()
    db.close()

def farm_mining():
    db = sqlite3.connect("kitbot.db")
    c = db.cursor()
    c.execute(f"UPDATE profile SET farm_balance=farm_balance+farm_profit")
    db.commit()
    db.close()

def city_mining():
    db = sqlite3.connect("kitbot.db")
    c = db.cursor()
    c.execute(f"UPDATE profile SET city_balance=city_balance+city_profit*city_lvl")
    db.commit()
    db.close()


def buy_business(message):
    business_number = int(message.text.lower().split(" ")[1])
    if business_number > 10:
        bot.send_message(message.chat.id,f"💀Такой номер бизнеса не найден!\n💵Чтобы купить бизнес напишите: бизнесы [номер]\n✉️Например: бизнесы 2")
    else:
        db = sqlite3.connect("kitbot.db")
        c = db.cursor()
        person = c.execute(f"SELECT rowid, balance, bussnes FROM profile WHERE chat_id={message.chat.id}").fetchone()
        if person[2] != "None":
            bot.send_message(message.chat.id, f"""⚠️У вас уже есть бизнес! 
Для продажи бизнеса напишите: продать бизнес""")
        elif person[1] < const["BUSINESS_LIST"][business_number - 1]["BUY"]:
            bot.send_message(message.chat.id, f"""⚠️Недостаточно средств для покупки бизнеса!
💰Стоимость бизнеса: {balance_display_mod(const['BUSINESS_LIST'][business_number - 1]['BUY'])}$
💵Баланс:{balance_display_mod(person[1])}$""")
        else:
            c.execute(f"UPDATE profile SET bussnes='{const['BUSINESS_LIST'][business_number - 1]['NAME']}', bussnes_profit={const['BUSINESS_LIST'][business_number - 1]['PROFIT']}, bussnes_balance=0 WHERE chat_id={message.chat.id}")
            c.execute(f"UPDATE profile SET balance={person[1] - const['BUSINESS_LIST'][business_number - 1]['BUY']} WHERE chat_id={message.chat.id}")
            db.commit()
            person = c.execute(f"SELECT rowid, balance FROM profile WHERE chat_id={message.chat.id}").fetchone()
            bot.send_message(message.chat.id,f"""👑 Вы успешно купили бизнес {const['BUSINESS_LIST'][business_number - 1]['NAME']} за {balance_display_mod(const['BUSINESS_LIST'][business_number - 1]['BUY'])}$ 💎
💰Остаток на балансе: {balance_display_mod(person[1])}$""")
        db.close()

def buy_farm(message):
    farm_number = int(message.text.lower().split(" ")[1])
    farm_count = int(message.text.lower().split(" ")[2])
    if farm_number > 7:
        bot.send_message(message.chat.id,
                         f"💀Такой номер фермы не найден!\n💵Чтобы купить фермы напишите: фермы [номер] [кол-во]\n✉️Например: фермы 3 10")
    else:
        db = sqlite3.connect("kitbot.db")
        c = db.cursor()
        person = c.execute(f"SELECT rowid, balance, farm, farm_count FROM profile WHERE chat_id={message.chat.id}").fetchone()
        if person[2] != "None" and person[2] != const["FARM_LIST"][farm_number - 1]["NAME"]:
            bot.send_message(message.chat.id, f"""⚠️У вас уже есть фермы! 
Для продажи ферм напишите: продать фермы""")
        elif person[1] < const["FARM_LIST"][farm_number - 1]["BUY"] * farm_count:
            bot.send_message(message.chat.id, f"""⚠️Недостаточно средств для покупки бизнеса!
💰Стоимость ферм: {balance_display_mod(const['FARM_LIST'][farm_number - 1]['BUY'] * farm_count)}$
💵Баланс:{balance_display_mod(person[1])}$""")
        else:
            c.execute(
                f"UPDATE profile SET farm='{const['FARM_LIST'][farm_number - 1]['NAME']}', farm_profit={const['FARM_LIST'][farm_number - 1]['PROFIT']}, farm_balance=0, farm_count={person[3] + farm_count} WHERE chat_id={message.chat.id}")
            c.execute(
                f"UPDATE profile SET balance={person[1] - const['FARM_LIST'][farm_number - 1]['BUY']} WHERE chat_id={message.chat.id}")
            db.commit()
            person = c.execute(f"SELECT rowid, balance FROM profile WHERE chat_id={message.chat.id}").fetchone()
            bot.send_message(message.chat.id,
                             f"""👑 Вы успешно купили фермы {const['FARM_LIST'][farm_number - 1]['NAME']} за {balance_display_mod(const['FARM_LIST'][farm_number - 1]['BUY'] * farm_count)}$ 💎
💰Остаток на балансе: {balance_display_mod(person[1])}$""")
        db.close()

def update_bonus_limit():
    if str(datetime.datetime.today().hour) == "23" and str(datetime.datetime.today().minute) == "45":
        db = sqlite3.connect("kitbot.db")
        c = db.cursor()
        c.execute(f"UPDATE profile SET bonus_limit=100000")
        db.commit()
        db.close()
        print(f"[INFO] Bonus limit update!")

def give_bonus(message):
    db = sqlite3.connect("kitbot.db")
    c = db.cursor()
    person = c.execute(f"SELECT rowid, bonus_limit, balance FROM profile WHERE chat_id={message.chat.id}").fetchone()
    if person[1] != 0:
        c.execute(f"UPDATE profile SET balance={person[2] + person[1]}, bonus_limit=0 WHERE chat_id={message.chat.id}")
        bot.send_message(message.chat.id,f"""💸Бонус {balance_display_mod(person[1])}$ успешно получен!\nПриходи за новым бонусом завтра!😎""")
    else:
        bot.send_message(message.chat.id, "🎁 Сегодня ты уже забрал бонус. \n⏱Приходи за новым бонусом завтра!⏱")
    db.commit()
    db.close()

def seller(message):
    why_sell = message.text.lower().split()[1]
    if why_sell == "бизнес":
        db = sqlite3.connect("kitbot.db")
        c = db.cursor()
        person = c.execute(f"SELECT rowid, bussnes, bussnes_balance, balance FROM profile WHERE chat_id={message.chat.id}").fetchone()
        if person[1] != "None":
            sell_sum = 0
            for bussnes in const["BUSINESS_LIST"]:
                if bussnes["NAME"] == person[1]:
                    sell_sum = bussnes["BUY"] / 2 + person[2]
                    break
            c.execute(f"UPDATE profile SET bussnes='None', bussnes_balance=0, balance={person[3] + sell_sum} WHERE chat_id={message.chat.id}")
            db.commit()
            db.close()
            bot.send_message(message.chat.id, f"🤩Вы успешно продали бизнесс {person[1]} за {balance_display_mod(sell_sum)}$💎")
        else:
            bot.send_message(message.chat.id, "⛔У вас нет бизнеса для продажи!")
    if why_sell == "фермы":
        count_sell = int(message.text.lower().split()[2])
        db = sqlite3.connect("kitbot.db")
        c = db.cursor()
        person = c.execute(f"SELECT rowid, farm, farm_balance, balance, balance_btc, farm_count FROM profile WHERE chat_id={message.chat.id}").fetchone()
        if person[1] != "None":
            if count_sell <= person[5]:
                sell_sum = 0
                for farm in const["FARM_LIST"]:
                    if farm["NAME"] == person[1]:
                        sell_sum = farm["BUY"] / 2 * count_sell
                        break
                if count_sell == person[5]:
                    c.execute(f"UPDATE profile SET farm='None', farm_balance=0, farm_count=0, balance={person[3] + sell_sum}, balance_btc={person[4] + person[2]} WHERE chat_id={message.chat.id}")
                else:
                    c.execute(f"UPDATE profile SET balance={person[3] + sell_sum}, farm_count={person[5] - count_sell} WHERE chat_id={message.chat.id}")
                db.commit()
                db.close()
                bot.send_message(message.chat.id, f"🤩Вы успешно продали фермы {person[1]}x{count_sell} за {balance_display_mod(sell_sum)}$💎")
            else:
                bot.send_message(message.chat.id, "⛔У вас нет столько ферм для продажи для продажи!")


def admin_commands(message):
    global  const
    db = sqlite3.connect("kitbot.db")
    c = db.cursor()
    person = c.execute(f"SELECT rowid, chat_id, status FROM profile WHERE chat_id={message.chat.id}").fetchone()
    if person[2] == "Admin":
        mes = message.text.lower().split()
        if mes[0] == "givemoney":
            c.execute(f"UPDATE profile SET balance+='{int(mes[2])}' WHERE rowid={mes[1]}")
            bot.send_message(message.chat.id, "✅ Успешно!")
    elif person[2] == "Owner":
        mes = message.text.lower().split()
        if mes[0] == "setbussnes":
            if mes[2] == "0":
                c.execute(f"UPDATE profile SET bussnes='None', bussnes_profit=0, bussnes_balance=0 WHERE rowid={mes[1]}")
                bot.send_message(message.chat.id, "✅ Успешно!")
            else:
                name = str(const['BUSINESS_LIST'][int(mes[2]) - 1]['NAME'])
                profit = int(const['BUSINESS_LIST'][int(mes[2]) - 1]['PROFIT'])
                c.execute(f"UPDATE profile SET bussnes='{name}', bussnes_profit='{profit}', bussnes_balance=0 WHERE rowid={mes[1]}")
                bot.send_message(message.chat.id, "✅ Успешно!")
        if mes[0] == "givemoney":
            bal = c.execute(f"SELECT balance FROM profile WHERE rowid={mes[1]}").fetchone()
            c.execute(f"UPDATE profile SET balance={int(bal[0]) + int(mes[2])} WHERE rowid={mes[1]}")
            bot.send_message(message.chat.id, "✅ Успешно!")
    else:
        bot.send_message(message.chat.id, "🚫У вас нет прав для выполнения данной команды.")

    db.commit()
    db.close()




@bot.message_handler(func= lambda message: True)
def reply_to_messages(message):
    if message.text.lower() in ["профиль", "проф", "🪪профиль"]:
        print_profile(message)
    elif message.text.lower().split(" ")[0] == "бизнесы":
        message_splited = message.text.lower().split(" ")
        if len(message_splited) == 1:
            bussiness_list(message)
        if len(message_splited) == 2:
            buy_business(message)
    elif message.text.lower() in ["💼бизнес", "бизнес"]:
        print_business(message)
    elif message.text.lower() in ["ферма", "🔋ферма"]:
        print_farm(message)
    elif message.text.lower() in ["город", "🌃город"]:
        print_city(message)
    elif message.text.lower().split(" ")[0] == "фермы":
        message_splited = message.text.lower().split(" ")
        if len(message_splited) == 1:
            farm_list(message)
        if len(message_splited) == 3:
            buy_farm(message)
    elif message.text.lower() in ["🎁бонус", "бонус"]:
        give_bonus(message)
    elif message.text.lower().split()[0] in ["setbussnes", "givemoney"]:
        admin_commands(message)
    elif message.text.lower().split()[0] == "продать":
        seller(message)
    else:
        bot.send_message(message.chat.id, "Такой команды не найдено, повторите попытку.")

@bot.callback_query_handler(func= lambda call: True)
def callback_query(call):
    if call.data == "business_withdrawal":
        businnes_money_withdrawal(call.message)
    elif call.data == "farm_withdrawal":
        farm_btc_withdrawal(call.message)
    elif call.data == "city_withdrawal":
        city_money_withdrawal(call.message)

def scheduler_create_jobs(scheduler):
    scheduler.add_job(business_mining, trigger="cron", minute=45)
    scheduler.add_job(farm_mining, trigger="cron", minute=45)
    scheduler.add_job(city_mining, trigger="cron", minute=45)
    scheduler.add_job(update_bonus_limit, trigger="interval", minutes=1)
async def minning():
    scheduler = BackgroundScheduler()
    scheduler_create_jobs(scheduler)
    scheduler.start()
    print(f"[INFO] Bot started!")
    bot.polling()


if __name__ == "__main__":
    db = sqlite3.connect("kitbot.db")
    c = db.cursor()
    # c.execute("UPDATE profile SET balance=100000 WHERE rowid=4")
    db.commit()
    db.close()
    asyncio.run(minning())
    # db = sqlite3.connect('kitbot.db')
    # c = db.cursor()
    # c.execute("""CREATE TABLE profile (
    # chat_id,
    # id,
    # banned,
    # status,
    # register_date,
    # bonus_limit,
    # balance,
    # balance_btc,
    # bussnes,
    # bussnes_profit,
    # bussnes_balance,
    # farm,
    # farm_count,
    # farm_profit,
    # farm_balance,
    # city,
    # city_lvl,
    # city_profit,
    # city_balance)""")
    # db.commit()
    #
    # db.close()
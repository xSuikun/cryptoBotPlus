import requests
import telebot
from auth_data import token
# Default coins to check: BTC-USD
# To select another pair of coins, you can enter "coin 1-coin 2" separated by a hyphen. You can also set the number of operations for which you want to view the "general request for trading" and "general trading rates", by default limit = 150


def get_help_message():
    help_message = 'Для вас доступны 3 функции:\n' \
                   'ticker — показывает информацию о выбранной монете за последние 24 часа.\n' \
                   "Пример запроса: 'ticker eth', где eth - интересующая нас монета.\n\n" \
                   'depths — показывает на сколько в сумме выстевлено ордеров на продажу по выбранной монете в установленном лимите.\n' \
                   "Пример запроса: 'depths btc, 150', где btc - интересующая нас монета, а 150 - лимит ордеров. Лимит - необязательный параметр, по умолчанию он установлен на 150. Его максимальное значение - 2000.\n\n" \
                   "trades — показывает на сколько в сумме завершено ордеров на продажу и покупку по выбранной монете в установленном лимите.\n" \
                   "Пример запроса: 'trades btc, 150', где btc - интересующая нас монета, а 150 - лимит ордеров. Лимит - необязательный параметр, по умолчанию он установлен на 150. Его максимальное значение - 2000.\n"
    return help_message


def get_info():
    response = requests.get(url='https://yobit.net/api/3/info')

    with open('info.txt', 'w') as file:
        file.write(response.text)

    return response.text


def get_ticker(coin1="btc", coin2="usd"):
    response = requests.get(url=f'https://yobit.net/api/3/ticker/{coin1}_{coin2}?ignore_invalid=1')

    with open('ticker.txt', 'w') as file:
        file.write(response.text)

    info = response.json()[f"{coin1}_{coin2}"]

    return f"HIGH: {info['high']}\n" \
           f"LOW: {info['low']}\n" \
           f"AVG: {info['avg']}\n" \
           f"LAST: {info['last']}\n" \
           f"BUY: {info['buy']}\n" \
           f"SELL: {info['sell']}"


def get_depths(coin1="btc", coin2="usd", limit=150):
    response = requests.get(url=f'https://yobit.net/api/3/depth/{coin1}_{coin2}?limit={limit}&ignore_invalid=1')

    with open('depths.txt', 'w') as file:
        file.write(response.text)

    bids = response.json()[f"{coin1}_{coin2}"]["bids"]

    total_bids_amount = 0
    for item in bids:
        price = item[0]
        coin_amount = item[1]

        total_bids_amount += price * coin_amount

    return f'DEPTHS:\nTotal bids: {total_bids_amount} | LIMIT: {limit}'


def get_trades(coin1="btc", coin2="usd", limit=150):
    response = requests.get(url=f'https://yobit.net/api/3/trades/{coin1}_{coin2}?limit={limit}&ignore_invalid=1')

    with open('trades.txt', 'w') as file:
        file.write(response.text)

    total_trade_ask = 0
    total_trade_bid = 0

    for item in response.json()[f'{coin1}_{coin2}']:
        if item['type'] == 'ask':
            total_trade_ask += item['price'] * item['amount']
        else:
            total_trade_bid += item['price'] * item['amount']

    info = f"TRADES:\n[-] TOTAL {coin1.upper()} SELL: {round(total_trade_ask, 2)} {coin2.upper()} | LIMIT: {limit}\n[+] TOTAL {coin1.upper()} BUY: {round(total_trade_bid, 2)} {coin2.upper()} | LIMIT: {limit}"

    return info


def run_operation(operation_name, operation_method, message, bot):
    clear_message = message.text.replace(operation_name, '').strip().split(',')
    if len(clear_message) == 1:
        try:
            bot.send_message(message.chat.id, operation_method(coin1=clear_message[0]))
        except Exception as ex:
            print(ex)
            bot.send_message(message.chat.id, f"Ошибка поиска пары {clear_message[0]}-usd")
    elif len(clear_message) == 2:
        try:
            bot.send_message(message.chat.id, operation_method(coin1=clear_message[0], limit=clear_message[1]))
        except Exception as ex:
            print(ex)
            bot.send_message(message.chat.id, f"Ошибка поиска пары {clear_message}-usd")


def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start'])
    def send_message(message):
        bot.send_message(message.chat.id, get_help_message())

    @bot.message_handler(commands=['help'])
    def send_message(message):
        bot.send_message(message.chat.id, get_help_message())

    @bot.message_handler(content_types=['text'])
    def send_text(message):
        if 'trades' in message.text.lower():
            run_operation('trades', get_trades, message, bot)
        elif 'depths' in message.text.lower():
            run_operation('depths', get_depths, message, bot)
        elif 'ticker' in message.text.lower():
            try:
                clear_message = message.text.lower().replace('ticker', '').strip()
                bot.send_message(message.chat.id, get_ticker(coin1=clear_message))
            except Exception as ex:
                print(ex)
                bot.send_message(message.chat.id, f"Ошибка поиска пары {clear_message}-usd")
        else:
            bot.send_message(message.chat.id, 'Неверная команда')

    bot.polling()



def main():
    telegram_bot(token)

if __name__ == '__main__':
    main()
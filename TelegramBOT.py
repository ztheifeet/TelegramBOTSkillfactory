import json
import requests
import telebot

class APIException(Exception):
    pass

class Converter:
    @staticmethod
    def get_price(base, quote, amount):
        if base == quote:
            raise APIException('Нельзя перевести валюту саму в себя.')

        try:
            base_ticker = base.upper()
            quote_ticker = quote.upper()
            amount = float(amount)
        except ValueError:
            raise APIException('Неверно введено число.')

        url = f'https://api.exchangeratesapi.io/latest?base={base_ticker}&symbols={quote_ticker}'
        response = requests.get(url)

        if response.status_code != 200:
            raise APIException('Ошибка при получении курса валют.')

        result = json.loads(response.content)
        price = result['rates'][quote_ticker] * amount

        return round(price, 2)

config = {
    'token': '6562728264:AAHXt2hgfwzm0_aAh6i6X_hg8VIMdoBm4T0'
}

bot = telebot.TeleBot(config['token'])

@bot.message_handler(commands=['start', 'help'])
def send_instructions(message):
    instructions = 'Чтобы узнать цену валюты, отправьте сообщение в формате:\n' \
                   '<имя валюты>, цену которой вы хотите узнать> ' \
                   '<имя валюты, в которой надо узнать цену первой валюты> ' \
                   '<количество первой валюты>'
    bot.send_message(message.chat.id, instructions)

@bot.message_handler(commands=['values'])
def send_available_currencies(message):
    currencies = 'Доступные валюты:\n' \
                 'Евро - EUR\n' \
                 'Доллар - USD\n' \
                 'Рубль - RUB'
    bot.send_message(message.chat.id, currencies)

@bot.message_handler(func=lambda message: True)
def get_currency_price(message):
    try:
        base, quote, amount = message.text.split(' ')
        price = Converter.get_price(base, quote, amount)
        response = f'{amount} {base} = {price} {quote}'
    except APIException as e:
        response = f'Ошибка: {str(e)}'
    except Exception as e:
        response = f'Произошла ошибка: {str(e)}'

    bot.send_message(message.chat.id, response)

bot.polling()
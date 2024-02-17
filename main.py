import requests
from datetime import datetime as dt
import smtplib
import keys


STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_ENDPOINT = "https://www.alphavantage.co/query"  # ?function=TIME_SERIES_DAILY&symbol=IBM&apikey=5AQY5ICD0TVN0H6E"
STOCK_API_KEY = keys.stock_api_key

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = keys.news_api_key

my_email = keys.my_email
password = keys.password

now = str(dt.today())
todays_date = now[0:10]


def closing_prices():
    stock_parameters = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK,
        "outputsize": "compact",
        "datatype": "json",
        "apikey": STOCK_API_KEY,
    }

    # Gets data from api
    response = requests.get(url=STOCK_ENDPOINT, params=stock_parameters)
    response.raise_for_status()
    data = response.json()

    # Access dicts of data from yesterday and the day before
    dates = list(data["Time Series (Daily)"].keys())
    yesterday, day_before = dates[0], dates[1]

    # Creating two variables that store only the closing cost from yesterday and the day before
    yesterday_closing = data["Time Series (Daily)"][yesterday]["4. close"]
    day_before_closing = data["Time Series (Daily)"][day_before]["4. close"]

    difference = round((float(yesterday_closing) - float(day_before_closing)) / float(day_before_closing), 2) * 100
    return difference


def get_news():
    news_parameters = {
        "q": "tesla",
        "sortBy": "publishedAt",
        "apiKey": "41368f626e514454b8b7b5c45876f349",
        "language": "en",
    }

    response = requests.get(url=NEWS_ENDPOINT, params=news_parameters)
    response.raise_for_status()
    data = response.json()

    title_1, title_2, title_3 = [data["articles"][n]["title"] for n in range(3)]
    descr_1, descr_2, descr_3 = [data["articles"][n]["description"] for n in range(3)]
    return [title_1, descr_1], [title_2, descr_2,], [title_3, descr_3]


def send_message(msg):
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=my_email, password=password)
        connection.sendmail(
            from_addr=my_email,
            to_addrs=keys.recipient,
            msg=msg,

        )


# # Temp code when I can't use stocks api. Can only make request to api 25 times per day.
# yesterday_closing = 250
# day_before_closing = 190
# difference = round((yesterday_closing - day_before_closing) / day_before_closing, 3) * 100


# Use this 👇 variable when able to access ap 
difference = closing_prices()
article_1 = get_news()[0]
article_2 = get_news()[1]
article_3 = get_news()[2]

if difference >= 5.0:
    send_message(f"Subject: TSLA UP {difference}%\n\n{
                 article_1[0].encode('utf8')}\n\nBrief: {article_1[1].encode('utf8')}")
    send_message(f"Subject: TSLA UP {difference}%\n\n{
                 article_2[0].encode('utf8')}\n\nBrief: {article_2[1].encode('utf8')}")
    send_message(f"Subject: TSLA UP {difference}%\n\n{
                 article_3[0].encode('utf8')}\n\nBrief: {article_3[1].encode('utf8')}")
elif difference <= - 5.0:
    send_message(f"Subject: TSLA Down {difference}%\n\n{
                 article_1[0].encode('utf8')}\n\nBrief: {article_1[1].encode('utf8')}")
    send_message(f"Subject: TSLA Down {difference}%\n\n{
                 article_2[0].encode('utf8')}\n\nBrief: {article_2[1].encode('utf8')}")
    send_message(f"Subject: TSLA Down {difference}%\n\n{
                 article_3[0].encode('utf8')}\n\nBrief: {article_3[1].encode('utf8')}")
else:
    print("no news", difference)

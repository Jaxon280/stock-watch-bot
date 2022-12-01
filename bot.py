from slack_sdk import WebClient
from flask import Flask, Response
from slackeventsapi import SlackEventAdapter
import datetime as dt
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
import json

# TEST
SLACK_TOKEN = "xoxb-379072713731-4445621711619-MoKkPYVMRlDzN9hOHhpNCQ5w"
SIGNING_SECRET = "415230efee75436a600da437593e0d8d"

# PRODUCTION
# SLACK_TOKEN = ""
# SIGNING_SECRET = "788e43a58928b68ba0fa5f6e1ddaff65"

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(SIGNING_SECRET, '/slack/event', app)

client = WebClient(token=SLACK_TOKEN)

groups = []

class Stock:
  def __init__(self, ticker, name, kabutan_url):
    self.ticker = ticker
    self.name = name
    self.kabutan_url = kabutan_url

class Group:
  def getMembers(self):
    return self.members

  def getStocks(self):
    return self.stocks

  def addStock(self, stock):
    self.stocks.append(stock)

  # def removeStock(self, stock):
    # self.stocks.

  def changeChannel(self, channel):
    self.channel = channel

  def __init__(self, name, members, channel):
    self.name = name
    self.members = members
    self.channel = channel
    stocks = []

def chatMessage(channel_id, msg):
  client.chat_postMessage(channel = channel_id, text = msg)

def chatErrorMessage(channel_id, msg):
  client.chat_postMessage(channel = channel_id, text = msg)

@slack_event_adapter.on('app_mention')
def message(payload):
  event = payload.get('event', {})
  channel_id = event.get('channel')
  user_id = event.get('user')
  text = event.get('text')

  words = text.split()
  if len(words) <= 1:
    chatErrorMessage(channel_id, "コマンドを入力してください。コマンドがわからない時は @株Watcher help と入力してください。")
    return Response(response=json.dumps({'message': 'OK'}), status=200)

  if words[1] == 'add-group':
    # Group newGroup();
    # groups.append()
    print("not yet")
  elif words[1] == 'kabuka':
    ticker = words[2] + ".JP"
    end = dt.date.today()
    start = str(end.year) + "-01-01"
    df = web.DataReader(ticker, data_source='stooq', start=start, end = end)
    plt.title(ticker + ' Stock price (' + str(start) + " - " + str(end) + 'まで)')
    plt.fill_between(df.index, df['Low'], df['High'], color="b", alpha=0.2)
    df['Open'].plot()
    filename = "kabuka_" + ticker + ".png"
    plt.savefig(filename, format="png", dpi=300)
    plt.show()
    response = client.files_upload(file = '/home/vagrant/development/stock-watcher/' + filename, initial_comment="今年の株価のグラフです", channels = channel_id)
  elif words[1][:7] == 'kabuka-':
    ticker = words[2] + ".JP"
    wordss = words[1].split("-")
    num, unit = int(wordss[1]), wordss[2]
    end = dt.date.today()
    start = dt.date.today()
    if unit == 'day' or unit == 'days':
      start = end - relativedelta(days = num)
    elif unit == 'week' or unit == 'weeks':
      start = end - relativedelta(days = num * 7)
    elif unit == 'month' or unit == 'months':
      start = end - relativedelta(months = num)
    elif unit == 'year' or unit == 'years':
      start = end - relativedelta(years = num)
    print(start)

    df = web.DataReader(ticker, data_source='stooq', start=start, end = end)
    plt.title(ticker + ' Stock price (' + str(start) + " - " + str(end) + 'まで)')
    plt.fill_between(df.index, df['Low'], df['High'], color="b", alpha=0.2)
    df['Open'].plot()
    filename = "kabuka_" + ticker + ".png"
    plt.savefig(filename, format="png", dpi=300)
    plt.show()
    response = client.files_upload(file = '/home/vagrant/development/stock-watcher/' + filename, initial_comment="株価のグラフです", channels = channel_id)
  elif words[1] == 'help':
    helpMessage = """
~~~ 基本的な使い方 ~~~
*この bot をメンションした後に改行せずにコマンドを入力してください。* 例えば、ウォッチする銘柄を追加したければ `@sss` add-stock と Slack で書き込んでください。

~~~ 機能の例 (メンションは省略) ~~~

*グループ関連*
- グループを追加する -> `add-group`
- グループを編集する -> `edit-group`
- 自分のグループ全員にメンションする -> `mention-group`
- グループを削除する -> `delete-group`

*銘柄ウォッチ*
- 自分のグループがウォッチする銘柄を追加する -> `add-stock`
- 自分のグループがウォッチしている銘柄の一覧を見る -> `list-stocks`
- 自分のグループがウォッチする銘柄を削除する -> `delete-stock`
- 自分のグループがウォッチする銘柄の詳細を編集する -> `edit-stock`

*その他便利機能*
- ソフトバンク (9434) の株価グラフを表示する -> `kabuka 9434`
- ソフトバンク (9434) の5日間の株価グラフを表示する -> `kabuka-5-day 9434`
  - 1年の場合は `kabuka-1year`, 1日の場合は `kabuka-1-day`, 1週間の場合は `kabuka-1-week`, 2ヶ月の場合は `kabuka-2-month`
- ソフトバンク (9434) の最近の IR ニュースを取得 -> `ir-news 9434`
    """
    chatMessage(channel_id, helpMessage)

  return Response(response=json.dumps({'message': 'OK'}), status=200)

if __name__ == '__main__':
  app.run(debug=True)

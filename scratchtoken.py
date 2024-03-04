import json
import os
from datetime import datetime
from dotenv import load_dotenv
import scratchattach as scratch3

os.system("pip install -r requirements.txt")

load_dotenv()

DEFAULT_BALANCE = 150
DAILY_CLAIM_AMOUNT = 10
BANDICOIN_DATA_FILE = 'bandicoin_data.json'

session = scratch3.Session(
    os.environ["SESSION_ID"], username="crashbandicootsthe1")
conn = session.connect_cloud(956578973)
client = scratch3.CloudRequests(conn)


def load_bandicoin_data():
    if os.path.exists(BANDICOIN_DATA_FILE):
        with open(BANDICOIN_DATA_FILE, 'r') as file:
            return json.load(file)
    return {}


def save_bandicoin_data(data):
    with open(BANDICOIN_DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)


@client.request
def save_as_owner(data):
    if session.get_linked_user() == "crashbandicootsthe1":
        with open(BANDICOIN_DATA_FILE, 'w') as file:
            json.dump(data, file, indent=4)


def get_balance(account_id):
    bandicoin_data = load_bandicoin_data()
    if account_id or account_id['balance'] not in bandicoin_data:
        today_date = datetime.utcnow().strftime('%m/%d/%Y')
        bandicoin_data[account_id] = {
            'balance': DEFAULT_BALANCE, 'last_claim_date': today_date}
        save_bandicoin_data(bandicoin_data)
    return bandicoin_data.get(account_id, {}).get('balance')


def update_balance(account_id, amount):
    bandicoin_data = load_bandicoin_data()
    if account_id in bandicoin_data:
        bandicoin_data[account_id]['balance'] = bandicoin_data[account_id].get(
            'balance', DEFAULT_BALANCE) + amount
    else:
        bandicoin_data[account_id] = {'balance': DEFAULT_BALANCE + amount}
    save_bandicoin_data(bandicoin_data)


def can_claim_daily(account_id):
    bandicoin_data = load_bandicoin_data()
    last_claim_date = bandicoin_data.get(account_id, {}).get('last_claim_date')
    if not last_claim_date:
        return True
    last_claim_datetime = datetime.strptime(last_claim_date, '%m/%d/%Y')
    today = datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0)
    return last_claim_datetime < today


def set_last_claim(account_id):
    bandicoin_data = load_bandicoin_data()
    bandicoin_data[account_id] = {
        'last_claim_date': datetime.datetime.now().strftime('%m/%d/%Y')}
    save_bandicoin_data(bandicoin_data)


@client.request
def view_bandicoin_amount(account_id):
    print("Requested balance for", account_id)
    return get_balance(account_id)


@client.request
def give_bandicoins(receiver_id, bandicoin_amount):
    sender_id = session.get_linked_user()
    sender_balance = get_balance(sender_id)
    if sender_balance >= bandicoin_amount:
        update_balance(sender_id, -bandicoin_amount)
        update_balance(receiver_id, bandicoin_amount)
        return "1"
    return "0"


@client.request
def get_leaderboard():
    bandicoin_data = load_bandicoin_data()
    sorted_users = sorted(bandicoin_data.items(),
                          key=lambda x: x[1]['balance'], reverse=True)

    leaderboard = []
    for i, (username, data) in enumerate(sorted_users[:10], start=1):
        entry = f"{i}. {username} | {data['balance']}"
        leaderboard.append(entry)

    return leaderboard


@client.request
def claim_daily_bandicoins(account_id):
    if can_claim_daily(account_id) is True:
        update_balance(account_id, DAILY_CLAIM_AMOUNT)
        set_last_claim(account_id)
        return "Claimed! Come back tomorrow!"
    else:
        return "Wait until tomorrow!"


@client.event
def on_ready():
    print("Request handler is running!")


client.run(data_from_websocket=True)

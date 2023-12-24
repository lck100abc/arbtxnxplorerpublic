import telepot
import requests
import time

# Replace with your Telegram Bot Token
BOT_TOKEN = '6443113559:AAFfrKdx-6IS59WqcW1xwyToBUVl41wJ0fQ'

# Define the chat ID where you want to send notifications
CHAT_ID = '6613211769'

# Arbiscan API Key
API_KEY = 'P8EEKQACC7ZPSBAG1WQKWCK8EAK7ZGQ8IA'

# Arbiscan API URL
API_URL = 'https://api.arbiscan.io/api'

# Dictionary to store the last checked block number for each wallet address
last_checked_blocks = {}


def get_current_block_number():
  params = {'module': 'proxy', 'action': 'eth_blockNumber', 'apikey': API_KEY}
  response = requests.get(API_URL, params=params)
  if response.status_code == 200:
    current_block = int(response.json().get('result', '0x0'), 16)
    return current_block
  else:
    return None


def get_latest_token_transfer(
    address, contract_address='0xda10009cbd5d07dd0cecc66161fc93d7c9000da1'):
  params = {
      'module': 'account',
      'action': 'tokentx',
      'contractaddress': contract_address,
      'address': address,
      'page': 1,
      'offset': 1,
      'startblock': last_checked_blocks.get(address, 0) + 1,
      'endblock': 'latest',
      'sort': 'asc',
      'apikey': API_KEY
  }
  response = requests.get(API_URL, params=params)
  if response.status_code == 200:
    result = response.json().get('result', [])
    if result:
      return result[0]
    else:
      return None
  else:
    return None


def get_token_balance(address, contract_address):
  params = {
      'module': 'account',
      'action': 'tokenbalance',
      'contractaddress': contract_address,
      'address': address,
      'tag': 'latest',
      'apikey': API_KEY
  }
  response = requests.get(API_URL, params=params)
  if response.status_code == 200:
    balance = response.json().get('result', '0')
    return balance
  else:
    return None


# Initialize the bot
bot = telepot.Bot(BOT_TOKEN)


def send_notification(chat_id, message):
  bot.sendMessage(chat_id, message, parse_mode="Markdown")


def monitor_wallet_addresses():
    wallet_addresses = [
        "0xFf3fe26386720B8475058DE12E1f7B8c5E41e9a4",
        "0xd1592F72b32537e470c4B38e708C3aF0832868EB",
        "0xa322075bE559eD4b7Cc1e391f6CE8F2E77e426fe",
        "0x38760f194a4303a9D7297b149E066D3c8E024745",
        "0x2bF3388F8CE63B822e7C9aBB423547E4E7b7f455",
        "0x0268C6b26a9148c25118aa462E5658f668C821F3",
        "0x7d2cf30b4506737864ce3e859928c3fec9d92fcB",
        "0x563159DeBcA67F15273E85EF556d27DB5E5c109d",
        "0x7d2cf30b4506737864ce3e859928c3fec9d92fcB",
        "0xD7ae7f0A87780c5Cf2962a6A878E0F557f56e0BA",
        "0xD39680FDFb7EDFF248484f905aB6860cB64d77cf",
        "0x898FDfd721F70335543A0122a9C6F0Cc05E6a0B5",
        "0xA32620A5647Ac4C38215fE037B98289F802A43f4",
        "0xbB140cAad2A312DCB2d1EAEC02BB11b35816D39d",
        "0xF8c9247484b6Fc68bf0C4f75934138f37439147B",
        "0x858da48232eA6731f22573Dc711c0cC415c334C5",
        "0x858da48232eA6731f22573Dc711c0cC415c334C5",
        "0x00336cD9F823dd8B5C5741638E5038FD561F01B9",
        "0x435FcbC37C499cb8197df2D843e7c21d2E77CAbf"
    ]

  current_block = get_current_block_number()
  if current_block:
    for address in wallet_addresses:
      last_checked_blocks[address] = current_block

  while True:
    for address in wallet_addresses:
      latest_tx = get_latest_token_transfer(address)
      if latest_tx:
        if address not in last_checked_blocks or int(
            latest_tx['blockNumber']) > last_checked_blocks[address]:
          token_name = latest_tx.get('tokenName', 'Unknown Token')
          value = latest_tx.get('value', 'N/A')
          token_symbol = latest_tx.get('tokenSymbol', 'N/A')
          contract_address = latest_tx.get('contractAddress', 'N/A')
          balance = get_token_balance(address, contract_address)
          direction = 'Received' if address.lower() == latest_tx.get(
              'to', '').lower() else 'Sent'

          message = (
              f"🚀 *New Arbiscan Transaction* 🚀\n\n"
              f"🔹 *Address*: [{address}](https://arbiscan.io/address/{address})\n"
              f"🔹 *Direction*: {direction}\n"
              f"🔹 *Token*: {token_name} ({token_symbol})\n"
              f"🔹 *Value*: {value}\n"
              f"🔹 *Balance*: {balance}\n"
              f"🔹 *Block Number*: {latest_tx['blockNumber']}\n")
          send_notification(CHAT_ID, message)

          last_checked_blocks[address] = int(latest_tx['blockNumber'])
    time.sleep(30)


if __name__ == '__main__':
  monitor_wallet_addresses()

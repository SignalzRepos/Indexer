import os

from dotenv import load_dotenv
from web3 import Web3, WebsocketProvider

load_dotenv()

alchemy_url = os.getenv("ALCHEMY_URL")

assert alchemy_url is not None

w3 = Web3(WebsocketProvider(alchemy_url))

print(w3.isConnected())

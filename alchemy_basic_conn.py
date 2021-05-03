import os

from dotenv import load_dotenv
from web3 import Web3, WebsocketProvider


def setup_conn() -> Web3:
    load_dotenv()
    alchemy_url = os.getenv("ALCHEMY_URL")

    assert alchemy_url is not None

    w3 = Web3(WebsocketProvider(alchemy_url))

    return w3


if __name__ == "__main__":
    w3 = setup_conn()

    print(f"Connection successful: {w3.isConnected()}")

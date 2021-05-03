import os
from pathlib import Path

import requests
from dotenv import load_dotenv

from alchemy_basic_conn import get_alchemy_conn

load_dotenv()

CONTRACT_ADDRESS = "0x06012c8cf97BEaD5deAe237070F9587f8E7A266d"
abi_filename = "crypto_kitties_abi.txt"


def print_cryptokitties_the_difficult_way():
    abi = Path(abi_filename).read_text().strip()
    w3 = get_alchemy_conn()

    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

    print(f"Contract Name: {contract.functions.name().call()}")


def get_k_latest_approved_transaction(k=10):
    etherscan_api_url = 'https://api.etherscan.io/api'
    api_key = os.getenv('ETHERSCAN_API_KEY')

    if api_key is None:
        print("You should add ETHERSCAN_API_KEY to the .env file, or set it as shell env var")

    w3 = get_alchemy_conn()

    print("Fetching latest block")
    latest_block_num: int = w3.eth.get_block("latest").number
    print(f"Latest block num -> {latest_block_num}")

    params = {'module': 'account', 'action': 'txlist', 'address': CONTRACT_ADDRESS, 'startblock': 0,
              'endblock': latest_block_num, 'page': 1, 'offset': k, 'apikey': api_key}

    resp = requests.get(etherscan_api_url, params=params)

    if not resp.ok:
        print("Failed while fetching the transaction list for cryptokitties")

    data = resp.json()
    tx_list = data.get('result')

    if tx_list is None:
        print("Seems like we have the wrong response from the tx_list request")

    tx_hashes = [tx.get('hash') for tx in tx_list]

    return tx_hashes


if __name__ == "__main__":
    # print_cryptokitties_the_difficult_way()

    print(get_k_latest_approved_transaction(5))

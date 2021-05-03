import os
from pathlib import Path
from typing import List

import requests
from dotenv import load_dotenv
from web3.datastructures import AttributeDict

from alchemy_basic_conn import get_alchemy_conn

load_dotenv()

CONTRACT_ADDRESS = "0x06012c8cf97BEaD5deAe237070F9587f8E7A266d"
abi_filename = "crypto_kitties_abi.txt"
ERROR_CLR = '\033[91m'
END_CLR = '\033[0m'


def print_error(msg: str) -> None:
    print(f"{ERROR_CLR}{msg}{END_CLR}")


def print_cryptokitties_the_difficult_way()->None:
    abi = Path(abi_filename).read_text().strip()
    w3 = get_alchemy_conn()

    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

    print(f"Contract Name: {contract.functions.name().call()}")


def get_k_latest_approved_transaction(k=10) -> List[str]:
    etherscan_api_url = "https://api.etherscan.io/api"
    api_key = os.getenv("ETHERSCAN_API_KEY")

    if api_key is None:
        print_error(
            "You should add ETHERSCAN_API_KEY to the .env file, or set it as shell env var"
        )
        exit(1)

    w3 = get_alchemy_conn()

    print("Fetching latest block")
    latest_block_num: int = w3.eth.get_block("latest").number
    print(f"Latest block num -> {latest_block_num}")

    params = {
        "module": "account",
        "action": "txlist",
        "address": CONTRACT_ADDRESS,
        "startblock": 0,
        "endblock": latest_block_num,
        "page": 1,
        "offset": k,
        "apikey": api_key,
    }

    print("Fetching transaction list for cryptokitties")
    resp = requests.get(etherscan_api_url, params=params)

    if not resp.ok:
        print_error("Failed while fetching the transaction list for cryptokitties")

    data = resp.json()
    tx_list = data.get("result")

    if tx_list is None:
        print_error("Seems like we have the wrong response from the tx_list request")

    tx_hashes = [tx.get("hash") for tx in tx_list]

    return tx_hashes


def get_crypto_kitty_logs(k=5):
    w3 = get_alchemy_conn()
    tx_list = get_k_latest_approved_transaction(k)

    print("Fetching transactions receipts")
    tx_receipts: List[AttributeDict] = [
        w3.eth.get_transaction_receipt(tx_hash) for tx_hash in tx_list
    ]

    tx_logs: List[AttributeDict] = [tx["logs"] for tx in tx_receipts]

    return tx_logs


if __name__ == "__main__":
    from pprint import pprint

    # print_cryptokitties_the_difficult_way()
    # pprint(get_k_latest_approved_transaction(5))

    pprint(get_crypto_kitty_logs(5))

import json
import logging
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import List

from web3 import Web3
from web3.contract import AttributeDict, Contract, LogFilter, LogReceipt

from alchemy_basic_conn import setup_conn


@lru_cache(maxsize=1)
def get_web3() -> Web3:
    return setup_conn()


abi = Path("./uniswapv2pair.abi.txt").read_text()
contract_address = (
    "0x7885e359a085372EbCF1ed6829402f149D02c600"  # LuaSwap LP Token V1 Swap Contract
)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)


@dataclass
class SwapEventLog:
    block: int
    transaction: str
    log_idx: int
    sender: str
    receiver: str
    amnt_0_in: int = 0
    amnt_1_in: int = 0
    amnt_0_out: int = 0
    amnt_1_out: int = 0


def get_swap_events(
    from_block: int, to_block: int, contract: Contract
) -> List[LogReceipt]:
    swap_filter: LogFilter = contract.events.Swap.createFilter(
        fromBlock=from_block, toBlock=to_block
    )
    entries = swap_filter.get_all_entries()

    get_web3().eth.uninstall_filter(swap_filter.filter_id)

    return entries


def parse_swap_event_log(lr: LogReceipt) -> SwapEventLog:
    block_num = lr["blockNumber"]
    log_idx = lr["logIndex"]
    transaction = lr["transactionHash"].hex()
    args: AttributeDict = lr["args"]

    return SwapEventLog(
        block_num,
        transaction,
        log_idx,
        sender=args.get("sender"),
        receiver=args.get("to"),
        amnt_0_in=args.get("amount0In"),
        amnt_1_in=args.get("amount1In"),
        amnt_0_out=args.get("amount0Out"),
        amnt_1_out=args.get("amount1Out"),
    )


def print_swap_log(log: SwapEventLog):
    print(f"Block Number: {log.block}\t\t\tTransaction: {log.transaction}")
    print(f"From: {log.sender}\tTo: {log.receiver}")
    print(f"Amount0In: {log.amnt_0_in}\tAmount0Out: {log.amnt_0_out}")
    print(f"Amount1In: {log.amnt_1_in}\tAmount1Out: {log.amnt_1_out}")
    print("-" * 79)


def save_swap_events_to_json(logs: List[SwapEventLog], file_pth: Path):
    logs_as_dict = [log.__dict__ for log in logs]
    with file_pth.open("w") as f:
        json.dump(logs_as_dict, f, indent=4, sort_keys=True)


def load_swap_event_json(file_pth: Path) -> List[SwapEventLog]:
    with file_pth.open("r") as f:
        logs_as_dict = json.load(f)

    return [SwapEventLog(**le) for le in logs_as_dict]


def main():
    w3 = get_web3()

    contract = w3.eth.contract(address=contract_address, abi=abi)

    logging.info("Getting latest block")
    latest_block = w3.eth.get_block("latest")
    latest_block_num: int = latest_block.number
    logging.info(f"Latest block number: {latest_block}")
    print("-" * 79)

    swap_events = []
    step = 100
    # start = 11149596  # first block with transaction for this contract - Etherscan
    start = latest_block_num - 10_000

    for i in range(start, latest_block_num + 1, step):
        logging.info(f"Getting events for block {i} -> {i + step}")
        events = get_swap_events(i, i + step, contract)
        swap_events.extend(events)
        time.sleep(0.01)

    logging.info(f"Total swap events : {len(swap_events)}")
    logging.info("Converting raw swap events to SwapEventLog list")
    swap_event_logs = [parse_swap_event_log(lr) for lr in swap_events]

    logging.info("Printing all events...")
    for swap_log in swap_event_logs:
        print_swap_log(swap_log)

    json_file_pth = Path(f"./swap_logs_{start}_to_{latest_block_num}.json")
    print("\n\n")
    logging.info(f"Saving logs to {json_file_pth}")
    save_swap_events_to_json(swap_event_logs, json_file_pth)
    logging.info("All done...")


if __name__ == "__main__":
    main()

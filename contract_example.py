from pathlib import Path
from typing import Union

from solcx import compile_source
from web3 import Web3


def compile_source_file(f_pth: Union[str, Path]):
    file_pth = Path(f_pth)
    source = file_pth.read_text()

    return compile_source(source)


def deploy_contract(w3: Web3, contract_interface) -> str:
    contract = w3.eth.contract(
        abi=contract_interface["abi"], bytecode=contract_interface["bin"]
    )

    tx_hash = contract.constructor().transact()
    addr = w3.eth.get_transaction_receipt(tx_hash)["contractAddress"]

    return addr


if __name__ == "__main__":
    import pprint

    from eth_tester import PyEVMBackend
    from web3.providers.eth_tester import EthereumTesterProvider

    compiled_source = compile_source_file("contract.sol")
    contract_id, contract_interface = compiled_source.popitem()
    gas_threshold = 100_000

    w3 = Web3(EthereumTesterProvider(PyEVMBackend()))

    addr = deploy_contract(w3, contract_interface)

    print(f"Deployed {contract_id} to : {addr}\n")

    store_var_contract = w3.eth.contract(address=addr, abi=contract_interface["abi"])

    gas_estimate = store_var_contract.functions.setVar(255).estimateGas()
    print(f"Estimated gas usage to transact with setVar: {gas_estimate}")

    if gas_estimate < gas_threshold:
        print("Sending transaction to setVar(255)\n")

        tx_hash = store_var_contract.functions.setVar(255).transact()
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        print("Transaction receipt mined: ")
        pprint.pp(dict(tx_receipt))

        print("\nWas transaction successful?")
        pprint.pp(tx_receipt["status"])
    else:
        print(f"Gas cost exceeds the threshold: [{gas_threshold}]")

from typing import Union
from fastapi import FastAPI
from web3 import Web3, AsyncWeb3
from eth_account import Account

from dotenv import load_dotenv
import os
import json

app = FastAPI()


load_dotenv(".env")

@app.get("/decimals/")
def read_root():
    w3 = Web3(Web3.HTTPProvider(os.environ.get("PROVIDER_URL")))
    contract_address = os.environ.get("CONTRACT_ADDRESS")

    with open("./assets/abi/sample.json") as f:
        abi = json.load(f)["result"]

    contrtact = w3.eth.contract(address=contract_address, abi=abi)
    result = contrtact.functions.decimals().call()

    return {"result": result}

@app.get("/name/")
def read_root():
    w3 = Web3(Web3.HTTPProvider(os.environ.get("PROVIDER_URL")))
    contract_address = os.environ.get("CONTRACT_ADDRESS")

    with open("./assets/abi/sample.json") as f:
        abi = json.load(f)["result"]

    contrtact = w3.eth.contract(address=contract_address, abi=abi)
    result = contrtact.functions.name().call()

    return {"result": result}

@app.post("/mint/")
def read_root():
    w3 = Web3(Web3.HTTPProvider(os.environ.get("PROVIDER_URL")))
    contract_address = os.environ.get("CONTRACT_ADDRESS")
    private_key = os.environ.get("PRIVATE_KEY")

    with open("./assets/abi/sample.json") as f:
        abi = json.load(f)["result"]

    contrtact = w3.eth.contract(address=contract_address, abi=abi)
    nonce = w3.eth.get_transaction_count(w3.to_checksum_address(os.environ.get("MINTER_ADDRESS")))

    from_address = Account.from_key(private_key).address
    print(from_address)

    transaction = {
        'from': from_address,
        'value': 100000000000000,
        'nonce': nonce,
    }

    print(transaction)

    tx = contrtact.functions.mintWithNativeToken().build_transaction(transaction)

    print("tx:", tx)

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return {"tx_hash": tx_hash.hex()}
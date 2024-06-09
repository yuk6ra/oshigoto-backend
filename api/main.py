from typing import Union
from fastapi import FastAPI
from web3 import Web3, AsyncWeb3
from eth_account import Account

from dotenv import load_dotenv
import os
import json

app = FastAPI()


load_dotenv()

CHAIN_ID = int(os.environ.get("CHAIN_ID"))

@app.get("/decimals/")
def read_root():
    w3 = Web3(Web3.HTTPProvider(os.environ.get("PROVIDER_URL")))
    contract_address = os.environ.get("CONTRACT_ADDRESS_OSHIGOTO_TOKEN")

    with open("./assets/abi/sample.json") as f:
        abi = json.load(f)["result"]

    contrtact = w3.eth.contract(address=contract_address, abi=abi)
    result = contrtact.functions.decimals().call()

    return {"result": result}

@app.get("/name/")
def read_root():
    w3 = Web3(Web3.HTTPProvider(os.environ.get("PROVIDER_URL")))
    contract_address = os.environ.get("CONTRACT_ADDRESS_OSHIGOTO_TOKEN")

    with open("./assets/abi/sample.json") as f:
        abi = json.load(f)["result"]

    contrtact = w3.eth.contract(address=contract_address, abi=abi)
    result = contrtact.functions.name().call()

    return {"result": result}

@app.get("/totalsupply/")
def read_root():
    w3 = Web3(Web3.HTTPProvider(os.environ.get("PROVIDER_URL")))
    contract_address = os.environ.get("CONTRACT_ADDRESS_OSHIGOTO_TOKEN")

    with open("./assets/abi/sample.json") as f:
        abi = json.load(f)["result"]

    contrtact = w3.eth.contract(address=contract_address, abi=abi)
    result = contrtact.functions.totalSupply().call()

    return {"result": result}

@app.post("/mint/oshigototoken/native/")
def read_root():   
    w3 = Web3(Web3.HTTPProvider(os.environ.get("PROVIDER_URL")))
    contract_address = os.environ.get("CONTRACT_ADDRESS_OSHIGOTO_TOKEN")
    private_key = os.environ.get("PRIVATE_KEY")

    with open("./assets/abi/sample.json") as f:
        abi = json.load(f)["result"]

    contrtact = w3.eth.contract(address=contract_address, abi=abi)
    nonce = w3.eth.get_transaction_count(w3.to_checksum_address(os.environ.get("MINTER_ADDRESS")))

    from_address = Account.from_key(private_key).address

    transaction = {
        'from': from_address,
        'value': 100000000000000,
        'nonce': nonce,
    }

    tx = contrtact.functions.mintWithNativeToken().build_transaction(transaction)
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return {"tx_hash": tx_hash.hex()}

@app.post("/mint/oshigototoken/erc20/")
def read_root():
    w3 = Web3(Web3.HTTPProvider(os.environ.get("PROVIDER_URL")))
    contract_address = os.environ.get("CONTRACT_ADDRESS_OSHIGOTO_TOKEN")
    private_key = os.environ.get("PRIVATE_KEY")

    with open("./assets/abi/sample.json") as f:
        abi = json.load(f)["result"]

    contrtact = w3.eth.contract(address=contract_address, abi=abi)
    nonce = w3.eth.get_transaction_count(w3.to_checksum_address(os.environ.get("MINTER_ADDRESS")))

    from_address = Account.from_key(private_key).address

    transaction = {
        'from': from_address,
        'nonce': nonce,
    }

    tx = contrtact.functions.mintWithERC20Token().build_transaction(transaction)
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return {"tx_hash": tx_hash.hex()}

@app.post("/mint/checkcoin/")
def mint_coin(value: int):
    w3 = Web3(Web3.HTTPProvider(os.environ.get("PROVIDER_URL")))
    contract_address = os.environ.get("CONTRACT_ADDRESS_CHECK_COIN")
    private_key = os.environ.get("PRIVATE_KEY")

    with open("./assets/abi/erc20.json") as f:
        abi = json.load(f)["result"]

    contrtact = w3.eth.contract(address=contract_address, abi=abi)
    nonce = w3.eth.get_transaction_count(w3.to_checksum_address(os.environ.get("MINTER_ADDRESS")))

    from_address = Account.from_key(private_key).address

    transaction = {
        'from': from_address,
        'nonce': nonce,
    }

    tx = contrtact.functions.mint(from_address, value).build_transaction(transaction)
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return {"tx_hash": tx_hash.hex()}

@app.get("/main_wallet/status")
def read_wallet():
    w3 = Web3(Web3.HTTPProvider(os.environ.get("PROVIDER_URL")))
    checkcoin_contract_address = os.environ.get("CONTRACT_ADDRESS_CHECK_COIN")
    target_address = Account.from_key(os.environ.get("PRIVATE_KEY")).address

    with open("./assets/abi/erc20.json") as f:
        abi = json.load(f)["result"]

    checkcoin_contrtact = w3.eth.contract(address=checkcoin_contract_address, abi=abi)
    erc20 = checkcoin_contrtact.functions.balanceOf(target_address).call()
    erc20_balance = int(erc20) / 10**18
    native = w3.eth.get_balance(target_address)
    native_balance = int(native) / 10**18

    with open("./assets/abi/sample.json") as f:
        abi = json.load(f)["result"]
    
    oshigoto_contract_address = os.environ.get("CONTRACT_ADDRESS_OSHIGOTO_TOKEN")
    oshigoto_contract = w3.eth.contract(address=oshigoto_contract_address, abi=abi)
    oshigoto = oshigoto_contract.functions.balanceOf(target_address).call()
    oshigoto_balance = int(oshigoto) / 10**18

    return {
        "native_token": native_balance,
        "check_coin": erc20_balance,
        "oshigoto_token": oshigoto_balance
    }

@app.post("/memberships/alice")
def mint_memberships():
    w3 = Web3(Web3.HTTPProvider(os.environ.get("PROVIDER_URL")))
    contract_address = os.environ.get("CONTRACT_ADDRESS_ALICE_MEMBERSHIP")

    private_key = os.environ.get("PRIVATE_KEY")

    with open("./assets/abi/membership.json") as f:
        abi = json.load(f)["result"]

    contract = w3.eth.contract(address=contract_address, abi=abi)
    account = Account.from_key(private_key)
    from_address = w3.to_checksum_address(account.address)
    nonce = w3.eth.get_transaction_count(from_address)

    transaction = contract.functions.mintMembership().build_transaction({
        'gas': 200000,  # Estimate gas limit
        'gasPrice': w3.to_wei('10', 'gwei'),  # Estimate gas price
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    return {
        "from": from_address,
        "tx_hash": tx_hash.hex(),
    }

@app.get("/wallets/")
def read_root(username: str):

    w3 = Web3(Web3.HTTPProvider(os.environ.get("PROVIDER_URL")))
    erc6551_contract_address = os.environ.get("CONTRACT_ADDRESS_ERC6551_REGISTRY")
    minter_address = w3.to_checksum_address(os.environ.get("MINTER_ADDRESS"))
    implement_contract_address = w3.to_checksum_address(os.environ.get("CONTRACT_ADDRESS_ERC6551_IMPLEMENTATION"))

    salt = w3.solidity_keccak(["string"], [username])

    membership_contract_address = w3.to_checksum_address(os.environ.get("CONTRACT_ADDRESS_ALICE_MEMBERSHIP"))

    with open("./assets/abi/membership.json") as f:
        abi = json.load(f)["result"]

    membership_contract = w3.eth.contract(address=membership_contract_address, abi=abi)
    tokenID = membership_contract.functions.getTokenIdFromAddress(minter_address).call()
    print(tokenID)

    with open("./assets/abi/erc6551registry.json") as f:
        abi = json.load(f)["result"]

    contrtact = w3.eth.contract(address=erc6551_contract_address, abi=abi)
    result = contrtact.functions.account(implement_contract_address,salt, CHAIN_ID, membership_contract_address, tokenID).call()
    return {
        "implement_contract_address": implement_contract_address,
        "chain_id": CHAIN_ID,
        "membership_contract_address": membership_contract_address,
        "token_id": tokenID,
        "username": username,
        "salt": salt.hex(),
        "wallet_address": result    
    }
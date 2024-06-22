from typing import Union
from fastapi import FastAPI
from web3 import Web3, AsyncWeb3, contract
from eth_account import Account

from dotenv import load_dotenv
import datetime
import os
import json
import base64

from models.model import MaterialBody

app = FastAPI()
load_dotenv()

CHAIN_ID = int(os.environ.get("CHAIN_ID"))

w3 = Web3(Web3.HTTPProvider(os.environ.get("PROVIDER_URL")))

# Contract address
membership_contract_address = os.environ.get("CONTRACT_ADDRESS_ALICE_MEMBERSHIP")
material_contract_address = os.environ.get("CONTRACT_ADDRESS_MIRROR_NFT")
oshigototoken_contract_address = os.environ.get("CONTRACT_ADDRESS_OSHIGOTO_TOKEN")
checkcoin_contract_address = os.environ.get("CONTRACT_ADDRESS_CHECK_COIN")

# Private key
user_private_key = os.environ.get("PRIVATE_KEY")

def load_contract(address: str, json_filename: str) -> contract.Contract:
    try:
        with open(f"./assets/abi/{json_filename}", 'r') as f:
            abi = json.load(f)["result"]
        return w3.eth.contract(address=address, abi=abi)
    except FileNotFoundError:
        raise FileNotFoundError(f"ABI file {json_filename} not found")
    except json.JSONDecodeError:
        raise ValueError(f"Error decoding ABI file {json_filename}")

contracts = {
    "membership": ("membership.json", membership_contract_address),
    "mirror": ("mirror-nft.json", material_contract_address),
    "oshigoto_token": ("oshigoto-token.json", oshigototoken_contract_address),
    "check_coin": ("erc20.json", checkcoin_contract_address),
    "erc6551_registry": ("erc6551registry.json", os.environ.get("CONTRACT_ADDRESS_ERC6551_REGISTRY")),
}

loaded_contracts = {name: load_contract(addr, json_file) for name, (json_file, addr) in contracts.items()}

@app.post("/oshigototoken/mint/native/")
def mint_oshigototoken():

    user_address = Account.from_key(user_private_key).address
    nonce = w3.eth.get_transaction_count(w3.to_checksum_address(user_address))

    transaction = {
        'from': user_address,
        'value': 100000000000000,
        'nonce': nonce,
    }

    tx = oshigototoken_contrtact.functions.mintWithNativeToken(w3.to_checksum_address(user_address)).build_transaction(transaction)
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=user_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return {"tx_hash": tx_hash.hex()}

@app.post("/oshigototoken/mint/erc20/")
def mint_oshigototoken_by_erc20():
    user_address = Account.from_key(user_private_key).address
    nonce = w3.eth.get_transaction_count(w3.to_checksum_address(user_address))

    transaction = {
        'from': user_address,
        'nonce': nonce,
    }

    tx = oshigototoken_contrtact.functions.mintWithERC20Token(w3.to_checksum_address(user_address)).build_transaction(transaction)
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=user_private_key)
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

    with open("./assets/abi/oshigoto-token.json") as f:
        abi = json.load(f)["result"]
    
    oshigoto_contract_address = os.environ.get("CONTRACT_ADDRESS_OSHIGOTO_TOKEN")
    oshigoto_contract = w3.eth.contract(address=oshigoto_contract_address, abi=abi)
    oshigoto = oshigoto_contract.functions.balanceOf(target_address).call()
    oshigoto_balance = int(oshigoto) / 10**18

    return {
        "native_token": native_balance,
        "check_coin": erc20_balance,
    }


@app.get("/tba_wallets/{wallet_address}")
def read_wallet(wallet_address: str):
    w3 = Web3(Web3.HTTPProvider(os.environ.get("PROVIDER_URL")))
    mirror_contract_address = os.environ.get("CONTRACT_ADDRESS_MIRROR_NFT")

    with open("./assets/abi/mirror-nft.json") as f:
        abi = json.load(f)["result"]
    mirror = w3.eth.contract(address=mirror_contract_address, abi=abi)
    nft_balance = mirror.functions.balanceOf(w3.to_checksum_address(wallet_address)).call()

    with open("./assets/abi/oshigoto-token.json") as f:
        abi = json.load(f)["result"]

    oshigoto_contract_address = os.environ.get("CONTRACT_ADDRESS_OSHIGOTO_TOKEN")
    oshigoto_contract = w3.eth.contract(address=oshigoto_contract_address, abi=abi)
    oshigoto = oshigoto_contract.functions.balanceOf(w3.to_checksum_address(wallet_address)).call()
    oshigoto_balance = int(oshigoto) / 10**18
    
    return {
        "oshigoto_token_erc721": nft_balance,
        "oshigoto_token_erc20": oshigoto_balance,
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
        "tba_wallet_address": result,
        "main_wallet_address": minter_address, 
    }

@app.get("/membership/{token_id}")
def get_membership(token_id: int):
    config = alice_membership_contrtact.functions.membershipConfigs(token_id).call()
    tokenURI = alice_membership_contrtact.functions.tokenURI(token_id).call()

    # base64 -> json
    metadata = json.loads(base64.b64decode(tokenURI.split(",")[1]))

    # unix timestamp to datetime
    last_burned = datetime.datetime.fromtimestamp(config[1])

    return {
        "token_id": token_id,
        "name": metadata["name"],
        "image": metadata["image"],
        "burn_point": config[0],
        "last_burned": last_burned,
    }

@app.post("/memberships/alice")
def mint_memberships():
    account = Account.from_key(user_private_key)
    from_address = w3.to_checksum_address(account.address)
    nonce = w3.eth.get_transaction_count(from_address)

    transaction = alice_membership_contrtact.functions.mintMembership().build_transaction({
        'gas': 200000,  # Estimate gas limit
        'gasPrice': w3.to_wei('10', 'gwei'),  # Estimate gas price
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.sign_transaction(transaction, user_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    return {
        "from": from_address,
        "tx_hash": tx_hash.hex(),
    }

@app.post("/memberships/levelup/{token_id}")
def levelup_memberships(token_id: int, material_body: MaterialBody):
    account = Account.from_key(user_private_key)
    from_address = w3.to_checksum_address(account.address)
    nonce = w3.eth.get_transaction_count(from_address)

    transaction = alice_membership_contrtact.functions.levelUp(
        token_id,
        material_body.material_token_id,
        material_body.material_contract_address,
    ).build_transaction({
        'gas': 200000,  # Estimate gas limit
        'gasPrice': w3.to_wei('10', 'gwei'),  # Estimate gas price
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.sign_transaction(transaction, user_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    return {
        "from": from_address,
        "tx_hash": tx_hash.hex(),
    }
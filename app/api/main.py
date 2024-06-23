from typing import Union
from fastapi import FastAPI
from web3 import Web3, AsyncWeb3, contract
from eth_account import Account

from dotenv import load_dotenv
import datetime
import os
import json
import base64
import re

from models.model import MaterialBody

app = FastAPI()
load_dotenv()

CHAIN_ID = int(os.environ.get("CHAIN_ID"))

w3 = Web3(Web3.HTTPProvider(os.environ.get("PROVIDER_URL")))

# Private key
owner_private_key = os.environ.get("OWNER_PRIVATE_KEY")
owner_address = Account.from_key(owner_private_key).address

user_private_key = os.environ.get("USER_PRIVATE_KEY")
user_address = Account.from_key(user_private_key).address

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
    "check_coin": ("check-coin.json", os.environ.get("CONTRACT_ADDRESS_CHECK_COIN")),
    "erc6551_registry": ("erc6551-registry.json", os.environ.get("CONTRACT_ADDRESS_ERC6551_REGISTRY")),
    "metalive_poap": ("metalive-poap.json", os.environ.get("CONTRACT_ADDRESS_METALIVE_POAP")),
    "mirror_nft": ("mirror-nft.json", os.environ.get("CONTRACT_ADDRESS_MIRROR_NFT")),
    "oshigoto_goods": ("oshigoto-goods.json", os.environ.get("CONTRACT_ADDRESS_OSHIGOTO_GOODS")),
    "oshigoto_membership": ("oshigoto-membership.json", os.environ.get("CONTRACT_ADDRESS_OSHIGOTO_MEMBERSHIP")),
    "oshigoto_token": ("oshigoto-token.json", os.environ.get("CONTRACT_ADDRESS_OSHIGOTO_TOKEN")),
}

loaded_contracts = {name: load_contract(addr, json_file) for name, (json_file, addr) in contracts.items()}

@app.post("/oshigototoken/mint/native/")
def mint_oshigototoken():
    nonce = w3.eth.get_transaction_count(w3.to_checksum_address(user_address))
    transaction = {
        'from': user_address,
        'value': 100000000000000,
        'nonce': nonce,
    }
    oshigototoken_contrtact = loaded_contracts.get("oshigoto_token")

    tx = oshigototoken_contrtact.functions.mintWithNativeToken(w3.to_checksum_address(user_address)).build_transaction(transaction)
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=user_private_key)

    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return {
        "from": user_address,
        "tx_hash": tx_hash.hex(),
    }

@app.post("/oshigototoken/mint/erc20/")
def mint_oshigototoken_by_erc20():
    nonce = w3.eth.get_transaction_count(w3.to_checksum_address(user_address))

    transaction = {
        'from': user_address,
        'nonce': nonce,
    }

    oshigototoken_contrtact = loaded_contracts.get("oshigoto_token")

    tx = oshigototoken_contrtact.functions.mintWithERC20Token(w3.to_checksum_address(user_address)).build_transaction(transaction)
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=user_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return {
        "from": user_address,
        "tx_hash": tx_hash.hex(),
    }

@app.post("/checkcoin/mint/")
def mint_coin(value: int):

    nonce = w3.eth.get_transaction_count(w3.to_checksum_address(user_address))
    transaction = {
        'from': user_address,
        'nonce': nonce,
    }

    checkcoin_contrtact = loaded_contracts.get("check_coin")

    tx = checkcoin_contrtact.functions.mint(user_address, value).build_transaction(transaction)
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=user_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return {"tx_hash": tx_hash.hex()}

@app.get("/main_wallet/status")
def read_wallet():
    checkcoin_contrtact = loaded_contracts.get("check_coin")

    # Check Coin
    checkcoin_balance_of = checkcoin_contrtact.functions.balanceOf(user_address).call()
    checkcoin_balance = int(checkcoin_balance_of) / 10**18

    # Native Token
    native_balance_of = w3.eth.get_balance(user_address)
    native_balance = int(native_balance_of) / 10**18

    return {
        "native_token": native_balance,
        "check_coin": checkcoin_balance,
    }


# @app.get("/tba_wallet/{wallet_address}")
# def read_wallet(wallet_address: str):
#     w3 = Web3(Web3.HTTPProvider(os.environ.get("PROVIDER_URL")))
#     mirror_contract_address = os.environ.get("CONTRACT_ADDRESS_MIRROR_NFT")

#     with open("./assets/abi/mirror-nft.json") as f:
#         abi = json.load(f)["result"]
#     mirror = w3.eth.contract(address=mirror_contract_address, abi=abi)
#     nft_balance = mirror.functions.balanceOf(w3.to_checksum_address(wallet_address)).call()

#     with open("./assets/abi/oshigoto-token.json") as f:
#         abi = json.load(f)["result"]

#     oshigoto_contract_address = os.environ.get("CONTRACT_ADDRESS_OSHIGOTO_TOKEN")
#     oshigoto_contract = w3.eth.contract(address=oshigoto_contract_address, abi=abi)
#     oshigoto = oshigoto_contract.functions.balanceOf(w3.to_checksum_address(wallet_address)).call()
#     oshigoto_balance = int(oshigoto) / 10**18
    
#     return {
#         "oshigoto_token_erc721": nft_balance,
#         "oshigoto_token_erc20": oshigoto_balance,
#     }

@app.get("/wallets/")
def read_root(username: str):
    salt = w3.solidity_keccak(["string"], [username])   

    membership_contract = loaded_contracts.get("oshigoto_membership")
    erc6551_contract = loaded_contracts.get("erc6551_registry")

    implement_contract_address = os.environ.get("CONTRACT_ADDRESS_ERC6551_IMPLEMENTATION")

    tokenID = membership_contract.functions.getTokenIdFromAddress(user_address).call()

    tba_address = erc6551_contract.functions.account(implement_contract_address,salt, CHAIN_ID, membership_contract.address, tokenID).call()
    return {
        "implement_contract_address": implement_contract_address,
        "chain_id": CHAIN_ID,
        "membership_contract_address": membership_contract.address,
        "token_id": tokenID,
        "username": username,
        "salt": salt.hex(),
        "tba_wallet_address": tba_address,
        "main_wallet_address": user_address, 
    }

@app.get("/membership/")
def get_membership():
    membership_contract = loaded_contracts.get("oshigoto_membership")
    oshigoto_membership_contract = loaded_contracts.get("oshigoto_membership")
    mirror_nft_contract = loaded_contracts.get("mirror_nft")
    oshigoto_token_contract = loaded_contracts.get("oshigoto_token")

    membership_token_id = membership_contract.functions.getTokenIdFromAddress(user_address).call()

    config = oshigoto_membership_contract.functions.membershipConfigs(membership_token_id).call()
    tokenURI = oshigoto_membership_contract.functions.tokenURI(membership_token_id).call()

    # base64 -> json
    metadata = json.loads(base64.b64decode(tokenURI.split(",")[1]))

    # # unix timestamp to datetime
    # last_burned = datetime.datetime.fromtimestamp()

    oshigoto_721_balance = mirror_nft_contract.functions.balanceOf(user_address).call()
    oshigoto_20_balance_of = oshigoto_token_contract.functions.balanceOf(user_address).call()
    oshigoto_20_blance = int(oshigoto_20_balance_of) / 10**18

    return {
        "token_id": membership_token_id,
        "name": metadata["name"],
        "image": metadata["image"],
        "burn_point": config[0],
        "last_burned": config[1],
        "oshigoto_20_balance": oshigoto_20_blance,
        "oshigoto_721_balance": oshigoto_721_balance,
    }

@app.post("/memberships/alice")
def mint_memberships():
    membership_contrtact = loaded_contracts.get("oshigoto_membership")
    nonce = w3.eth.get_transaction_count(user_address)

    transaction = membership_contrtact.functions.mintMembership().build_transaction({
        'gas': 200000,  # Estimate gas limit
        'gasPrice': w3.to_wei('10', 'gwei'),  # Estimate gas price
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.sign_transaction(transaction, user_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    return {
        "from": user_address,
        "tx_hash": tx_hash.hex(),
    }

@app.get("/mirror_nft/{token_id}")
def get_mirror_nft(token_id: int):
    mirror_contract = loaded_contracts.get("mirror_nft")
    oshigoto_token_contract = loaded_contracts.get("oshigoto_token")
    
    try:
        token_uri = mirror_contract.functions.tokenURI(token_id).call()
    except:
        return {
            "error": "Token not found"
        }

    match = re.search(r'data:application/json;utf8,(.*)', token_uri)
    metadata = json.loads(match.group(1))

    rank = oshigoto_token_contract.functions.rankOf(token_id).call()
    owner = mirror_contract.functions.ownerOf(token_id).call()
    return {
        "name": metadata["name"],
        "image": metadata["image"],
        "owner_address": owner,
        "rank": rank,
    }

@app.post("/memberships/levelup/{material_token_id}")
def levelup_memberships(material_token_id: int):

    oshigoto_membership_contract = loaded_contracts.get("oshigoto_membership")
    material_contract_address = os.environ.get("CONTRACT_ADDRESS_MIRROR_NFT")

    nonce = w3.eth.get_transaction_count(user_address)

    # Membership Token ID
    token_id = oshigoto_membership_contract.functions.getTokenIdFromAddress(user_address).call()

    transaction = oshigoto_membership_contract.functions.levelUp(
        token_id,
        material_token_id,
        material_contract_address,
    ).build_transaction({
        'gas': 200000,  # Estimate gas limit
        'gasPrice': w3.to_wei('10', 'gwei'),  # Estimate gas price
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.sign_transaction(transaction, user_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    return {
        "from": user_address,
        "tx_hash": tx_hash.hex(),
    }

@app.post("/metalive_poap/mint/")
def mint_metalive_poap(username: str, nft_name: str):
    metalive_poap_contract = loaded_contracts.get("metalive_poap")
    nonce = w3.eth.get_transaction_count(owner_address)

    print(owner_address)

    # TBA Wallet
    salt = w3.solidity_keccak(["string"], [username])  
    membership_contract = loaded_contracts.get("oshigoto_membership")
    erc6551_contract = loaded_contracts.get("erc6551_registry")
    implement_contract_address = os.environ.get("CONTRACT_ADDRESS_ERC6551_IMPLEMENTATION")
    tokenID = membership_contract.functions.getTokenIdFromAddress(user_address).call()
    tba_address = erc6551_contract.functions.account(implement_contract_address,salt, CHAIN_ID, membership_contract.address, tokenID).call()
    print(tba_address)

    transaction = metalive_poap_contract.functions.airdrop(
        tba_address,
        nft_name,
    ).build_transaction({
        'from': owner_address,
        'gas': 2000000,  # Estimate gas limit
        'gasPrice': w3.to_wei('10', 'gwei'),  # Estimate gas price
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.sign_transaction(transaction, owner_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    return {
        "from": owner_address,
        "to": tba_address,
        "tx_hash": tx_hash.hex(),
    }

@app.post("/goods/mint/{goods_type}")
def mint_goods(goods_type: str, username: str):
    oshigoto_goods_contract = loaded_contracts.get("oshigoto_goods")
    oshigoto_token_contract = loaded_contracts.get("oshigoto_token")
    nonce = w3.eth.get_transaction_count(user_address)

    # TBA Wallet
    salt = w3.solidity_keccak(["string"], [username])  
    membership_contract = loaded_contracts.get("oshigoto_membership")
    erc6551_contract = loaded_contracts.get("erc6551_registry")
    implement_contract_address = os.environ.get("CONTRACT_ADDRESS_ERC6551_IMPLEMENTATION")
    tokenID = membership_contract.functions.getTokenIdFromAddress(user_address).call()
    tba_address = erc6551_contract.functions.account(implement_contract_address,salt, CHAIN_ID, membership_contract.address, tokenID).call()
    print(tba_address)

    # Approve
    transaction = oshigoto_token_contract.functions.approve(oshigoto_goods_contract.address, oshigoto_token_contract.balanceOf(user_address)).build_transaction({
        'gas': 200000,  # Estimate gas limit
        'gasPrice': w3.to_wei('10', 'gwei'),  # Estimate gas price
        'nonce': nonce,
    })

    # Mint goods
    if goods_type == "a":
        transaction = oshigoto_goods_contract.functions.purchaseGoodsA(tba_address).build_transaction({
            'gas': 200000,  # Estimate gas limit
            'gasPrice': w3.to_wei('10', 'gwei'),  # Estimate gas price
            'nonce': nonce,
        })
    elif goods_type == "b":
        transaction = oshigoto_goods_contract.functions.purchaseGoodsB(tba_address).build_transaction({
            'gas': 200000,  # Estimate gas limit
            'gasPrice': w3.to_wei('10', 'gwei'),  # Estimate gas price
            'nonce': nonce,
        })

    elif goods_type == "c":
        transaction = oshigoto_goods_contract.functions.purchaseGoodsC(tba_address).build_transaction({
            'gas': 200000,  # Estimate gas limit
            'gasPrice': w3.to_wei('10', 'gwei'),  # Estimate gas price
            'nonce': nonce,
        })
    else:
        return {
            "error": "Invalid goods type"
        }

    signed_txn = w3.eth.account.sign_transaction(transaction, user_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    return {
        "from": user_address,
        "to": tba_address,
        "tx_hash": tx_hash.hex(),
    }
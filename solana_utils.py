import json
import boto3
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.system_program import transfer, TransferParams

secrets_client = boto3.client('secretsmanager', region_name='eu-north-1')
PRIVATE_KEY_SECRET_NAME = 'game-wallet.json'

solana_client = Client("https://api.mainnet-beta.solana.com")

def get_game_wallet_keypair():
    secret_value = secrets_client.get_secret_value(SecretId=PRIVATE_KEY_SECRET_NAME)
    secret_array = json.loads(secret_value['SecretString'])  # should be [int, int, ...]
    secret_bytes = bytes(secret_array)
    return Keypair.from_secret_key(secret_bytes)

def send_sol(to_address, amount, sender_keypair):
    to_pubkey = PublicKey(to_address)
    tx = Transaction()
    tx.add(
        transfer(
            TransferParams(
                from_pubkey=sender_keypair.public_key,
                to_pubkey=to_pubkey,
                lamports=int(amount * 1e9)
            )
        )
    )
    response = solana_client.send_transaction(tx, sender_keypair)
    return response

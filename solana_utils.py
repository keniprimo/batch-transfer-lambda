import json
import boto3
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.system_program import transfer, TransferParams
from solana.rpc.api import Client

secrets_client = boto3.client('secretsmanager', region_name='eu-north-1')
PRIVATE_KEY_SECRET_NAME = 'game-wallet.json'
solana_client = Client("https://api.mainnet-beta.solana.com")

def get_game_wallet_keypair():
    secret_value = secrets_client.get_secret_value(SecretId=PRIVATE_KEY_SECRET_NAME)
    secret_array = json.loads(secret_value['SecretString'])
    return Keypair.from_bytes(bytes(secret_array))

def send_sol(to_address, amount, sender_keypair):
    to_pubkey = Pubkey.from_string(to_address)
    tx = Transaction([
        transfer(
            TransferParams(
                from_pubkey=sender_keypair.pubkey(),
                to_pubkey=to_pubkey,
                lamports=int(amount * 1e9)
            )
        )
    ])
    return solana_client.send_transaction(tx, sender_keypair)
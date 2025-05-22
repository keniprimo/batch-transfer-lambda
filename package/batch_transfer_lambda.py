import json
import boto3
from solana_utils import get_game_wallet_keypair, send_sol
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
balances_table = dynamodb.Table('PlayerBalances')

def lambda_handler(event, context):
    keypair = get_game_wallet_keypair()

    # Scan for all players
    response = balances_table.scan()
    players = response.get('Items', [])

    results = []

    for player in players:
        wallet = player.get('PlayerWallet')
        balance = Decimal(player.get('Balance', '0'))
        address = player.get('PlayerAddress')

        if wallet and balance > 0:
            try:
                tx = send_sol(wallet, float(balance), keypair)

                # Reset balance
                balances_table.put_item(Item={
                    'PlayerAddress': address,
                    'Balance': '0',
                    'PlayerWallet': wallet
                })

                results.append({
                    'PlayerAddress': address,
                    'txSignature': tx['result']
                })
            except Exception as e:
                results.append({
                    'PlayerAddress': address,
                    'error': str(e)
                })

    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }

import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import patch, MagicMock
from batch_transfer_lambda import lambda_handler

@patch("batch_transfer_lambda.send_sol")
@patch("solana_utils.get_game_wallet_keypair")
@patch("batch_transfer_lambda.balances_table")
def test_lambda_handler_success(mock_balances_table, mock_get_keypair, mock_send_sol):
    # Mock keypair
    mock_get_keypair.return_value = MagicMock()

    # Mock DynamoDB scan response
    mock_balances_table.scan.return_value = {
        "Items": [
            {"PlayerWallet": "Wallet1", "Balance": "0.5", "PlayerAddress": "Addr1"},
            {"PlayerWallet": "Wallet2", "Balance": "1.0", "PlayerAddress": "Addr2"}
        ]
    }

    # Mock Solana transfer
    mock_send_sol.return_value = {"result": "mocked_tx_signature"}

    # Call the lambda handler
    response = lambda_handler({}, {})

    # Assertions
    assert response["statusCode"] == 200
    result = json.loads(response["body"])
    assert len(result) == 2
    assert all("txSignature" in entry for entry in result)

@patch("batch_transfer_lambda.send_sol", side_effect=Exception("Transfer failed"))
@patch("solana_utils.get_game_wallet_keypair")
@patch("batch_transfer_lambda.balances_table")
def test_lambda_handler_transfer_failure(mock_balances_table, mock_get_keypair, mock_send_sol):
    mock_get_keypair.return_value = MagicMock()
    mock_balances_table.scan.return_value = {
        "Items": [
            {"PlayerWallet": "Wallet3", "Balance": "2.0", "PlayerAddress": "Addr3"}
        ]
    }

    response = lambda_handler({}, {})
    assert response["statusCode"] == 200
    result = json.loads(response["body"])
    assert len(result) == 1
    assert "error" in result[0]

@patch("batch_transfer_lambda.send_sol")
@patch("solana_utils.get_game_wallet_keypair")
@patch("batch_transfer_lambda.balances_table")
def test_lambda_handler_skips_zero_balance(mock_balances_table, mock_get_keypair, mock_send_sol):
    mock_get_keypair.return_value = MagicMock()
    mock_balances_table.scan.return_value = {
        "Items": [
            {"PlayerWallet": "Wallet4", "Balance": "0", "PlayerAddress": "Addr4"}
        ]
    }

    response = lambda_handler({}, {})
    assert response["statusCode"] == 200
    result = json.loads(response["body"])
    assert result == []

@patch("batch_transfer_lambda.send_sol")
@patch("solana_utils.get_game_wallet_keypair")
@patch("batch_transfer_lambda.balances_table")
def test_lambda_handler_empty_table(mock_balances_table, mock_get_keypair, mock_send_sol):
    mock_get_keypair.return_value = MagicMock()
    mock_balances_table.scan.return_value = {"Items": []}

    response = lambda_handler({}, {})
    assert response["statusCode"] == 200
    result = json.loads(response["body"])
    assert result == []

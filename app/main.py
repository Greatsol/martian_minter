"""Dev: https://t.me/python_web3"""


import json
from random import randint

from aptos_sdk.account import Account, AccountAddress
from aptos_sdk.bcs import Serializer
from aptos_sdk.client import RestClient
from aptos_sdk.transactions import (EntryFunction, TransactionArgument,
                                    TransactionPayload)
from loguru import logger
from tenacity import retry
from tenacity.stop import stop_after_attempt

from app.config import (EXIST_WALLETS, MAIN_PRIVATE_KEY, TESTNET_URL,
                        WALLETS_AMOUNT)

logger.add(
    "log/debug.log",
    format="{time} | {level} | {message}",
    level="DEBUG",
)

rest_client = RestClient(TESTNET_URL)
main_acc = Account.load_key(MAIN_PRIVATE_KEY)


def main():
    logger.info("Start abuz")
    if EXIST_WALLETS:
        wallets = load_wallets()
    else:
        wallets = generate_wallets(WALLETS_AMOUNT)
    disperse_apt_to_wallets(main_acc=main_acc, target_wallets=wallets)
    multi_mint(wallets)
    logger.success("All done")


def multi_mint(wallets: list[Account]) -> None:
    """Creates collection and mint Martian testnet NFT for all target wallets."""

    for wallet in wallets:
        mint_martian_nft(wallet)


def generate_wallets(amount: int) -> list[Account]:
    """Generate wallets and save they in private.json."""

    wallets = [Account.generate() for _ in range(amount)]
    for wallet in wallets:
        txn = create_account(main_acc, wallet)
        wait_for_transaction(txn)
        logger.success(f"Create wallet: {wallet.address()}")
    with open("private.json", "w", encoding="utf8") as file:
        json.dump(
            obj=[str(wallet.private_key) for wallet in wallets], fp=file, indent=4
        )
    logger.info(f"Generate and save {amount} wallets")
    return wallets


def load_wallets() -> list[Account]:
    """Load private keys from private.json."""

    with open("private.json", "r", encoding="utf8") as file:
        wallets = json.load(file)
    wallets = [Account.load_key(key) for key in wallets]
    logger.info(f"Load {len(wallets)} wallets from file")
    return wallets


@retry(stop=stop_after_attempt(3))
def wait_for_transaction(txn: str) -> None:
    """Wrapped RestClient.wait_for_transaction."""

    rest_client.wait_for_transaction(txn)


@retry(stop=stop_after_attempt(3))
def create_account(account: Account, target_acc: Account) -> str:
    """Create wallet without faucet."""

    transaction_arguments = [
        TransactionArgument(str(target_acc.address()), Serializer.struct)
    ]

    payload = {
        "type": "entry_function_payload",
        "function": "0x1::aptos_account::create_account",
        "type_arguments": [],
        "arguments": [f"{target_acc.address()}"],
    }
    signed_transaction = rest_client.submit_transaction(account, payload)
    return signed_transaction


def disperse_apt_to_wallets(main_acc: Account, target_wallets: list[Account]) -> None:
    """Disperse APT to target wallets."""

    amount = 0.15
    for wallet in target_wallets:
        txn = transfer(main_acc, wallet.address(), amount)
        wait_for_transaction(txn)
        logger.info(f"Transfer {amount} APT to {wallet.address()}")


@retry(stop=stop_after_attempt(3))
def transfer(main_acc: Account, target_wallet: AccountAddress, amount: float | int) -> str:
    """Safe transfer apt."""
    return transfer(main_acc, target_wallet, convert_apt_to_wei(amount))


def convert_apt_to_wei(amount: float | int) -> int:
    """Converts APT to wei."""

    return int(amount * 100_000_000)


def mint_martian_nft(account: Account):
    """Creates random Martian testnet NFT for wallet."""

    name = randint(11111, 99999)
    txn = create_testnet_collection(account, name)
    wait_for_transaction(txn)
    logger.info(
        f"Create collection number {name} for address {account.address()}")

    txn = create_testnet_nft(account, name)
    wait_for_transaction(txn)
    logger.success(f"Mint nft number {name} for address {account.address()}")


@retry(stop=stop_after_attempt(3))
def create_testnet_collection(account: Account, name: int) -> str:
    """Creates a new collection by number within the specified account."""

    transaction_arguments = [
        TransactionArgument(f"Martian Testnet{name}", Serializer.str),
        TransactionArgument("Martian Testnet NFT", Serializer.str),
        TransactionArgument("https://aptos.dev", Serializer.str),
        TransactionArgument(9007199254740991, Serializer.u64),
        TransactionArgument(
            [False, False, False], Serializer.sequence_serializer(
                Serializer.bool)
        ),
    ]

    payload = EntryFunction.natural(
        "0x3::token",
        "create_collection_script",
        [],
        transaction_arguments,
    )

    signed_transaction = rest_client.create_single_signer_bcs_transaction(
        account, TransactionPayload(payload)
    )
    return rest_client.submit_bcs_transaction(signed_transaction)


@retry(stop=stop_after_attempt(3))
def create_testnet_nft(account: Account, name: int) -> str:
    """Creates a Martian NFT."""

    transaction_arguments = [
        TransactionArgument(f"Martian Testnet{name}", Serializer.str),
        TransactionArgument(f"Martian NFT #{name}", Serializer.str),
        TransactionArgument("OG Martian", Serializer.str),
        TransactionArgument(1, Serializer.u64),
        TransactionArgument(9007199254740991, Serializer.u64),
        TransactionArgument(
            "https://gateway.pinata.cloud/ipfs/QmXiSJPXJ8mf9LHijv6xFH1AtGef4h8v5VPEKZgjR4nzvM",
            Serializer.str,
        ),
        TransactionArgument(account.address(), Serializer.struct),
        TransactionArgument(0, Serializer.u64),
        TransactionArgument(0, Serializer.u64),
        TransactionArgument(
            [False, False, False, False, False],
            Serializer.sequence_serializer(Serializer.bool),
        ),
        TransactionArgument(
            [], Serializer.sequence_serializer(Serializer.str)),
        TransactionArgument(
            [], Serializer.sequence_serializer(Serializer.bytes)),
        TransactionArgument(
            [], Serializer.sequence_serializer(Serializer.str)),
    ]

    payload = EntryFunction.natural(
        "0x3::token",
        "create_token_script",
        [],
        transaction_arguments,
    )
    signed_transaction = rest_client.create_single_signer_bcs_transaction(
        account, TransactionPayload(payload)
    )
    return rest_client.submit_bcs_transaction(signed_transaction)


if __name__ == "__main__":
    main()

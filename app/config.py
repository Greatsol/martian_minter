import os

from dotenv import load_dotenv

load_dotenv()

MAIN_PRIVATE_KEY = os.environ["MAIN_PRIVATE_KEY"]
EXIST_WALLETS = os.environ["EXIST_WALLETS"] == "True"
WALLETS_AMOUNT = int(os.environ["WALLETS_AMOUNT"])
TESTNET_URL = os.environ["TESTNET_URL"]

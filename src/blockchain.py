import os

from dotenv import load_dotenv
from stellar_sdk import Server


load_dotenv()

PUBLIC_KEY = os.getenv("STELLAR_PUBLIC_KEY")

if not PUBLIC_KEY:
    raise RuntimeError(
        "STELLAR_PUBLIC_KEY is missing from .env"
    )


print()
print("=" * 50)
print("        FACETRACE BLOCKCHAIN")
print("=" * 50)

print("\nConnecting to Stellar Testnet...")

server = Server(
    "https://horizon-testnet.stellar.org"
)

try:
    server.load_account(PUBLIC_KEY)

    print("✓ Connected to Stellar Testnet")
    print(f"✓ Account loaded: {PUBLIC_KEY}")
    print("✓ Testnet account is active")
    print("\nSPRINT 3 BLOCKCHAIN SETUP COMPLETE ✓")

except Exception as e:

    print("\n❌ Could not load Stellar account")
    print(f"Error: {e}")

print("=" * 50)
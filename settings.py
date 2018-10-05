import os

from dotenv import load_dotenv
load_dotenv()

ENV = os.getenv('ENV', "development")

CHANNEL_SECRET = os.getenv('CHANNEL_SECRET', None)
CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN', None)

if CHANNEL_SECRET is None:
    print('Specify CHANNEL_SECRET as environment variable.')
    os.sys.exit(1)
if CHANNEL_ACCESS_TOKEN is None:
    print('Specify CHANNEL_ACCESS_TOKEN as environment variable.')
    os.sys.exit(1)

SHARED_ACCESS_KEY_NAME = os.getenv('SHARED_ACCESS_KEY_NAME', None)
SHARED_ACCESS_KEY = os.getenv('SHARED_ACCESS_KEY', None)

if SHARED_ACCESS_KEY_NAME is None:
    print('Specify SHARED_ACCESS_KEY_NAME as environment variable.')
    os.sys.exit(1)
if SHARED_ACCESS_KEY is None:
    print('Specify SHARED_ACCESS_KEY as environment variable.')
    os.sys.exit(1)

BLOB_ACCOUNT_NAME = os.getenv('BLOB_ACCOUNT_NAME', None)
BLOB_ACCOUNT_KEY = os.getenv('BLOB_ACCOUNT_KEY', None)

if BLOB_ACCOUNT_NAME is None:
    print('Specify BLOB_ACCOUNT_NAME as environment variable.')
    os.sys.exit(1)
if BLOB_ACCOUNT_KEY is None:
    print('Specify BLOB_ACCOUNT_KEY as environment variable.')
    os.sys.exit(1)
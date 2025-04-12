import os
import sys
import psycopg
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read DB config from environment variables
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', 5432)
POSTGRES_DATABASE = os.environ.get('POSTGRES_DATABASE')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

TABLE_NAME = 'summary'

# Validate required variables
required_vars = [POSTGRES_HOST, POSTGRES_DATABASE, POSTGRES_USER, POSTGRES_PASSWORD]
if not all(required_vars):
    print("Missing one or more required environment variables: POSTGRES_HOST, POSTGRES_DATABASE, POSTGRES_USER, POSTGRES_PASSWORD", file=sys.stderr)
    sys.exit(1)

try:
    # Connect using psycopg3
    with psycopg.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DATABASE,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    ) as conn:
        # Use pandas to read the table
        query = f"SELECT * FROM {TABLE_NAME};"
        df = pd.read_sql(query, conn)

        # Print DataFrame as CSV to stdout
        print(df.to_csv(index=False))

except Exception as e:
    print(f"Error: {e}", file=sys.stderr)

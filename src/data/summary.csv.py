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

        query = f'''with filtered_dates as (
            select distinct datestamp
                from {TABLE_NAME}
                where datestamp >= date_trunc('day', current_date) - interval '12 months'
            ),
            ordered_dates as (
                select datestamp,
                    row_number() over (order by datestamp) as rn,
                    count(*) over () as total
                from filtered_dates
            ),
            selected_dates as (
                select datestamp
                from ordered_dates
                where rn = 1
                or rn = total
                or rn in (
                        floor(total * 1.0 / 11 * 1)::int,
                        floor(total * 1.0 / 11 * 2)::int,
                        floor(total * 1.0 / 11 * 3)::int,
                        floor(total * 1.0 / 11 * 4)::int,
                        floor(total * 1.0 / 11 * 5)::int,
                        floor(total * 1.0 / 11 * 6)::int,
                        floor(total * 1.0 / 11 * 7)::int,
                        floor(total * 1.0 / 11 * 8)::int,
                        floor(total * 1.0 / 11 * 9)::int,
                        floor(total * 1.0 / 11 * 10)::int
                )
            )
            SELECT * FROM {TABLE_NAME} inner join selected_dates on selected_dates.datestamp = {TABLE_NAME}.datestamp;'''

        df = pd.read_sql(query, conn)

        # Print DataFrame as CSV to stdout
        print(df.to_csv(index=False))

except Exception as e:
    print(f"Error: {e}", file=sys.stderr)

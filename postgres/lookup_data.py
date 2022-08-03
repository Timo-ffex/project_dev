import argparse, os
from time import time
import pandas as pd
from sqlalchemy import create_engine

def batch_write(df, table_name, engine):

    total = len(df)
    count = 0

    while count < total:
        start = time()
        next_ = count + 50000
        write_df = df.iloc[count: next_]
        write_df.to_sql(name=table_name, con=engine, if_exists='append')
        count = next_
        print(f'inserted chunk... took: {round((time()-start), 2)} second')


def main(params):
    user = params.user
    password = params.password
    host = params.host
    db = params.db
    table_name = params.table_name
    port = params.port
    url = params.url

    file_name = 'file.csv'
    os.system(f"wget {url} -O {file_name}")

    engine = create_engine(f'postgresql+pg8000://{user}:{password}@{host}:{port}/{db}')

    df = pd.read_parquet(file_name)
    print(df.shape)
    df.head(0).to_sql(name=table_name, con=engine, if_exists='replace')
    batch_write(df, table_name, engine)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest data into postgres")

    parser.add_argument('--user', help='username for postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='database for postgres')
    parser.add_argument('--table_name', help='the name of the table to write the data')
    parser.add_argument('--url', help='the url to download the file')


    args = parser.parse_args()
    print(args)
    main(args)
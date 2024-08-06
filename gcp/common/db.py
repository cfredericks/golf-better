"""
Helpers for interacting with the database.
"""

import os
import pg8000

from .auth_utils import get_gsm_secret
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from google.cloud.sql.connector import Connector


def get_db_connection():
    db_user = os.getenv('DB_USER', default='postgres')
    db_password = os.getenv('DB_PASSWORD') or get_gsm_secret('golf-better-cloudsql-password')
    db_name = os.getenv('DB_NAME', default='postgres')
    db_instance_conn_name = os.getenv('INSTANCE_CONNECTION_NAME', default='stoked-depth-428423-j7:us-central1:golf-better')
    db_host = os.getenv('DB_HOST', default=f'/cloudsql/{db_instance_conn_name}')
    db_port = os.getenv('DB_PORT', default=5432)

    pw_log = "****" if db_password is not None else "<unset>"
    print(f'Connecting to PG on user={db_user}, pw={pw_log}, host={db_host}, port={db_port}, db={db_name}')

    def getconn():
        if db_instance_conn_name:
            print(f'Connecting to CloudSQL instance with instance name: "{db_instance_conn_name}"')
            connector = Connector()
            return connector.connect(
                db_instance_conn_name,
                "pg8000",
                user=db_user,
                password=db_password,
                db=db_name,
            )
        else:
            print('Connecting to vanilla Postgres database')
            return pg8000.connect(
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
                database=db_name
            )

    engine = create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        connect_args={
            "port": db_port
        }
    )

    return engine

engine = get_db_connection()
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
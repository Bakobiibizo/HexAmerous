import os
import json
from dotenv import load_dotenv
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

load_dotenv()


cloud_config= {
  'secure_connect_bundle': 'creds/secure-connect-vectorstore.zip'
}


with open("creds/vectorstore-token.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

CLIENT_ID = secrets["clientId"]
CLIENT_SECRET = secrets["secret"]
ASTRA_DB_KEYSPACE = os.getenv("ASTRA_DB_KEYSPACE")


auth_provider = PlainTextAuthProvider(CLIENT_ID, CLIENT_SECRET)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()


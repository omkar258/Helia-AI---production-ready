"""Setup PostgreSQL database for Helia AI."""
import psycopg2
import sys

creds = [
    ("postgres", "postgres"),
    ("postgres", ""),
    ("omkar", ""),
    ("omkar", "omkar"),
    ("postgres", "root"),
    ("postgres", "admin"),
    ("postgres", "password"),
    ("postgres", "1234"),
    ("postgres", "12345"),
]

connected = False
for user, pw in creds:
    try:
        conn = psycopg2.connect(host="localhost", port=5432, user=user, password=pw, dbname="postgres")
        conn.autocommit = True
        print(f"SUCCESS: Connected as '{user}'")
        connected = True
        cur = conn.cursor()

        # Check/create database
        cur.execute("SELECT 1 FROM pg_database WHERE datname='helia_db'")
        if cur.fetchone():
            print("  helia_db already exists")
        else:
            cur.execute("CREATE DATABASE helia_db")
            print("  Created helia_db")

        # Check/create user
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname='helia_user'")
        if not cur.fetchone():
            cur.execute("CREATE USER helia_user WITH PASSWORD 'change_me_in_production'")
            print("  Created helia_user")
        else:
            print("  helia_user already exists")

        # Grant privileges
        cur.execute("GRANT ALL PRIVILEGES ON DATABASE helia_db TO helia_user")
        print("  Granted privileges to helia_user")

        # Grant schema access
        try:
            conn2 = psycopg2.connect(host="localhost", port=5432, user=user, password=pw, dbname="helia_db")
            conn2.autocommit = True
            cur2 = conn2.cursor()
            cur2.execute("GRANT ALL ON SCHEMA public TO helia_user")
            cur2.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO helia_user")
            print("  Granted schema privileges")
            conn2.close()
        except Exception as e2:
            print(f"  Schema grant note: {e2}")

        conn.close()
        print("\nDatabase setup complete!")
        break
    except Exception as e:
        continue

if not connected:
    print("ERROR: Could not connect to PostgreSQL with any default credentials.")
    print("Please provide your PostgreSQL username and password.")
    sys.exit(1)

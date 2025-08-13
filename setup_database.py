import sqlite3
import pandas as pd

# Connect to the SQLite database. It will be created if it doesn't exist.
conn = sqlite3.connect('food_waste.db')
cursor = conn.cursor()

# Create Providers table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Providers (
        Provider_ID INTEGER PRIMARY KEY,
        Name TEXT,
        Type TEXT,
        Address TEXT,
        City TEXT,
        Contact TEXT
    )
""")

# Create Receivers table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Receivers (
        Receiver_ID INTEGER PRIMARY KEY,
        Name TEXT,
        Type TEXT,
        City TEXT,
        Contact TEXT
    )
""")

# Create Food_Listings table with all required columns
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Food_Listings (
        Food_ID INTEGER PRIMARY KEY,
        Food_Name TEXT,
        Quantity INTEGER,
        Expiry_Date TEXT,
        Provider_ID INTEGER,
        Provider_Type TEXT,
        Location TEXT,
        Food_Type TEXT,
        Meal_Type TEXT,
        FOREIGN KEY (Provider_ID) REFERENCES Providers (Provider_ID)
    )
""")

# Create Claims table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Claims (
        Claim_ID INTEGER PRIMARY KEY,
        Food_ID INTEGER,
        Receiver_ID INTEGER,
        Status TEXT,
        Timestamp TEXT,
        FOREIGN KEY (Food_ID) REFERENCES Food_Listings (Food_ID),
        FOREIGN KEY (Receiver_ID) REFERENCES Receivers (Receiver_ID)
    )
""")

# Read data from CSV files and insert into tables
def load_data_from_csv(table_name, csv_file_path):
    df = pd.read_csv(csv_file_path)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    print(f"Data from {csv_file_path} loaded into {table_name} table.")

try:
    load_data_from_csv("Providers", "providers_data.csv")
    load_data_from_csv("Receivers", "receivers_data.csv")
    load_data_from_csv("Food_Listings", "food_listings_data.csv")
    load_data_from_csv("Claims", "claims_data.csv")
    print("Database setup complete.")
except FileNotFoundError as e:
    print(f"Error: {e}. Please ensure all CSV files are in the same directory.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

# Commit changes and close connection
conn.commit()
conn.close()

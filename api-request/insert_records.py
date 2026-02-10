import os

from api_request import mock_fetch_data
import psycopg2
from dotenv import load_dotenv

load_dotenv('./.env')

DB_PASSWORD = os.getenv('DB_PASSWORD')



def connect_to_postgres():
    print("Connecting to the PostgreSQL database...")

    try:
      conn = psycopg2.connect(
        host="localhost",
        port=5000,
        dbname='weather_db',
        user='weather_user',
        password=DB_PASSWORD
      )

      return conn

    except psycopg2.Error as e:
      print(f"Database connection failed: {e}")
      raise

def create_tables(conn):
    print("Creating table if not exists...")

    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE SCHEMA IF NOT EXISTS dev;
            CREATE TABLE IF NOT EXISTS dev.raw_weather_data (
                id SERIAL PRIMARY KEY,
                city TEXT,
                temperature FLOAT,
                weather_description TEXT,
                wind_speed FLOAT,
                time TIMESTAMP,
                inserted_at TIMESTAMP DEFAULT NOT(),
                utc_offset TEXT
            );
        ''')

        conn.commit()
        print("Table created successfully.")

    except psycopg2.Error as e:
        print(f"Table Creation failed: {e}")
        raise

def insert_weather_data(conn, data):
    print("Inserting weather data...")
    try:
        weather = data['current']
        location = data['location']

        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO dev.raw_weather_data (
                city,
                temperature,
                weather_description,
                wind_speed,
                time,
                inserted_at,
                utc_offset
            ) VALUES (%s, %s, %s, %s, %s, NOW(), %s)
        ''', (
            location['name'],
            weather['temperature'],
            weather['weather_descriptions'][0],
            weather['wind_speed'],
            location['localtime'],
            location['utc_offset'],
        ))

        conn.commit()
        print("Weather data inserted successfully.")

    except psycopg2.Error as e:
        print(f"Insertion failed: {e}")
        raise


def main():
    try:
        data = mock_fetch_data()
        conn = connect_to_postgres()
        create_tables(conn)
        insert_weather_data(conn, data)
    except Exception as e:
        print("An error occurred during execution: ", e)
        raise

    finally:
        if 'conn' in locals():
            conn.close()
            print("Connection closed.")

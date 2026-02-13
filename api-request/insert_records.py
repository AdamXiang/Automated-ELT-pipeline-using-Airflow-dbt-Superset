import os
from api_request import mock_fetch_data, fetch_data
import psycopg2
from dotenv import load_dotenv
import json
from airflow.models import Variable

def connect_to_postgres(password):
    print("Connecting to the PostgreSQL database...")

    try:
      conn = psycopg2.connect(
        host="postgres",
        port=5432,
        dbname='weather_db',
        user='weather_user',
        password=password
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
                inserted_at TIMESTAMP DEFAULT NOW(),
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

    # 1. 安全檢查：確保資料是正確的
    if not isinstance(data, dict):
        raise ValueError(f"Data format error: Expected dict, got {type(data)}")

    # 2. 檢查是否包含 'current'，如果沒有，把整包資料印出來看
    if 'current' not in data:
        # 這行會把那個「導致錯誤的壞資料」印在 Log 裡
        print(f"❌ CRITICAL ERROR: API response is missing 'current' key.")
        print(f"❌ BAD DATA: {json.dumps(data, indent=2)}")

        # 檢查是否為 API 錯誤訊息
        if 'error' in data:
            raise ValueError(f"API Error: {data['error'].get('info', 'Unknown error')}")

        raise KeyError("Missing 'current' key in API response")

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
        api_key = Variable.get("WEATHER_API_KEY")
        data = fetch_data(api_key)
        db_password = Variable.get("DB_PASSWORD")
        conn = connect_to_postgres(db_password)
        create_tables(conn)
        insert_weather_data(conn, data)
    except Exception as e:
        print("An error occurred during execution: ", e)
        raise

    finally:
        if 'conn' in locals():
            conn.close()
            print("Connection closed.")

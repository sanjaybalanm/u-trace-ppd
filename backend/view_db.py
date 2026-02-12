import sqlite3
import pandas as pd
import json

def view_database():
    print("--- CONNECTING TO DATABASE ---")
    try:
        conn = sqlite3.connect('users.db')
        
        print("\n=== 1. USERS TABLE ===")
        users_df = pd.read_sql_query("SELECT * FROM users", conn)
        if not users_df.empty:
            print(users_df)
        else:
            print("No users found.")

        print("\n=== 2. PREDICTIONS TABLE (Last 5) ===")
        predictions_df = pd.read_sql_query("SELECT * FROM predictions ORDER BY id DESC LIMIT 5", conn)
        
        if not predictions_df.empty:
            # Clean up display
            print(predictions_df[['id', 'user_id', 'date', 'risk_level', 'score']])
            print("\n[Details Column Omitted for Brevity]")
        else:
            print("No predictions found.")

        conn.close()
        print("\n--- DONE ---")

    except Exception as e:
        print(f"Error accessing database: {e}")

if __name__ == "__main__":
    view_database()

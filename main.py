import os
from database import Database

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.db")

def main():
    db = Database(DB_PATH)

    if not os.path.exists(DB_PATH):
        db.init_db()

if __name__ == "__main__":
    main()

import sqlite3

def init_database():
    conn = sqlite3.connect("cinema.db")
    cursor = conn.cursor()

    # Create movies table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            cinema_room INTEGER CHECK(cinema_room BETWEEN 1 AND 7),
            release_date TEXT,
            end_date TEXT,
            tickets_available INTEGER,
            ticket_price REAL
        )
    ''')

    # Create sales table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER,
            customer_name TEXT,
            number_of_tickets INTEGER,
            total REAL,
            FOREIGN KEY(movie_id) REFERENCES movies(id)
        )
    ''')

    # Check if movies already exist
    cursor.execute('SELECT COUNT(*) FROM movies')
    if cursor.fetchone()[0] == 0:
        movies = [
            ("Jurassic Park",       1, "2025-07-01", "2025-07-20", 100, 85.0),
            ("Frozen",              2, "2025-07-02", "2025-07-22", 120, 65.0),
            ("The Dictator",        3, "2025-07-03", "2025-07-18", 80, 70.0),
            ("Final Destination",   4, "2025-07-04", "2025-07-25", 90, 75.0),
            ("Ocean’s Legacy",      5, "2025-07-05", "2025-07-28", 70, 80.0),
            ("Novacaine",           6, "2025-07-06", "2025-07-26", 150, 60.0),
            ("The Incredible Hulk", 7, "2025-07-07", "2025-07-30", 85, 90.0)
        ]

        cursor.executemany('''
            INSERT INTO movies (title, cinema_room, release_date, end_date, tickets_available, ticket_price)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', movies)

        print("Sample movies inserted successfully.")
    else:
        print("Movies already exist. Skipping sample insert.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()

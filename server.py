import socket
import json
import sqlite3
import threading

# Handles each client
def handle_client(conn, addr):
    db = sqlite3.connect("cinema.db")
    cursor = db.cursor()

    with conn:
        while True:
            try:
                data = conn.recv(4096).decode()
                if not data:
                    break

                request = json.loads(data)
                response = handle_request(request, cursor, db)
                conn.send(json.dumps(response).encode())

            except Exception as e:
                error_msg = {"status": "error", "message": str(e)}
                try:
                    conn.send(json.dumps(error_msg).encode())
                except:
                    break

# Handles client requests
def handle_request(req, cursor, db):
    action = req.get("action")

    if action == "get_movies":
        cursor.execute("SELECT * FROM movies")
        return {"status": "success", "data": cursor.fetchall()}

    elif action == "add_movie":
        m = req["movie"]
        cursor.execute('''
            INSERT INTO movies (title, cinema_room, release_date, end_date, tickets_available, ticket_price)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (m["title"], m["cinema_room"], m["release_date"], m["end_date"], m["tickets_available"], m["ticket_price"]))
        db.commit()
        return {"status": "success", "message": "Movie added."}

    elif action == "update_movie":
        m = req["movie"]
        cursor.execute('''
            UPDATE movies
            SET title=?, cinema_room=?, release_date=?, end_date=?, tickets_available=?, ticket_price=?
            WHERE id=?
        ''', (m["title"], m["cinema_room"], m["release_date"], m["end_date"], m["tickets_available"], m["ticket_price"], m["id"]))
        db.commit()
        return {"status": "success", "message": "Movie updated."}

    elif action == "delete_movie":
        movie_id = req.get("id")
        cursor.execute("SELECT * FROM movies WHERE id=?", (movie_id,))
        if not cursor.fetchone():
            return {"status": "error", "message": "Movie not found."}
        cursor.execute("DELETE FROM movies WHERE id=?", (movie_id,))
        db.commit()
        return {"status": "success", "message": "Movie deleted."}

    elif action == "buy_ticket":
        try:
            movie_id = req["movie_id"]
            name = req["customer_name"]
            qty = int(req["number_of_tickets"])

            if qty <= 0:
                return {"status": "error", "message": "Invalid quantity."}

            cursor.execute("SELECT ticket_price, tickets_available FROM movies WHERE id=?", (movie_id,))
            movie = cursor.fetchone()
            if not movie:
                return {"status": "error", "message": "Movie not found."}

            price, available = movie
            if qty > available:
                return {"status": "error", "message": "Not enough tickets."}

            total = qty * price

            cursor.execute('''
                INSERT INTO sales (movie_id, customer_name, number_of_tickets, total)
                VALUES (?, ?, ?, ?)
            ''', (movie_id, name, qty, total))

            cursor.execute("UPDATE movies SET tickets_available=? WHERE id=?", (available - qty, movie_id))
            db.commit()

            return {
                "status": "success",
                "message": "Purchase successful.",
                "data": {
                    "movie_id": movie_id,
                    "customer_name": name,
                    "number_of_tickets": qty,
                    "total": total
                }
            }

        except Exception as e:
            return {"status": "error", "message": f"Purchase failed: {e}"}

    return {"status": "error", "message": "Unknown action."}

# Starts the server
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 12345))
    server.listen(5)
    print("Server running on port 12345")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    main()


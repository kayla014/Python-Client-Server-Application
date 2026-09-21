import socket
import tkinter as tk
from tkinter import ttk, messagebox
import json

def send_request(data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", 12345))
            s.send(json.dumps(data).encode())
            return json.loads(s.recv(4096).decode())
    except Exception as e:
        return {"status": "error", "message": str(e)}

class CinemaClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Welcome To the NewLine Cinema")
        self.root.geometry("720x520")
        self.root.resizable(False, False)
        self.setup_style()
        self.setup_ui()
        self.load_movies()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 11), padding=6)
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TCombobox", font=("Segoe UI", 10))

    def setup_ui(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Welcome To the NewLine Cinema", font=("Segoe UI", 24, "bold")).pack(pady=(0, 20))

        self.movie_dropdown = ttk.Combobox(frame, state="readonly", width=60)
        self.movie_dropdown.pack(pady=(0, 15))

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)

        for text, cmd in [
            ("Refresh", self.load_movies),
            ("Show All", self.show_all),
            ("Add", self.add_movie),
            ("Edit", self.edit_movie),
            ("Delete", self.delete_movie),
            ("Buy", self.buy_ticket),
        ]:
            ttk.Button(btn_frame, text=text, command=cmd).pack(side="left", padx=5)

        # Text Box
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill="both", expand=True)

        self.movie_text = tk.Text(text_frame, height=15, state="disabled", font=("Segoe UI", 10), relief="solid")
        self.movie_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(text_frame, command=self.movie_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.movie_text.config(yscrollcommand=scrollbar.set)

    def load_movies(self):
        res = send_request({"action": "get_movies"})
        if res["status"] == "success":
            self.movie_dropdown["values"] = [f"{m[0]} - {m[1]}" for m in res["data"]]
            self.movie_dropdown.set("Select a movie")
        else:
            messagebox.showerror("Error", res["message"])

    def show_all(self):
        res = send_request({"action": "get_movies"})
        if res["status"] == "success":
            self.movie_text.config(state="normal")
            self.movie_text.delete(1.0, tk.END)
            for m in res["data"]:
                line = f"ID: {m[0]} | Title: {m[1]} | Room: {m[2]} | Release: {m[3]} | End: {m[4]} | Tickets: {m[5]} | Price: R{m[6]:.2f}\n"
                self.movie_text.insert(tk.END, line)
            self.movie_text.config(state="disabled")
        else:
            messagebox.showerror("Error", res["message"])

    def get_selected_movie_id(self):
        selected = self.movie_dropdown.get()
        return int(selected.split(" - ")[0]) if " - " in selected else None

    def open_form(self, title, fields, values, on_submit):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("350x350")
        entries = []
        for i, field in enumerate(fields):
            frame = ttk.Frame(win)
            frame.pack(fill="x", pady=5)
            ttk.Label(frame, text=field).pack(anchor="w")
            entry = ttk.Entry(frame)
            if values: entry.insert(0, values[i])
            entry.pack(fill="x")
            entries.append(entry)
        ttk.Button(win, text="Submit", command=lambda: on_submit(entries, win)).pack(pady=10)

    def add_movie(self):
        fields = ["Title", "Cinema Room", "Release Date", "End Date", "Tickets", "Price"]
        def submit(entries, win):
            try:
                movie = {
                    "title": entries[0].get(),
                    "cinema_room": int(entries[1].get()),
                    "release_date": entries[2].get(),
                    "end_date": entries[3].get(),
                    "tickets_available": int(entries[4].get()),
                    "ticket_price": float(entries[5].get())
                }
                res = send_request({"action": "add_movie", "movie": movie})
                messagebox.showinfo("Result", res["message"])
                self.load_movies()
                self.show_all()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid: {e}")
        self.open_form("Add Movie", fields, None, submit)

    def edit_movie(self):
        movie_id = self.get_selected_movie_id()
        if not movie_id:
            messagebox.showerror("Error", "Select a movie.")
            return
        res = send_request({"action": "get_movies"})
        movie = next((m for m in res["data"] if m[0] == movie_id), None)
        if not movie:
            messagebox.showerror("Error", "Movie not found.")
            return
        fields = ["Title", "Cinema Room", "Release Date", "End Date", "Tickets", "Price"]
        values = [movie[1], movie[2], movie[3], movie[4], movie[5], movie[6]]
        def submit(entries, win):
            try:
                updated = {
                    "id": movie_id,
                    "title": entries[0].get(),
                    "cinema_room": int(entries[1].get()),
                    "release_date": entries[2].get(),
                    "end_date": entries[3].get(),
                    "tickets_available": int(entries[4].get()),
                    "ticket_price": float(entries[5].get())
                }
                res = send_request({"action": "update_movie", "movie": updated})
                messagebox.showinfo("Updated", res["message"])
                self.load_movies()
                self.show_all()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid: {e}")
        self.open_form("Edit Movie", fields, values, submit)

    def delete_movie(self):
        movie_id = self.get_selected_movie_id()
        if not movie_id:
            messagebox.showerror("Error", "Select a movie.")
            return
        if messagebox.askyesno("Delete", f"Delete movie ID {movie_id}?"):
            res = send_request({"action": "delete_movie", "id": movie_id})
            if res["status"] == "success":
                messagebox.showinfo("Deleted", res["message"])
                self.load_movies()
                self.show_all()
            else:
                messagebox.showerror("Error", res["message"])

    def buy_ticket(self):
        movie_id = self.get_selected_movie_id()
        if not movie_id:
            messagebox.showerror("Error", "Select a movie.")
            return
        fields = ["Your Name", "Number of Tickets"]
        def submit(entries, win):
            try:
                res = send_request({
                    "action": "buy_ticket",
                    "movie_id": movie_id,
                    "customer_name": entries[0].get(),
                    "number_of_tickets": int(entries[1].get())
                })
                if res["status"] == "success":
                    total = res["data"]["total"]
                    messagebox.showinfo("Success", f"Total: R{total:.2f}")
                    self.load_movies()
                    self.show_all()
                    win.destroy()
                else:
                    messagebox.showerror("Error", res["message"])
            except Exception as e:
                messagebox.showerror("Error", f"Invalid: {e}")
        self.open_form("Buy Tickets", fields, None, submit)

# Run App
if __name__ == "__main__":
    root = tk.Tk()
    app = CinemaClient(root)
    root.mainloop()


import re
import time
import json
import threading
import functools
from datetime import datetime, date

from models import (
    Book,
    Member,
    Student,
    Faculty,
    get_fine_calculator
)


def log_call(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        print(f"[LOG] Calling {func.__name__}{args[1:]}")
        result = func(*args, **kwargs)

        print(f"[LOG] {func.__name__} -> {result}")

        return result

    return wrapper


class Library:
    def __init__(self):
        self.books = {}      
        self.members = {}    

    
    def add_book(self, book):
        self.books[book.isbn] = book
        print(f"Added book: {book}")

    def register_member(self, member):
        self.members[member.member_id] = member
        print(f"Registered member: {member}")


    @log_call
    def issue_book(self, isbn, member_id):
        book = self.books.get(isbn)
        member = self.members.get(member_id)

        if not book:
            return "Error: Book not found."
        if not member:
            return "Error: Member not found."
        if book.is_issued:
            return f"Error: '{book.title}' is already issued."
        if len(member.books_held) >= member.max_books:
            return f"Error: {member.name} has reached the max limit of {member.max_books} books."

        book.is_issued = True
        book.issued_to = member_id
        book.issue_date = date.today()
        member.books_held.append(isbn)
        return f"'{book.title}' issued to {member.name}."

    @log_call
    def return_book(self, isbn, days_late=0):
        book = self.books.get(isbn)
        if not book or not book.is_issued:
            return "Error: Book not found or was not issued."

        member = self.members.get(book.issued_to)
        fine_calculator = get_fine_calculator(member)
        fine_amount = fine_calculator.calculate(days_late)

        member.books_held.remove(isbn)
        book.is_issued = False
        book.issued_to = None
        book.issue_date = None

        if fine_amount > 0:
            return f"'{book.title}' returned. Fine due: Rs.{fine_amount:.2f}"
        return f"'{book.title}' returned. No fine."

    
    def issued_titles(self):
        return [b.title for b in self.books.values() if b.is_issued]

    def isbn_to_title_map(self):
        return {isbn: b.title for isbn, b in self.books.items()}

    def member_books_map(self):
        return {m.member_id: list(m.books_held) for m in self.members.values() if m.books_held}

    def unique_authors(self):
        return {b.author for b in self.books.values()}
    # ---------------- Generator: overdue books in batches ----------------
    def overdue_batches(self, max_days_allowed=14, batch_size=2):
        overdue = [
            b for b in self.books.values()
            if b.is_issued and (date.today() - b.issue_date).days > max_days_allowed
        ]
        for i in range(0, len(overdue), batch_size):
            yield overdue[i:i + batch_size]

    # ---------------- Search (regex) ----------------
    def search_by_title(self, pattern):
        regex = re.compile(pattern, re.IGNORECASE)
        return [b for b in self.books.values() if regex.search(b.title)]

    # ---------------- Multithreaded reminders ----------------
    def send_overdue_reminders(self):
        overdue_books = [b for b in self.books.values() if b.is_issued]

        def notify(member_id, book_title):
            time.sleep(1)   # simulate network/email delay
            member = self.members.get(member_id)
            name = member.name if member else member_id
            print(f"  -> Reminder sent to {name} about '{book_title}'")

        threads = [
            threading.Thread(target=notify, args=(b.issued_to, b.title))
            for b in overdue_books
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        print("All reminders sent.")

    # ---------------- Persistence (file handling) ----------------
    def save_state(self, filepath="library_state.json"):
        data = {
            "books": [
                {
                    "title": b.title, "author": b.author, "isbn": b.isbn,
                    "is_issued": b.is_issued, "issued_to": b.issued_to,
                    "issue_date": b.issue_date.isoformat() if b.issue_date else None,
                }
                for b in self.books.values()
            ],
            "members": [
                {
                    "type": m.__class__.__name__, "name": m.name, "member_id": m.member_id,
                    "email": m.email, "phone": m.phone, "books_held": m.books_held,
                    "roll_no": getattr(m, "roll_no", None),
                    "department": getattr(m, "department", None),
                }
                for m in self.members.values()
            ],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"State saved to {filepath}")

    def load_state(self, filepath="library_state.json"):
        with open(filepath, "r") as f:
            data = json.load(f)

        self.books.clear()
        self.members.clear()

        for bd in data["books"]:
            book = Book(bd["title"], bd["author"], bd["isbn"])
            book.is_issued = bd["is_issued"]
            book.issued_to = bd["issued_to"]
            book.issue_date = datetime.fromisoformat(bd["issue_date"]).date() if bd["issue_date"] else None
            self.books[book.isbn] = book

        for md in data["members"]:
            if md["type"] == "Student":
                member = Student(md["name"], md["member_id"], md["email"], md["phone"], md["roll_no"])
            elif md["type"] == "Faculty":
                member = Faculty(md["name"], md["member_id"], md["email"], md["phone"], md["department"])
            else:
                member = Member(md["name"], md["member_id"], md["email"], md["phone"])
            member.books_held = md["books_held"]
            self.members[member.member_id] = member

        print(f"State loaded from {filepath}")
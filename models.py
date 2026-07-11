import re
from datetime import date


class Book:
    def __init__(self, title, author, isbn):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.is_issued = False
        self.issued_to = None
        self.issue_date = None

    def __str__(self):
        status = (
            f"Issued to {self.issued_to}"
            if self.is_issued
            else "Available"
        )
        return f"'{self.title}' by {self.author} (ISBN: {self.isbn}) [{status}]"

    def __lt__(self, other):
        return self.title.lower() < other.title.lower()


class Member:
    EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$")
    PHONE_RE = re.compile(r"^\d{10}$")

    def __init__(self, name, member_id, email, phone):
        if not self.EMAIL_RE.match(email):
            raise ValueError("Invalid email address.")

        if not self.PHONE_RE.match(phone):
            raise ValueError("Phone number must contain exactly 10 digits.")

        self.name = name
        self.member_id = member_id
        self.email = email
        self.phone = phone
        self.max_books = 2
        self.books_held = []

    def __str__(self):
        return f"{self.name} ({self.member_id})"


class Student(Member):
    def __init__(self, name, member_id, email, phone, roll_no):
        super().__init__(name, member_id, email, phone)
        self.roll_no = roll_no
        self.max_books = 3


class Faculty(Member):
    def __init__(self, name, member_id, email, phone, department):
        super().__init__(name, member_id, email, phone)
        self.department = department
        self.max_books = 6


class Fine:
    RATE_PER_DAY = 1.0

    def calculate(self, days_late):
        if days_late <= 0:
            return 0.0
        return days_late * self.RATE_PER_DAY


class StudentFine(Fine):
    RATE_PER_DAY = 0.5


class FacultyFine(Fine):
    def calculate(self, days_late):
        return 0.0


def get_fine_calculator(member):
    if isinstance(member, Student):
        return StudentFine()

    if isinstance(member, Faculty):
        return FacultyFine()

    return Fine()
from flask import Flask, render_template, request, redirect, url_for, flash
from models import Book, Student, Faculty
from library import Library

app = Flask(__name__)
app.secret_key = "smart_book_repository"

library = Library()

# Load previous data if available
try:
    library.load_state()
except:
    pass


@app.route("/")
def home():
    return render_template(
        "index.html",
        books=library.books.values(),
        members=library.members.values()
    )


@app.route("/add_book", methods=["POST"])
def add_book():
    title = request.form["title"]
    author = request.form["author"]
    isbn = request.form["isbn"]

    library.add_book(Book(title, author, isbn))
    library.save_state()

    flash("Book added successfully!")
    return redirect(url_for("home"))


@app.route("/register_student", methods=["POST"])
def register_student():
    student = Student(
        request.form["name"],
        request.form["member_id"],
        request.form["email"],
        request.form["phone"],
        request.form["roll_no"]
    )

    library.register_member(student)
    library.save_state()

    flash("Student registered successfully!")
    return redirect(url_for("home"))


@app.route("/register_faculty", methods=["POST"])
def register_faculty():
    faculty = Faculty(
        request.form["name"],
        request.form["member_id"],
        request.form["email"],
        request.form["phone"],
        request.form["department"]
    )

    library.register_member(faculty)
    library.save_state()

    flash("Faculty registered successfully!")
    return redirect(url_for("home"))


@app.route("/issue", methods=["POST"])
def issue_book():
    message = library.issue_book(
        request.form["isbn"],
        request.form["member_id"]
    )

    library.save_state()
    flash(message)

    return redirect(url_for("home"))


@app.route("/return", methods=["POST"])
def return_book():
    message = library.return_book(
        request.form["isbn"],
        int(request.form["days_late"])
    )

    library.save_state()
    flash(message)

    return redirect(url_for("home"))


@app.route("/search")
def search():
    keyword = request.args.get("keyword", "")

    books = library.search_by_title(keyword)

    return render_template(
        "search.html",
        books=books,
        keyword=keyword
    )


@app.route("/save")
def save():
    library.save_state()
    flash("Library data saved.")
    return redirect(url_for("home"))


@app.route("/load")
def load():
    library.load_state()
    flash("Library data loaded.")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
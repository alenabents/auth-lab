import os
import random
from flask import Flask, render_template, request, redirect, make_response, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import User
from smtp_handler import send_email

db_user = os.getenv('POSTGRES_USER', 'admin')
db_password = os.getenv('POSTGRES_PASSWORD', 'Secret')
db_host = os.getenv('DB_HOST', '127.0.0.1')
db_port = os.getenv('DB_PORT', '55437')
db_name = os.getenv('POSTGRES_DB', 'test_db')

engine = create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
Session = sessionmaker(bind=engine)
session = Session()

app = Flask(__name__)
app.secret_key = 'superMegaSecretKey'


# Routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if session.query(User).filter_by(email=email).first():
            flash("Email already registered!", "error")
            return redirect("/register")

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        confirmation_code = str(random.randint(100000, 999999))

        new_user = User(email=email, password=hashed_password, confirmation_code=confirmation_code)
        session.add(new_user)
        session.commit()

        send_email(email, confirmation_code)
        flash("A confirmation code has been sent to your email.", "info")
        return redirect(url_for("confirm", email=email))

    return render_template("register.html")


@app.route("/auth", methods=["POST"])
def auth():
    email = request.form.get("email")
    password = request.form.get("password")

    user = session.query(User).filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        confirmation_code = str(random.randint(100000, 999999))
        user.confirmation_code = confirmation_code
        session.commit()

        send_email(email, confirmation_code)
        flash("A confirmation code has been sent to your email.", "info")
        return redirect(url_for("confirm", email=email))

    flash("Invalid email or password.", "error")
    return redirect("/")


@app.route("/confirm", methods=["GET", "POST"])
def confirm():
    email = request.args.get("email")
    user = session.query(User).filter_by(email=email).first()
    if not user:
        flash("Invalid session. Please log in again.", "error")
        return redirect("/")

    if request.method == "POST":
        code = request.form.get("code")
        if user.confirmation_code == code:
            user.is_confirmed = 1
            user.confirmation_code = None
            session.commit()

            response = make_response(redirect("/profile"))
            response.set_cookie("token", str(user.id))
            return response

        flash("Invalid confirmation code.", "error")
        return redirect(url_for("confirm", email=email))

    return render_template("confirm.html", email=email)


@app.route("/profile")
def profile():
    token = request.cookies.get("token")
    user = session.query(User).filter_by(id=token, is_confirmed=1).first()
    if not user:
        flash("You need to log in and verify your account.", "error")
        return redirect("/")
    return render_template("profile.html", email=user.email)


@app.route("/logout", methods=["POST"])
def logout():
    response = make_response(redirect("/"))
    response.set_cookie("token", "", max_age=0)
    flash("You have been logged out.", "info")
    return response


if __name__ == "__main__":
    app.run(debug=True)

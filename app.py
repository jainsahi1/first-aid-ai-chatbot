from flask import Flask, render_template, request, jsonify, redirect, session
from openai import OpenAI
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    message = db.Column(db.Text)
    response = db.Column(db.Text)

@app.before_request
def create_tables():
    db.create_all()

@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and user.password == request.form["password"]:
            session["user"] = user.id
            return redirect("/")
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        new_user = User(username=request.form["username"], password=request.form["password"])
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a safe first aid assistant."},
            {"role": "user", "content": user_message}
        ]
    )

    reply = response.choices[0].message.content

    chat = Chat(user_id=session["user"], message=user_message, response=reply)
    db.session.add(chat)
    db.session.commit()

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run()

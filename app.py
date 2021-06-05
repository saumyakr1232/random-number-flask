from flask import Flask, render_template, request, redirect, url_for, session
import pymongo
import bcrypt
import random

app = Flask(__name__)


app.secret_key = "testing"
client = pymongo.MongoClient("mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false")
db = client.get_database('randomnumber')

records = db.register

items = db.items

@app.route('/', methods=['POST','GET'])
def home():
    print("Home")
    print(session)
    if "email" in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if request.method == "POST":
        random_number = random.randint(1, 1000000)
        print(session['email'])
        new_item = {"number": random_number, "user_id": "" }
        print(new_item)
    return render_template('dashboard.html', )

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if "email" in session:
        return redirect('/dashboard')
    if request.method == "POST":
        user = request.form.get("name")
        email = request.form.get("email")

        password = request.form.get("password")

        email_found = records.find_one({'email': email})

        if email_found:
            message = 'There is a user by that email'
            return render_template('signup.html', message=message)

        else:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name':user, 'email': email, 'password': hashed}

            records.insert_one(user_input)
            return redirect('/dashboard')

    return render_template('signup.html')



@app.route('/login', methods=['GET','POST'])
def login():
    message = ""
    if "email" in session:
        return redirect('/dashboard')
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect('/dashboard')

            else:
                if "email" in session:
                    return redirect('/dashboard')
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)


@app.route("/logout")
def logout():
    if "email" in session:
        print("email in session")
        print(session)
        session.pop("email", None)
        print("after logout", session)
    return redirect('/')
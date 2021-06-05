from threading import current_thread
from flask import Flask, render_template, request, redirect, url_for, session
import pymongo
import bcrypt
import random
from datetime import datetime

app = Flask(__name__)


app.secret_key = "testing"
client = pymongo.MongoClient("mongodb+srv://admin:Jt7ahFBbfBVPfUz@cluster0.wsaho.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.get_database('randomnumber')

records = db.register

usersdata = db.usersdata

@app.route('/', methods=['POST','GET'])
def home():
    if "email" in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    items = usersdata.find().sort('date',direction=-1)
    
    if request.method == "POST":
        if "email" not in session:
            return redirect('/')
        random_number = random.randint(1, 1000)
        email = session['email']
        current_user = records.find_one({'email': email})
        date = datetime.utcnow()
        new_item = {"number": random_number, "user_id": current_user['_id'], "date":date.strftime(r"%m/%d/%Y, %H:%M:%S") }
        usersdata.insert(new_item)
        return redirect('/')
    else:
        modified_items= []
        for item in items:
            user = records.find_one({'_id': item['user_id']})
            item['name'] = user['name']
            modified_items.append(item)
        number = modified_items[0]['number'] if len(modified_items) != 0 else 0
        return render_template('dashboard.html',items=modified_items, number=number)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if "email" in session:
        return redirect('/')
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
            session["email"] = email
            records.insert_one(user_input)
            return redirect('/')

    return render_template('signup.html')



@app.route('/login', methods=['GET','POST'])
def login():
    message = ""
    if "email" in session:
        return redirect('/')
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect('/')

            else:
                if "email" in session:
                    return redirect('/')
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)


@app.route("/logout")
def logout():
    if "email" in session:
        session.pop("email", None)
    return redirect('/')


@app.after_request
def after_request(response):
    response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0') 
    return response


#TODO: clear back stack when on dashboard
from flask import Flask, render_template, request, redirect, flash
import flask_login

import pymysql

from dynaconf import Dynaconf

conf = Dynaconf(
    settings_file = ("settings.toml")
)

app = Flask(__name__)
app.secret_key = conf.secret_key

login_manager= flask_login.LoginManager()
login_manager.init_app(app)

class User:
    is_authenticated = True
    is_anonymous = False
    is_active = True

    def __init__(self, id, username, email, first_name, last_name):
        self.id = id
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM `Customer` WHERE `id` = {user_id};")

    result = cursor.fetchone()

    cursor.close
    conn.close

    if result is not None:
        return User (result["id"], result["username"], result["email"], result["first_name"], result["last_name"])


def connect_db():
    conn = pymysql.connect(
        host = "10.100.34.80",
        database = "tordonez_CatCentral",
        user = 'tordonez',
        password = conf.password,
        autocommit = True,
        cursorclass = pymysql.cursors.DictCursor
    )
    return conn

@app.route("/")
def index():
    return render_template("homepage.html.jinja")


@app.route("/browse")
def product_browse():
    query = request.args.get('query')

    conn = connect_db()

    cursor = conn.cursor()

    if query is None:
        cursor.execute("SELECT * FROM `Product`;")
    else:
        cursor.execute(f"SELECT * FROM `Product` WHERE `product_name` LIKE '%{query}%' ;")

    results = cursor.fetchall()

    return render_template("browse.html.jinja", products = results)

    cursor.close()
    conn.close()

@app.route("/product/<product_id>")
def product_page(product_id):
    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM `Product` WHERE `id` ={product_id};")

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("product.html.jinja", products = result)

@app.route("/signin")
def signin():
    return render_template("signin.html.jinja")

@app.route("/signup",methods=["POST","GET"])
def signup():
    if request.method =="POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]
        username = request.form["username"]
        address = request.form["address"]
        number = request.form["number"]
        confirm_password = request.form["confirm_password"]
        
        if password != confirm_password:
            flash("Passwords Do NOT Match")
            return render_template("signup.html.jinja")


        conn = connect_db()

        cursor = conn.cursor()

        try:
            cursor.execute(f"""
                INSERT INTO `Customer`
                    (`first_name`, `last_name`, `email`,`password`, `username`, `address`, `number`)
                VALUES
                    ( '{first_name}', '{last_name}', '{email}', '{password}', '{username}', '{address}', '{number}');
            """)
        except pymysql.err.IntegrityError:
            flash("Sorry, that username/email is already in use")
        else:
            return redirect("/signin")  
        finally:
            cursor.close()
            conn.close()
        
    return render_template("signup.html.jinja")

@app.route("/signin", methods = ["POST", "GET"])
def sign_in():
    if request.method == "POST":
        username = request.form['username'].strip()
        password = request.form['password']

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM `Customer` WHERE `username` = '{username}';")

        result = cursor.fetchone()

        if result is None:
            flash("Username/Password is incorrect")
        elif password != result["password"]:
            flash("Your username/password is incorrect")
        else:
            user = User (result["id"], result["username"], result["email"], result["first_name"], result["last_name"])

            flask_login.login_user(user)

            return redirect('/')


        return render_template("signin.html.jinja")
    

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect('/')
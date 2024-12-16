from flask import Flask, render_template, request, redirect
import pymysql
from dynaconf import Dynaconf

app = Flask(__name__)

conf = Dynaconf(
    settings_file = ("settings.toml")
)

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
        

        conn = connect_db()

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO `Customer`
                (`first_name`, `last_name`, `email`,`password`, `username`, `address`, `number`)
            VALUES
                ( '{first_name}', '{last_name}', '{email}', '{password}', '{username}');
        """)
        cursor.close()
        return redirect("signin")  
    return render_template("signup.html.jinja")
    cursor.close()
    conn.close()
from flask import Flask, render_template, request
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


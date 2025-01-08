from flask import Flask, render_template, request, redirect, flash, abort
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
login_manager.login_view = '/sign_in'

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

    result = cursor.fetchall()

    return render_template("browse.html.jinja", products = result)

    cursor.close()
    conn.close()

@app.route("/product/<id>")
def product_page(id):
    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM `Product` WHERE `id` ={id};")

    result = cursor.fetchone()
    if result is None:
        abort(404)
    cursor.close()
    conn.close()

    return render_template("product.html.jinja", product = result)

@app.route("/product/<product_id>/cart", methods = ["POST"])
@flask_login.login_required
def add_to_cart(product_id):
    qty = request.form['qty']
    customer_id = flask_login.current_user.id

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute (f"""
        INSERT INTO `Cart` (`product_id`), `customer_id`,`qty`)
        VALUES ({id}, {customer_id}, {qty})
        ON DUPLICATE KEY UPDATE
            `qty` = `qty` + {qty}
    """)


    return redirect('/cart')

@app.route("/signin")
def signin():
    if flask_login.current_user.is_authenticated:
        return redirect ("/")
    else:
        return render_template("signin.html.jinja")

@app.route("/signup",methods=["POST","GET"])
def signup():
    if flask_login.current_user.is_authenticated:
        return redirect ("/")
    else:
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

@app.route('/cart')
@flask_login.login_required
def cart():
    conn = connect_db()
    cursor = conn.cursor()

    customer_id = flask_login.current_user.id

    cursor.execute(f"""SELECT 
                   `product_name`, 
                   `price`,
                    `qty`,
                   `image_dir`,
                   `product_id`,
                   `Cart`.`id` 
                   FROM `Cart` 
                   JOIN `Product` ON `product_id` = `Product`.`id` 
                   WHERE `customer_id` = {customer_id};""")

    results = cursor.fetchall()

    total = 0
    for products in results: 
        quantity = products["qty"]
        price = products["price"]
        item_total = quantity * price
        total = item_total + total

    cursor.close()
    cursor.close()

    return render_template("cart.html.jinja", products = results, total = total)

@app.route("/cart/<cart_id>/delete", methods = ["POST"])
@flask_login.login_required
def delete_cart(cart_id):

    conn = connect_db

    cursor = conn.cursor()

    cursor.execute(f"DELETE FROM `Cart` WHERE `id` = {cart_id};")

    conn.close()
    cursor.close()

    return redirect('/cart')


@app.route("/cart/<cart_id>/delete", methods = ["POST", "GET"])
@flask_login.login_required
def update_quantity(cart_id):

    conn=connect_db()
    cursor = conn.cursor()

    cursor.execute(f"""
    UPDATE `Cart`
    SET `cart_id` = {cart_id}
    WHERE `id` = {id};
    """)

    cursor.close()
    conn.close()

    flash ("Updated Successfully")
    return redirect("/cart")

@app.route('/cart/<id>/checkout' , methods = ["POST","GET"])
@flask_login.login_required
def checkout(id):

    conn = connect_db
    cursor = conn.cursor()

    cursor.execute(f"""SELECT 
                   `product_name`, 
                   `price`,
                    `qty`,
                   `image_dir`,
                   `product_id`,
                   `Cart`.`id` 
                   FROM `Cart` 
                   JOIN `Product` ON `product_id` = `Product`.`id` 
                   WHERE `customer_id` = {id};""")

    results = cursor.fetchone()
    conn.close()
    cursor.close()

    return render_template ("checkout.hmtl.jinja",  products = results )

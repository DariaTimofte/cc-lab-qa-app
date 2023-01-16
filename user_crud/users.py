import pymysql
from tables import Users
from flask import Flask, flash, render_template, request, redirect
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret key"

# MySQL configurations
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = ""
app.config["MYSQL_DATABASE_DB"] = "cc_lab"
app.config["MYSQL_DATABASE_HOST"] = "localhost"
mysql = MySQL(app)

@app.route("/create-database")
def create_database():
    connection = None
    cursor = None
    try:
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS `cc_lab`")
        connection.commit()
        flash("Database created")
        return redirect("/")    
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        connection.close()

@app.route("/create-users-table")
def create_users_table():
    connection = None
    cursor = None
    try:
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS `users` (
            `user_id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
            `username` varchar(100), 
            `email` varchar(200), 
            `password` varchar(200))
        ''')
        connection.commit()
        flash("Users table created")
        return redirect("/")    
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        connection.close()

@app.route("/")
def users():
    connection = None
    cursor = None
    try:
        create_database()
        create_users_table()
        connection = mysql.connect()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        table = Users(rows)
        table.border = True
        return render_template("users.html", table=table)
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        connection.close()

@app.route("/new-user")
def add_user_view():
    return render_template("add_user.html")

@app.route("/add-user", methods=["POST"])
def add_user():
    connection = None
    cursor = None

    try:
        _username = request.form["username"]
        _email = request.form["email"]
        _password = request.form["password"]

        if _username and _email and _password and request.method == "POST":
            # generate hash from password
            _hash_password = generate_password_hash(_password)

            sql = "INSERT INTO users(username, email, password) VALUES(%s, %s, %s)"
            data = (_username, _email, _hash_password)

            connection = mysql.connect()
            cursor = connection.cursor()
            cursor.execute(sql, data)
            connection.commit()

            flash("User created successfully!")
            return redirect("/")
        else:
            return "There was an error when creating the user account."
    except Exception as e:
        print(e)
    finally: 
        cursor.close()
        connection.close()

@app.route("/edit-user/<int:id>")
def edit_user_view(id):
    connection = None
    cursor = None
    try:
        connection = mysql.connect()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE user_id=%s", id)
        row = cursor.fetchone()

        if row:
            return render_template("edit_user.html", row=row)
        else:
            return "Error loading #{id}".format(id=id)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()

@app.route("/update-user", methods=["POST"])
def update_user():
    connection = None
    cursor = None
    try: 
        _username = request.form["username"]
        _email = request.form["email"]
        _password = request.form["password"]
        _id = request.form["id"]
        # validate the received values
        if _username and _email and _password and _id and request.method == "POST":
            #do not save password as a plain text
            _hashed_password = generate_password_hash(_password)
            print(_hashed_password)

            # save edits
            sql = "UPDATE users SET username=%s, email=%s, password=%s WHERE user_id=%s"
            data = (_username, _email, _hashed_password, _id,)
            connection = mysql.connect()
            cursor = connection.cursor()
            cursor.execute(sql, data)
            connection.commit()

            flash("User updated successfully!")
            return redirect("/")
        else:
            return "Error while updating user"
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        connection.close()

@app.route("/delete-user/<int:id>")
def delete_user(id):
    connection = None
    cursor = None
    try:
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE user_id=%s", (id,))
        connection.commit()

        flash("User deleted successfully!")
        return redirect("/")
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        connection.close()

if __name__ == "__main__":
    app.run() 
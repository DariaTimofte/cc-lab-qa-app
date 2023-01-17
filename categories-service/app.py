import pymysql
import mysql.connector
from mysql.connector import connect, Error
from category import Categories
from flask import Flask, flash, render_template, request, redirect
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# app.secret_key = "secret key"

# # MySQL configurations
# app.config["MYSQL_DATABASE_USER"] = "root"
# app.config["MYSQL_DATABASE_PASSWORD"] = "p@ssw0rd1"
# # app.config["MYSQL_DATABASE_DB"] = "cc_lab"
# app.config["MYSQL_DATABASE_HOST"] = "mysqldb"
# mysql = MySQL(app)

@app.route('/')
def open_category_page():
    return 'BoostIQ'

@app.route('/create-database')
def createDatabase():
    with connect(host='0.0.0.0', user='root', password='p@ssw0rd1') as connection:
        try:
            drop_database_query = "DROP DATABASE IF EXISTS cc_lab"
            create_database_query = "CREATE DATABASE cc_lab"
            with connection.cursor() as cursor:
                cursor.execute(drop_database_query)
                cursor.execute(create_database_query)
                connection.commit()
                return 'Database created'

        except errors.DatabaseError:
            pass  

@app.route("/create-categories-table")
def create_categories_table():
    # connection = None
    # cursor = None
    with connect(host='0.0.0.0', user='root', password='p@ssw0rd1',database='projectdb') as connection:
        try:
            # connection = mysql.connect()
            # cursor = connection.cursor()
            with connection.cursor() as cursor:
                cursor.execute('''CREATE TABLE IF NOT EXISTS `categories` (
                    `category_id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
                    `category_text` varchar(100), 
                    `user_id` int,
                    `question_id` int,
                    FOREIGN KEY(user_id) REFERENCES users(user_id),
                    FOREIGN KEY(question_id) REFERENCES questions(question_id))
                ''')
                connection.commit()
                flash("Categories table created")
                return redirect("/")    
        except errors.ProgrammingError:
            pass
        # finally:
        #     cursor.close() 
        #     connection.close()


@app.route("/categories")
def categories():
    # connection = None
    # cursor = None
    with connect(host='0.0.0.0', user='root', password='p@ssw0rd1',database='projectdb') as connection:
        try:
        # create_categories_table()
        # connection = mysql.connect()
            with connection.cursor() as cursor:
                # cursor = connection.cursor(pymysql.cursors.DictCursor)
                cursor.execute("SELECT * FROM categories")
                rows = cursor.fetchall()
                table = Categories(rows)
                table.border = True
                return render_template("categories.html", table=table)
        except Exception as e:
            print(e)
        finally:
            cursor.close() 
            connection.close()

@app.route("/new-category")
def add_category_view():
    return render_template("add_category.html")

@app.route("/edit-category/<int:id>")
def edit_category_view(id):
    connection = None
    cursor = None
    try:
        connection = mysql.connect()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM categories WHERE category_id=%s", id)
        row = cursor.fetchone()

        if row:
            return render_template("edit_categories.html", row=row)
        else:
            return "Error loading #{id}".format(id=id)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()

@app.route("/update-category", methods=["POST"])
def update_category():
    connection = None
    cursor = None
    try: 
        _category_text = request.form["description"]
        _id = request.form["id"]
        # validate the received values
        if _category_text and request.method == "POST":
            # save edits
            sql = "UPDATE categories SET category_text=%s WHERE category_id=%s"
            data = (_category_text, _id)
            connection = mysql.connect()
            cursor = connection.cursor()
            cursor.execute(sql, data)
            connection.commit()

            flash("Category updated successfully!")
            return redirect("/categories")
        else:
            return "Error while updating category"
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        connection.close()

@app.route("/delete-categories/<int:id>")
def delete_category(id):
    connection = None
    cursor = None
    try:
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM categories WHERE category_id=%s", (id,))
        connection.commit()

        flash("Category deleted successfully!")
        return redirect("/categories")
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        connection.close()

if __name__ == "__main__":
    app.run(host ='0.0.0.0', port=5002) 
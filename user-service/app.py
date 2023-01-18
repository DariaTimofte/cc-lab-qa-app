import json
import mysql.connector
from mysql.connector import connect, Error
from tables import Users
from flask import Flask, flash, render_template, request, redirect
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = "secret"

@app.route("/create-database")
def create_database():
    with connect(host='mysqldb', user='root', password='p@ssw0rd1') as connection:
        try:
            drop_users_database = "DROP DATABASE IF EXISTS qa_app"
            create_users_database = "CREATE DATABASE qa_app"
            with connection.cursor() as cursor:
                cursor.execute(drop_users_database)
                cursor.execute(create_users_database)
                connection.commit()
                return "Database created"
        except errors.DatabaseError:
            pass

@app.route("/create-users-table")
def create_users_table():
    with connect(host='mysqldb', user='root', password='p@ssw0rd1', database='qa_app') as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute('''CREATE TABLE IF NOT EXISTS `users` (
                    `user_id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
                    `username` varchar(100), 
                    `email` varchar(200), 
                    `password` varchar(200))
                ''')
                connection.commit()
                return "Users table created"  
        except errors.ProgrammingError:
            pass

@app.route("/")
def users():
    with connect(host='mysqldb', user='root', password='p@ssw0rd1', database='qa_app') as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            row_headers=[x[0] for x in cursor.description] #this will extract row headers
            rows = cursor.fetchall()
            json_data=[]
            for result in rows:
                json_data.append(dict(zip(row_headers,result)))
            cursor.close()

        table = Users(json_data)
        table.border = True
        return render_template("users.html", table=table)

@app.route("/new-user")
def add_user_view():
    return render_template("add_user.html")

@app.route("/add-user", methods=["POST"])
def add_user():
    with connect(host='mysqldb', user='root', password='p@ssw0rd1', database='qa_app') as connection:
        _username = request.form["username"]
        _email = request.form["email"]
        _password = request.form["password"]

        if _username and _email and _password and request.method == "POST":
            # generate hash from password
            _hash_password = generate_password_hash(_password)

            sql = "INSERT INTO users(username, email, password) VALUES(%s, %s, %s)"
            data = (_username, _email, _hash_password)

            with connection.cursor() as cursor:
                cursor.execute(sql, data)
                connection.commit()

                flash("User created successfully!")
                return redirect("/")
        else:
            return "There was an error when creating the user account."

@app.route("/edit-user/<int:id>")
def edit_user_view(id):
    with connect(host='mysqldb', user='root', password='p@ssw0rd1', database='qa_app') as connection:
        select_query = "SELECT * FROM users WHERE user_id=%s"
        data_query = [id]
        with connection.cursor() as cursor:
            cursor.execute(select_query, data_query)
            row_headers=[x[0] for x in cursor.description] #this will extract row headers
            row = cursor.fetchone()
            json_data = dict(zip(row_headers,row))
            
            cursor.close()
            connection.close()

            if json_data:
                return render_template("edit_user.html", row=json_data)
            else:
                return "Error loading #{id}".format(id=id)
            
@app.route("/update-user", methods=["POST"])
def update_user():
    with connect(host='mysqldb', user='root', password='p@ssw0rd1', database='qa_app') as connection:
        try: 
            _username = request.form["username"]
            _email = request.form["email"]
            _password = request.form["password"]
            _id = request.form["id"]
            # validate the received values
            if _username and _email and _password and _id and request.method == "POST":
                #do not save password as a plain text
                _hashed_password = generate_password_hash(_password)

                # save edits
                sql = "UPDATE users SET username=%s, email=%s, password=%s WHERE user_id=%s"
                data = (_username, _email, _hashed_password, _id,)
                with connection.cursor() as cursor:
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
    with connect(host='mysqldb', user='root', password='p@ssw0rd1', database='qa_app') as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM answers WHERE user_id=%s", (id,))
            cursor.execute("DELETE FROM questions WHERE user_id=%s", (id,))
            cursor.execute("DELETE FROM users WHERE user_id=%s", (id,))
            connection.commit()

            cursor.close() 
            connection.close()
            flash("User deleted successfully!")
            return redirect("/")
            

@app.route("/new-question/<int:id>")
def add_question_view(id):
    with connect(host='mysqldb', user='root', password='p@ssw0rd1', database='qa_app') as connection:
        select_query = "SELECT * FROM users WHERE user_id=%s"
        data_query = [id]
        with connection.cursor() as cursor:
            cursor.execute(select_query, data_query)
            row_headers=[x[0] for x in cursor.description] #this will extract row headers
            row = cursor.fetchone()
            json_data = dict(zip(row_headers,row))
            
            cursor.close()
            connection.close()

            if json_data:
                return render_template("add_question.html", user=json_data)
            else:
                return "Error creating question for user #{id}".format(id=id)

@app.route("/add-question", methods=["POST"])
def add_question():
    with connect(host='mysqldb', user='root', password='p@ssw0rd1', database='qa_app') as connection:
        _question = request.form["question"]
        _category = request.form["category"]
        _id = request.form["id"]

        if _question and _category and _id and request.method == "POST":
            sql = "INSERT INTO questions(question_text, user_id, category_id) VALUES(%s, %s, %s)"
            data = [_question, _id, _category]

            with connection.cursor() as cursor:
                cursor.execute(sql, data)
                connection.commit()

                flash("Question created successfully!")
                return redirect("/")
        else:
            return "There was an error when creating the question."



if __name__ == "__main__":
    app.run(host ='0.0.0.0', port=5000) 
import mysql.connector
from mysql.connector import connect, Error
from category import Categories
from flask import Flask, flash, render_template, request, redirect

app = Flask(__name__)
app.secret_key = "secret key"

@app.route('/')
def open_category_page():
    return 'BoostIQ'

@app.route("/create-categories-table")
def create_categories_table():
    with connect(host='mysqldb', user='root', password='p@ssw0rd1', database='qa_app') as connection:
        with connection.cursor() as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS `categories` (
                `category_id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
                `category_text` varchar(100))
            ''')
            connection.commit()
            return "Categories table created"  

@app.route("/categories")
def categories():

    with connect(host='mysqldb', user='root', password='p@ssw0rd1',database='qa_app') as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM categories")
            row_headers=[x[0] for x in cursor.description] #this will extract row headers
            rows = cursor.fetchall()
            json_data=[]
            for result in rows:
                json_data.append(dict(zip(row_headers,result)))
            cursor.close()

        table = Categories(json_data)
        table.border = True
        return render_template("categories.html", table=table)

@app.route("/new-category")
def add_category_view():
    return render_template("add_category.html")

@app.route("/add-category", methods=["POST"])
def add_user():
    with connect(host='mysqldb', user='root', password='p@ssw0rd1', database='qa_app') as connection:
        _category = request.form["category"]

        if _category and request.method == "POST":
            sql = "INSERT INTO categories(category_text) VALUES(%s)"
            data = [_category]

            with connection.cursor() as cursor:
                cursor.execute(sql, data)
                connection.commit()

                flash("Category created successfully!")
                return redirect("/categories")
        else:
            return "There was an error when creating the category."


@app.route("/edit-category/<int:id>")
def edit_category_view(id):
    with connect(host='mysqldb', user='root', password='p@ssw0rd1',database='qa_app') as connection:
        select_query = "SELECT * FROM categories WHERE category_id=%s"
        data_query = [id]
        with connection.cursor() as cursor:
            cursor.execute(select_query, data_query)
            row_headers=[x[0] for x in cursor.description] #this will extract row headers
            row = cursor.fetchone()
            json_data = dict(zip(row_headers,row))
            
            cursor.close()
            connection.close()

            if json_data:
                return render_template("edit_categories.html", row=json_data)
            else:
                return "Error loading #{id}".format(id=id)

@app.route("/update-category", methods=["POST"])
def update_category():
    with connect(host='mysqldb', user='root', password='p@ssw0rd1',database='qa_app') as connection:
        with connection.cursor() as cursor:
            _category_text = request.form["description"]
            _id = request.form["id"]
            # validate the received values
            if _category_text and request.method == "POST":
                # save edits
                sql = "UPDATE categories SET category_text=%s WHERE category_id=%s"
                data = (_category_text, _id)
                cursor.execute(sql, data)
                connection.commit()

                flash("Category updated successfully!")
                return redirect("/categories")
            else:
                return "Error while updating category"

@app.route("/delete-categories/<int:id>")
def delete_category(id):
    with connect(host='mysqldb', user='root', password='p@ssw0rd1',database='qa_app') as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM questions WHERE category_id=%s", (id,))
            cursor.execute("DELETE FROM categories WHERE category_id=%s", (id,))
            connection.commit()

            flash("Category deleted successfully!")
            return redirect("/categories")

if __name__ == "__main__":
    app.run(host ='0.0.0.0', port=5002) 
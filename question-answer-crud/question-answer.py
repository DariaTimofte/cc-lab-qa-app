import pymysql
from question import Questions
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

@app.route('/')
def open_question_answer_page():
    return 'BoostIQ'
 
 
@app.route("/create-questions-table")
def create_questions_table():
    connection = None
    cursor = None
    try:
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS `questions` (
            `question_id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
            `question_text` varchar(100), 
            `answer_id` int,
            `user_id` int,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        connection.commit()
        flash("Questions table created")
        return redirect("/")    
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        connection.close()


@app.route("/create-answers-table")
def create_answers_table():
    connection = None
    cursor = None
    try:
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS `answers` (
            `answer_id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
            `answer_text` varchar(100), 
            `question_id` int,
            `user_id` int,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(question_id) REFERENCES questions(question_id))
        ''')
        cursor.execute('''
            ALTER TABLE `questions`
            ADD FOREIGN KEY (answer_id) REFERENCES answers(answer_id)
        ''')
        connection.commit()
        flash("Answers table created")
        return redirect("/")    
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        connection.close()


@app.route("/questions")
def questions():
    connection = None
    cursor = None
    try:
        create_questions_table()
        create_answers_table()
        connection = mysql.connect()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM questions")
        rows = cursor.fetchall()
        table = Questions(rows)
        table.border = True
        return render_template("questions.html", table=table)
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        connection.close()


@app.route("/edit-questions/<int:id>")
def edit_question_view(id):
    connection = None
    cursor = None
    try:
        connection = mysql.connect()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM questions WHERE question_id=%s", id)
        row = cursor.fetchone()

        if row:
            return render_template("edit_questions.html", row=row)
        else:
            return "Error loading #{id}".format(id=id)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()


@app.route("/update-question", methods=["POST"])
def update_question():
    connection = None
    cursor = None
    try: 
        _question_text = request.form["description"]
        _id = request.form["id"]
        # validate the received values
        if _question_text and request.method == "POST":
            # save edits
            sql = "UPDATE questions SET question_text=%s WHERE question_id=%s"
            data = (_question_text, _id)
            connection = mysql.connect()
            cursor = connection.cursor()
            cursor.execute(sql, data)
            connection.commit()

            flash("Question updated successfully!")
            return redirect("/questions")
        else:
            return "Error while updating question"
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        connection.close()


@app.route("/delete-questions/<int:id>")
def delete_question(id):
    connection = None
    cursor = None
    try:
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM questions WHERE question_id=%s", (id,))
        connection.commit()

        flash("Question deleted successfully!")
        return redirect("/questions")
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        connection.close()


if __name__ == "__main__":
    app.run(host ='0.0.0.0', port=5001)
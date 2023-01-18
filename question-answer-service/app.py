import mysql.connector
from mysql.connector import connect, Error
from question import Questions, Answers
from flask import Flask, flash, render_template, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret key"

@app.route('/')
def open_question_answer_page():
    return 'BoostIQ'
 
@app.route("/create-questions-table")
def create_questions_table():
    with connect(host='mysqldb', user='root', password='p@ssw0rd1', database='qa_app') as connection:
        with connection.cursor() as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS `questions` (
                `question_id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
                `question_text` varchar(100), 
                `answer_id` int,
                `user_id` int,
                `category_id` int,
                FOREIGN KEY(category_id) REFERENCES categories(category_id),
                FOREIGN KEY(user_id) REFERENCES users(user_id))
            ''')
            connection.commit()
            return "Questions table created"


@app.route("/create-answers-table")
def create_answers_table():
    with connect(host='mysqldb', user='root', password='p@ssw0rd1', database='qa_app') as connection:
        with connection.cursor() as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS `answers` (
                `answer_id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
                `answer_text` varchar(100), 
                `question_id` int,
                `user_id` int,
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(question_id) REFERENCES questions(question_id))
            ''')
            connection.commit()
            return "Answers table created"

@app.route("/questions")
def questions():
    with connect(host='mysqldb', user='root', password='p@ssw0rd1', database='qa_app') as connection:
        with connection.cursor() as cursor:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM questions")
                row_headers=[x[0] for x in cursor.description] #this will extract row headers
                rows = cursor.fetchall()
                json_data=[]
                for result in rows:
                    json_data.append(dict(zip(row_headers,result)))

                cursor.execute("SELECT * FROM answers")
                answer_row_headers=[x[0] for x in cursor.description] #this will extract row headers
                answer_rows = cursor.fetchall()
                json_data_anwers=[]
                for result in answer_rows:
                    json_data_anwers.append(dict(zip(answer_row_headers,result)))

                cursor.close()

        table = Questions(json_data)
        table.border = True

        answer_table = Answers(json_data_anwers)
        answer_table.border = True
        return render_template("questions.html", table=table, answer_table=answer_table)

@app.route("/edit-questions/<int:id>")
def edit_question_view(id):
    with connect(host='mysqldb', user='root', password='p@ssw0rd1', database='qa_app') as connection:
        select_query = "SELECT * FROM questions WHERE question_id=%s"
        data_query = [id]
        with connection.cursor() as cursor:
            cursor.execute(select_query, data_query)
            row_headers=[x[0] for x in cursor.description] #this will extract row headers
            row = cursor.fetchone()
            json_data = dict(zip(row_headers,row))

            if json_data:
                return render_template("edit_questions.html", row=json_data)
            else:
                return "Error loading #{id}".format(id=id)

@app.route("/update-question", methods=["POST"])
def update_question():
    with connect(host='mysqldb', user='root', password='p@ssw0rd1', database='qa_app') as connection:
        with connection.cursor() as cursor:
            _question_text = request.form["description"]
            _id = request.form["id"]
            _category = request.form["category"]

            # validate the received values
            if _question_text and _id and _category and request.method == "POST":
                # save edits
                sql = "UPDATE questions SET question_text=%s, category_id = %s WHERE question_id=%s"
                data = (_question_text, _category, _id)
                cursor.execute(sql, data)
                connection.commit()

                return redirect("/questions")
            else:
                return "Error while updating question"

@app.route("/delete-questions/<int:id>")
def delete_question(id):
    with connect(host='mysqldb', user='root', password='p@ssw0rd1', database='qa_app') as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM answers WHERE question_id=%s", (id,))
            cursor.execute("DELETE FROM questions WHERE question_id=%s", (id,))
            connection.commit()

            flash("Question deleted successfully!")
            return redirect("/questions")

@app.route("/answer/<int:id>/<int:user_id>")
def answer_question_view(id, user_id):
    with connect(host='mysqldb', user='root', password='p@ssw0rd1', database='qa_app') as connection:
        select_query = "SELECT * FROM questions WHERE question_id=%s"
        data_query = [id]

        select_user_query = "SELECT * FROM users WHERE user_id=%s"
        data_user_query = [user_id]
        with connection.cursor() as cursor:
            cursor.execute(select_query, data_query)
            row_headers=[x[0] for x in cursor.description] #this will extract row headers
            row = cursor.fetchone()
            json_data = dict(zip(row_headers,row))
            
            cursor.execute(select_user_query, data_user_query)
            row_headers=[x[0] for x in cursor.description] #this will extract row headers
            row = cursor.fetchone()
            json_data_user = dict(zip(row_headers,row))

            cursor.close()
            connection.close()

            if json_data:
                return render_template("add_answer.html", question=json_data, user=json_data_user)
            else:
                return "Error creating question for user #{id}".format(id=id)

@app.route("/add-answer", methods=["POST"])
def add_answer():
    with connect(host='mysqldb', user='root', password='p@ssw0rd1', database='qa_app') as connection:
        _answer = request.form["answer"]
        _id = request.form["id"]
        _user_id = request.form["user_id"]

        if _answer and _id and _user_id and request.method == "POST":
            sql = "INSERT INTO answers(answer_text, question_id, user_id) VALUES(%s, %s, %s)"
            data = [_answer, _id, _user_id]

            with connection.cursor() as cursor:
                cursor.execute(sql, data)

                answer_id_sql = "SELECT * FROM answers WHERE question_id=%s"
                answer_id_data = [_id]
                cursor.execute(answer_id_sql, answer_id_data)
                row_headers=[x[0] for x in cursor.description] #this will extract row headers
                row = cursor.fetchone()
                json_data = dict(zip(row_headers,row))

                question_update_sql = "UPDATE questions SET answer_id = %s WHERE question_id = %s"
                question_data = [json_data['answer_id'], _id]
                cursor.execute(question_update_sql, question_data)

                connection.commit()
                flash("Question created successfully!")
                return redirect("/questions")
        else:
            return "There was an error when creating the question."

if __name__ == "__main__":
    app.run(host ='0.0.0.0', port=5001)
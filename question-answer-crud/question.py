from flask_table import Table, Col, LinkCol

class Questions(Table):
    question_id = Col("id", show = False)
    question_text = Col("Question")
    user_id = Col("UserId")
    answer_id = Col("AnswerId")
    # answer = LinkCol("Answer", "answer_question_view", url_kwargs=dict(id="question_id"))
    edit = LinkCol("Edit", "edit_question_view", url_kwargs=dict(id="question_id"))
    delete = LinkCol("Delete", "delete_question", url_kwargs=dict(id="question_id"))
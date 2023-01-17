from flask_table import Table, Col, LinkCol

class Categories(Table):
    category_id = Col("id", show = False)
    category_text = Col("Category")
    user_id = Col("UserId")
    question_id = Col("QuestionId")
    # answer = LinkCol("Answer", "answer_question_view", url_kwargs=dict(id="question_id"))
    edit = LinkCol("Edit", "edit_category_view", url_kwargs=dict(id="category_id"))
    delete = LinkCol("Delete", "delete_category", url_kwargs=dict(id="category_id"))
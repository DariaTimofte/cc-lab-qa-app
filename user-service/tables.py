from flask_table import Table, Col, LinkCol

class Users(Table):
    user_id = Col("id", show = False)
    username = Col("Username")
    email = Col("Email")
    password = Col("password", show = False)
    add_question = LinkCol("Add Question", "add_question_view", url_kwargs=dict(id="user_id"))
    edit = LinkCol("Edit", "edit_user_view", url_kwargs=dict(id="user_id"))
    delete = LinkCol("Delete", "delete_user", url_kwargs=dict(id="user_id"))
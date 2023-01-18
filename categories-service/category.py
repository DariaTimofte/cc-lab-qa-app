from flask_table import Table, Col, LinkCol

class Categories(Table):
    category_id = Col("id")
    category_text = Col("Category")
    edit = LinkCol("Edit", "edit_category_view", url_kwargs=dict(id="category_id"))
    delete = LinkCol("Delete", "delete_category", url_kwargs=dict(id="category_id"))
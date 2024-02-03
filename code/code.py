from flask import Flask, render_template
import pymongo

mongo_client = pymongo.MongoClient("mongodb://admin:admin@mongodb:27017", connect=False)
db = mongo_client['tasks']
task_collection = db['tasks']

tasks_init = [
    {'task': 'Nefunguje monitor', 'requestor': 'Skladnik2', 'assignee': 'IT1', 'status': 'New', 'due_date': '14.02.2024'}
    , {'task': 'Potrebuji pridat report', 'requestor': 'Manager1', 'assignee': 'ERP1', 'status': 'In Progress', 'due_date': '17.02.2024'}
    , {'task': 'pomoc excel', 'requestor': 'Acct', 'assignee': 'IT1', 'status': 'Completed', 'due_date': '05.02.2024'}
    , {'task': 'n€funguj€ mi €', 'requestor': 'QE6', 'assignee': 'IT2', 'status': 'Completed', 'due_date': '04.02.2024'}
    , {'task': 'neumim zapnout pc', 'requestor': 'Skladnik1', 'assignee': 'IT2', 'status': 'Completed', 'due_date': '01.02.2024'}
    , {'task': 'ahoj', 'requestor': 'QE1', 'assignee': 'ERP1', 'status': 'Completed', 'due_date': '01.02.2024'}
]

task_collection.insert_many(tasks_init)

app = Flask(__name__)
app.secret_key = "super secret key"


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
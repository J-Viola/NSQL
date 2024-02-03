from flask import Flask, render_template, request, redirect, session, flash, url_for
import pymongo

mongo_client = pymongo.MongoClient("mongodb://admin:admin@mongodb:27017", connect=False)
db = mongo_client['helpdesk']
task_collection = db['tasklist']
users_collection = db['helpdeskuser']

task_collection.drop()
users_collection.drop()


tasks_init = [
    {'id': '6', 'task': 'Nefunguje monitor', 'requestor': 'Skladnik2', 'assignee': 'IT1', 'status': 'New', 'due_date': '14.02.2024'}
    , {'id': '5', 'task': 'Potrebuji pridat report', 'requestor': 'Manager1', 'assignee': 'ERP1', 'status': 'In Progress', 'due_date': '17.02.2024'}
    , {'id': '4', 'task': 'pomoc excel', 'requestor': 'Acct', 'assignee': 'IT1', 'status': 'Completed', 'due_date': '05.02.2024'}
    , {'id': '3', 'task': 'n€funguj€ mi €', 'requestor': 'QE2', 'assignee': 'IT2', 'status': 'Completed', 'due_date': '04.02.2024'}
    , {'id': '2', 'task': 'neumim zapnout pc', 'requestor': 'Skladnik1', 'assignee': 'IT2', 'status': 'Completed', 'due_date': '01.02.2024'}
    , {'id': '1', 'task': 'ahoj', 'requestor': 'QE1', 'assignee': 'ERP1', 'status': 'Completed', 'due_date': '01.02.2024'}
]

users_init = [
    {'userid': '1', 'username': 'ERP1', 'password': 'helpdesk'}
    , {'userid': '2', 'username': 'IT1', 'password': 'helpdesk'}
    , {'userid': '3', 'username': 'IT2', 'password': 'helpdesk'}
]

task_collection.insert_many(tasks_init)
users_collection.insert_many(users_init)

app = Flask('code.py')
app.secret_key = "super secret key"


@app.route('/')
@app.route('/index')
def index():
    tasks = task_collection.find(sort=[('id', pymongo.DESCENDING)])
    return render_template('index.html', tasklist=tasks)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = users_collection.find_one({'username': username})

        if user and user['password'] == password:
            session['user_is_authenticated'] = True
            session['user'] = username
            flash('Login successful!', 'success')
        else:
            flash('Login failed. Please check your credentials.', 'error')
    return redirect('index')


@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session for logging out
    session.clear()
    flash('Successfuly logged out.', 'Logout successful!')
    return redirect('index')


# delete + edit

@app.route('/form', methods=['GET', 'POST'])
def form():

    assignee_list = users_collection.distinct('username')
    status_list = [
        'New'
        , 'In Process'
        , 'Completed'
        , 'Closed'
        , 'Awaiting Additional Info'
        , 'Long Term Project'
    ]

    if request.method == 'POST':
        task = request.form.get('task')
        requestor = request.form.get('requestor')
        assignee = request.form.get('assignee')
        status = request.form.get('status')
        duedate = request.form.get('duedate')

        highestid = task_collection.find_one(sort=[('id', pymongo.DESCENDING)])
        newid = int(highestid['id']) + 1 if highestid else 1

        result = task_collection.insert_one({
            'id': str(newid)
            , 'task': task
            , 'requestor': requestor
            , 'assignee': assignee
            , 'status': status
            , 'due_date': duedate
        })
        if result.acknowledged:
            flash('Ticket submitted succesfully.', 'success')
        else:
            flash('Failed to submit', 'error')
    return render_template('form.html', assignees=assignee_list, statuses=status_list)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)

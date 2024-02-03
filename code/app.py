from flask import Flask, render_template, request, redirect, session, flash, url_for
import pymongo

mongo_client = pymongo.MongoClient("mongodb://admin:admin@mongodb:27017", connect=False)
db = mongo_client['helpdesk']
task_collection = db['tasklist']
users_collection = db['helpdeskuser']

task_collection.drop()
users_collection.drop()


tasks_init = [
    {'id': '6', 'task': 'Nefunguje monitor', 'requestor': 'Skladnik2', 'assignee': 'IT1', 'status': 'New', 'due_date': '2024-02-14'}
    , {'id': '5', 'task': 'Potrebuji pridat report', 'requestor': 'Manager1', 'assignee': 'ERP1', 'status': 'In Progress', 'due_date': '2024-02-17'}
    , {'id': '4', 'task': 'pomoc excel', 'requestor': 'Acct', 'assignee': 'IT1', 'status': 'Completed', 'due_date': '2024-02-05'}
    , {'id': '3', 'task': 'n€funguj€ mi €', 'requestor': 'QE2', 'assignee': 'IT2', 'status': 'Completed', 'due_date': '2024-02-04'}
    , {'id': '2', 'task': 'neumim zapnout pc', 'requestor': 'Skladnik1', 'assignee': 'IT2', 'status': 'Completed', 'due_date': '2024-02-01'}
    , {'id': '1', 'task': 'ahoj', 'requestor': 'QE1', 'assignee': 'ERP1', 'status': 'Completed', 'due_date': '2024-02-01'}
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


@app.route('/edit_ticket', methods=['GET', 'POST'])
def edit_ticket():
    if request.method == 'GET':
        ticket_id = request.args.get('id')
        ticket = task_collection.find_one({'id': ticket_id})
        return render_template('tasks.html', ticket=ticket)

    elif request.method == 'POST':
        ticket_id = request.form.get('id')
        existing_ticket = task_collection.find_one({'id': ticket_id})

        if existing_ticket:
            updated_fields = {
                'task': request.form.get('task'),
                'requestor': request.form.get('requestor'),
                'assignee': request.form.get('assignee'),
                'status': request.form.get('status'),
                'due_date': request.form.get('duedate')
            }
            task_collection.update_one({'id': ticket_id}, {'$set': updated_fields})
            flash('Ticket updated successfully.', 'success')
            return redirect(url_for('manage'))

        else:
            flash('Ticket not found!', 'error')
            return redirect(url_for('manage'))


@app.route('/delete_ticket', methods=['GET'])
def delete_ticket():
    ticket_id = request.args.get('id')
    deletion = task_collection.delete_one({'id': ticket_id})
    if deletion.deleted_count > 0:
        flash('Ticket deleted succesfully.', 'success')
    else:
        flash('Ticket was not deleted.', 'error')
    return redirect(url_for('manage'))


@app.route('/manage', methods=['GET', 'POST'])
def manage():
    if request.method == 'GET':
        id_list = task_collection.distinct('id')
        return render_template('manage.html', ids=id_list)

    elif request.method == 'POST':
        ticket_id = request.form.get('id')
        ticket = task_collection.find_one({'id': ticket_id})

        if ticket:
            session['ticket_listed'] = True
            session['ticket'] = str(ticket)
            session['ticket_id'] = ticket['id']
            session['ticket_task'] = ticket['task']
            session['ticket_requestor'] = ticket['requestor']
            session['ticket_assignee'] = ticket['assignee']
            session['ticket_status'] = ticket['status']
            session['ticket_duedate'] = ticket['due_date']

        return redirect(url_for('manage'))


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)

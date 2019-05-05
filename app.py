from flask import Flask, request, flash, redirect, url_for
from flask import send_from_directory
from flask import render_template
from wtforms import Form, StringField, PasswordField, validators
from pymongo import MongoClient, errors
import pandas as pd
import os
# import run_all_contact_crawlers
import datetime
from readabledelta import readabledelta
from multiprocessing import Process


DEBUG = True  # False is for production
from mongo_credentials import MONGO_URL
if DEBUG:
    contacts_collection = MongoClient(MONGO_URL).contacts.real_estate_agent_contacts
else:
    contacts_collection = MongoClient(MONGO_URL).contacts.real_estate_agent_contacts


class RegistrationForm(Form):
    name = StringField('First Name', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "data/"


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/test', methods=['GET', 'POST'])
def test():
    return render_template('sign_in.html', test='Username and Password are: test')

@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    form = RegistrationForm(request.form)
    if request.method == 'POST':
        name = form.name.data
        password = form.password.data
        print(name)
        print(password)
        print(os.environ.get('USERNAME'))
        print(os.environ.get('PASSWORD'))
        if name == os.environ.get('USERNAME') and password == os.environ.get('PASSWORD'):
            return redirect(url_for('contacts', api_key=os.environ.get('API_KEY')))
        elif name == '' and password == '':
            pass
        else:
            return render_template('sign_in.html', form=form, test='Wrong Username or Password.')

    return render_template('sign_in.html', form=form)


@app.route('/contacts/', methods=['GET', 'POST'])
@app.route('/contacts/<api_key>', methods=['GET', 'POST'])
def contacts(api_key=None):
    if request.method == 'POST':
        api_key = request.form.get('api_key')
        return redirect(url_for('contacts', api_key=api_key))
    if not api_key:
        return render_template('index.html', error='Missing API-key. Please Sign in.')
    elif os.environ.get('API_KEY') != api_key:
        return render_template('index.html', error='Wrong API-key. Please Sign in.')

    date = contacts_collection.find().sort([("timestamp", -1)]).limit(1)
    updated_date = readabledelta(round_to_hour(datetime.datetime.now()) - round_to_hour(date[0]['timestamp']))
    contact_count = contacts_collection.count()
    agency_count = len(contacts_collection.distinct("company"))
    return render_template('contacts.html', api_key=api_key, contact_count=contact_count, updated_date=updated_date, agency_count=agency_count)

def round_to_hour(dt):
    dt_start_of_hour = dt.replace(minute=0, second=0, microsecond=0)
    dt_half_hour = dt.replace(minute=30, second=0, microsecond=0)

    if dt >= dt_half_hour:
        # round up
        dt = dt_start_of_hour + datetime.timedelta(hours=1)
    else:
        # round down
        dt = dt_start_of_hour

    return dt

@app.route('/download', methods=['GET', 'POST'])
def download():
    api_key = request.form.get('api_key')
    if not api_key:
        return render_template('index.html', error='Missing API-key. Please Sign in.')
    elif os.environ.get('API_KEY') != api_key:
        return render_template('index.html', error='Wrong API-key. Please Sign in.')
    else:
        update_contacts_csv_file()
        return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename='contacts.csv', as_attachment=True)

def update_contacts_csv_file():
    # Creating CSV file
    contacts_collection = MongoClient(
        MONGO_URL).contacts.real_estate_agent_contacts
    df = pd.DataFrame(list(contacts_collection.find()))
    df.to_csv('data/contacts.csv', sep=';')

@app.route('/update', methods=['GET', 'POST'])
def update():
    api_key = request.form.get('api_key')
    if not api_key:
        return render_template('index.html', error='Missing API-key. Please Sign in.')
    elif os.environ.get('API_KEY') != api_key:
        return render_template('index.html', error='Wrong API-key. Please Sign in.')
    else:
        date = contacts_collection.find().sort([("timestamp", -1)]).limit(1)
        updated_date = (datetime.datetime.now()) - (date[0]['timestamp'])
        if updated_date < datetime.timedelta(hours=2):
            return render_template('contacts.html', api_key=api_key, error='Contacts.csv has been updated less that 2 hours ago.')            
        else:
            # p = Process(target=run_all_contact_crawlers.run_all_crawlers_one_by_one())
            # p.start()
            return render_template('contacts.html', api_key=api_key, error='Contacts.csv file is now updating')
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=DEBUG)


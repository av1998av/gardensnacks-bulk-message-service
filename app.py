import datetime
import mailer
import json
import os
from dotenv import load_dotenv

load_dotenv()

def mailer_job(email, templateId):
    mailer.SendDynamic(email, templateId)
    
def whatsapp_job(email, templateId):
    return

from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.date import DateTrigger
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from flask import request
from models import db, MessageGroupUser

database_host: str = os.getenv('DATABASE_HOST')
database_username: str = os.getenv('DATABASE_USERNAME')
database_password: str = os.getenv('DATABASE_PASSWORD')
database_name: str = os.getenv('DATABASE_NAME')
database_url = "mysql+pymysql://"+database_username+":"+database_password+"@"+database_host+"/"+database_name
test_sendgrid_template = os.getenv('TEST_TEMPLATE_ID')

jobstores = {
    'default': SQLAlchemyJobStore(url=database_url,tablename='apscheduler_jobs')
}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

scheduler = BackgroundScheduler(jobstores=jobstores,executors=executors,job_defaults=job_defaults)

app = Flask(__name__)

scheduler.start()

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
db.init_app(app)

@app.route('/messageGroupUsers', methods=['GET'])
def list_messagegroup_users():
    data = MessageGroupUser.query.all()
    result = [z.to_json() for z in data]
    return jsonify(result)

@app.route('/jobs', methods = ['GET', 'POST', 'DELETE'])
def jobs():
    if request.method == 'GET':
        result = []
        for job in scheduler.get_jobs():
            print(job.next_run_time)
            result.append({
                'name' : job.name,
                'next_run_time' : str(job.next_run_time)
			})
        return result
    elif request.method == 'POST':
        timestamp = datetime.datetime(2024, 10, 17, 1, 19)
        job = scheduler.add_job(mailer_job,DateTrigger(run_date=timestamp),args=['test_email',test_sendgrid_template],id="test",second='*/20',jobstore='default')
        result = []
        for job in scheduler.get_jobs():
            print(job.next_run_time)
            result.append({
                'name' : job.name,
                'next_run_time' : str(job.next_run_time)
			})
        return result
    elif request.method == 'DELETE':
        scheduler.remove_job("test")
        result = []
        for job in scheduler.get_jobs():
            print(job.next_run_time)
            result.append({
                'name' : job.name,
                'next_run_time' : str(job.next_run_time)
			})
        return result

if __name__ == '__main__':
    app.run(debug=True)
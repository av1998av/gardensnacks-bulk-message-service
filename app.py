import datetime
import mailer
import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.date import DateTrigger
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from flask import request
from models import db, MessageGroupUser, MessageGroup, Job
from functools import wraps
import jwt

database_host: str = os.getenv('DATABASE_HOST')
database_username: str = os.getenv('DATABASE_USERNAME')
database_password: str = os.getenv('DATABASE_PASSWORD')
database_name: str = os.getenv('DATABASE_NAME')
jwt_secret: str = os.getenv('JWT_SECRET')
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

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
        try:
            data = jwt.decode(token, jwt_secret, algorithms=["HS256"])            
        except Exception as e:            
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        return  f(*args, **kwargs)
  
    return decorated

@app.route('/messageGroupUsers', methods=['GET'])
@token_required
def list_messagegroup_users():
    data = MessageGroupUser.query.all()
    result = [z.to_json() for z in data]
    return jsonify(result)

@app.route('/jobs', methods = ['GET', 'POST', 'DELETE'])
@token_required
def jobs():
    if request.method == 'GET':
        result = []
        for job in scheduler.get_jobs():
            result.append({
                'name' : job.name,
                'next_run_time' : str(job.next_run_time)
			})
        return result
    elif request.method == 'POST':
        input = request.get_json()
        timestamp = datetime.datetime.strptime(input['timestamp'], "%Y-%m-%dT%H:%M:%S")
        job = Job(input['messageGroupId'], input['templateId'], timestamp)
        job = scheduler.add_job(mailer_job,DateTrigger(run_date=job.timestamp),args=[job.messageGroupId,job.templateId],id="test",jobstore='default')
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
    
def mailer_job(messageGroupId, templateId):
    with app.app_context():
        messageGroupUsers = MessageGroupUser.query.filter_by(groupId=messageGroupId).all()
        for item in messageGroupUsers:
            mailer.SendDynamic(item.emailOrPhone, templateId)
    
if __name__ == '__main__':
    app.run(debug=True)
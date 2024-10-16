import os
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient
from dotenv import load_dotenv

load_dotenv()

test_sendgrid_template = os.getenv('TEST_TEMPLATE_ID')
sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
from_email = os.getenv('FROM_EMAIL')

def SendDynamic(to_email,template_id):
    message = Mail(
        from_email=from_email,
        to_emails=to_email)
    message.dynamic_template_data = {
        'content' : 'Mail content'
    }
    message.template_id = template_id
    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        code, body, headers = response.status_code, response.body, response.headers
        print(f"Response code: {code}")
        print(f"Response headers: {headers}")
        print(f"Response body: {body}")
        print("Dynamic Messages Sent!")
    except Exception as e:
        print("Error: {0}".format(e))
    return str(response.status_code)
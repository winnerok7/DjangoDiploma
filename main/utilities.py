from django.template.loader import render_to_string
from django.core.signing import Signer
from DjBoard.settings import ALLOWED_HOSTS
from datetime import datetime
from os.path import splitext

signer = Signer()

def send_activn(user):
    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0]
    else:
        host = 'http://localhost:8000'
    context = {'user': user, 'host': host,'sign': signer.sign(user.username)}
    subject = render_to_string('email/activation_letter_topic.txt',context)
    body_text = render_to_string('email/activation_letter_body.txt', context)
    user.email_user(subject, body_text)

def get_time_marker(instanse,filename):
    return '%s%s' % (datetime.now().timestamp(),splitext(filename)[1])


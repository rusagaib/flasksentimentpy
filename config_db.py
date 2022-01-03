import os
from os.path import join, dirname
from dotenv import load_dotenv


# dotenv_path = join(dirname(__file__), '.env')
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# prod
database_username=os.environ.get('usernamenya')
database_password=os.environ.get('passwordnya')
database_ip=os.environ.get('db_ip')
database_name=os.environ.get('db_name')
secret_key=os.environ.get('SECRET_KEY')
# salt=os.environ.get('SALT')
env=os.environ.get('FLASK_ENV')
FILENAMES=os.environ.get('FILENAMES')
assets_dir=FILENAMES+'/assets/'

# static_folder = os.path.join('static')
# assets_dir = os.path.join('assets')
# resource_dir = os.path.join('resource')
# debugging on
# debug=os.environ.get('debug')

# print(database_username)
# print(database_password)
# print(database_ip)
# print(database_name)



# class Config(object):
#     # ...
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
#         'sqlite:///' + os.path.join(basedir, 'app.db')
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

# CONSUMER_KEY=os.environ.get("API_KEY")
# CONSUMER_SECRET=os.environ.get('API_secret')
# ACCESS_TOKEN=os.environ.get('Access_token')
# ACCESS_TOKEN_SECRET=os.environ.get('Access_token_secret')

# def progress(count, total, suffix=''):
#     bar_len = 60
#     filled_len = int(round(bar_len * count / float(total)))
#
#     percents = round(100.0 * count / float(total), 1)
#     bar = '=' * filled_len + '-' * (bar_len - filled_len)
#
#     sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
#     sys.stdout.flush()  # As suggested by Rom Ruben

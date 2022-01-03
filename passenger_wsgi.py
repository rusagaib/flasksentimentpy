# import sys
# import os

# add your project directory to the sys.path
# project_home=os.getenv('FILENAMES')
# project_home='/home/rusagaib/erhost/sentimenpy_prod/sentimentpy/app'
# project_home = '~/erhost/sentimenpy_prod/sentimentpy/app'
# if project_home not in sys.path:
#     sys.path.insert(0, project_home)

from main_app import app as application

import os
from setuptools import setup, find_packages

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

requirements = '''
boto3==1.7.41
django>=1.8
pytz
'''

setup(
    name='django_aws_s3_sync',
    version='1.0',
    packages=find_packages(),
    url='',
    license='',
    author='ccortinhas',
    author_email='ccortinhas@ubiwhere.com',
    description='Management command that sync local files with AWS S3 with some custom options',
    install_requires=requirements
)

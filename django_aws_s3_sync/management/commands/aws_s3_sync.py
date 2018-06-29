import threading

from django.core.management import BaseCommand

import boto3
import os
import pytz
import re
import sys
from datetime import datetime

from django.conf import settings


class Command(BaseCommand):
    help = '''
    Performs AWS S3 synchronization and deletes older copies of Postgres Backups in S3. It detects the backup files
    that have the following structure (default structure created by 'dbbackup' and 'mediabackup' django extensions):
    
    dbbackup: default-fe3c82a21f92-2018-06-20-105612.psql.bin ;
    
    mediabackup: fe3c82a21f92-2018-06-20-111443.tar.gz (with compression)
    '''

    show_progress = False
    bucket_name = ''
    number_backups_to_keep = 2
    aws_key_id = ''
    aws_secret_key = ''

    # Base directory where the backups will be
    backup_directory = ''
    # Directories of the Daily and Weekly backups
    DAILY = ''
    WEEKLY = ''

    def add_arguments(self, parser):
        parser.add_argument('--progress',
                            action='store_true',
                            help='Shows the progress of the upload files')
        parser.add_argument('--bucket_name',
                            type=str,
                            default=getattr(settings, 'AWS_STORAGE_BACKUPS_BUCKET_NAME', None),
                            help='Specify Amazon S3 Bucket name. Default: AWS_STORAGE_BACKUPS_BUCKET_NAME in django'
                                 ' settings')
        parser.add_argument('--n_backups',
                            type=int,
                            default=getattr(settings, 'AWS_NUMBER_BACKUPS_TO_KEEP', 4),
                            help='Number of Postgres backups to keep in S3. Default=2 or AWS_NUMBER_BACKUPS_TO_KEEP '
                                 'defined in django settings')
        parser.add_argument('--aws_key_id',
                            type=str,
                            default=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
                            help='Amazon S3 username. Default: AWS_ACCESS_KEY_ID in django settings.')
        parser.add_argument('--aws_secret_key',
                            type=str,
                            default=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
                            help='Amazon S3 password. Default: AWS_SECRET_ACCESS_KEY in django settings')
        parser.add_argument('--backup_dir',
                            type=str,
                            default=getattr(settings, 'AWS_LOCAL_BASE_DIRECTORY', None),
                            help='Directory to sync with Amazon. Default: AWS_LOCAL_BASE_DIRECTORY in django settings')
        parser.add_argument('--daily_backup_subdir',
                            type=str,
                            default=getattr(settings, 'AWS_DAILY_BACKUP_SUBDIR', None),
                            help='Directory that contains the daily backups. Default: AWS_DAILY_BACKUP_SUBDIR in '
                                 'django settings')
        parser.add_argument('--weekly_backup_subdir',
                            type=str,
                            default=getattr(settings, 'AWS_WEEKLY_BACKUP_SUBDIR', None),
                            help='Directory that contains the weekly backups. Default: AWS_WEEKLY_BACKUP_SUBDIR in '
                                 'django settings')

    def login(self):
        try:
            session = boto3.Session(
                aws_access_key_id=self.aws_key_id,  # settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=self.aws_secret_key,  # settings.AWS_SECRET_ACCESS_KEY
            )
        except AttributeError:
            self.stdout.write('No AWS credentials were found in the Django settings')
            return
        s3 = session.resource('s3')
        return s3

    def upload_file(self, bucket, local_file, aws_key):
        s3_key = list(bucket.objects.filter(Prefix=aws_key))
        if len(s3_key) > 0:
            s3_datetime = s3_key[0].last_modified
            local_datetime = datetime.utcfromtimestamp(
                os.stat(local_file).st_mtime).replace(tzinfo=pytz.utc)

            if local_datetime < s3_datetime:
                # self.stdout.write('s3 file is newer, no new version will be uploaded... file: {}'.format(aws_key))
                return
        if self.show_progress:
            bucket.upload_file(local_file, aws_key, Callback=ProgressPercentage(local_file))
        else:
            bucket.upload_file(local_file, aws_key)

    def sync_files_with_s3(self, bucket):

        for root, dirs, files in os.walk(self.backup_directory):
            aws_root = root.replace(self.backup_directory, '')

            for f in files:
                local_file = root + '/' + f

                if aws_root == '':
                    aws_key = f
                    self.upload_file(bucket, local_file, aws_key)
                else:
                    aws_key = aws_root + '/' + f
                    self.upload_file(bucket, local_file, aws_key)

    def delete_older_files_by_modified_date(self, aws_list):
        if len(aws_list) > self.number_backups_to_keep:
            aws_list.sort(key=lambda item: item.last_modified, reverse=False)
            for i in range(0, len(aws_list) - self.number_backups_to_keep):
                aws_list[i].delete()

    @staticmethod
    def get_date_from_filename(item):
        r = re.search(r'[\w\d]{12}-(\d{4}-\d{2}-\d{2}-\d{6})', item.key)
        return datetime.strptime(r.group(1), '%Y-%m-%d-%H%M%S')

    def delete_older_files_by_filename_date(self, aws_list):
        if len(aws_list) > self.number_backups_to_keep:
            aws_list.sort(key=lambda item: self.get_date_from_filename(item), reverse=False)
            for i in range(0, len(aws_list) - self.number_backups_to_keep):
                aws_list[i].delete()

    def handle_old_files(self, bucket, folder):

        aws_postgres_objects = []
        aws_media_objects = []
        for o in bucket.objects.all():

            if o.key.startswith(folder):
                # This regex checks for the media backup generated by dbbackup
                r = re.search(r'[\w\d]{12}-(\d{4}-\d{2}-\d{2}-\d{6}).tar.gz', o.key)
                if r:
                    aws_media_objects.append(o)

                # This regex checks for the postgres backup generated by dbbackup
                r = re.search(r'default-[\w\d]{12}-(\d{4}-\d{2}-\d{2}-\d{6}).psql.bin', o.key)
                if r:
                    aws_postgres_objects.append(o)

        # self.delete_older_files_by_modified_date(aws_media_objects)
        self.delete_older_files_by_filename_date(aws_media_objects)
        self.delete_older_files_by_filename_date(aws_postgres_objects)

    def handle(self, *args, **options):
        self.show_progress = options['progress']
        self.bucket_name = options['bucket_name']
        if self.bucket_name is None:
            self.stdout.write('No bucket name specified. Exiting.')
            return
        self.number_backups_to_keep = options['n_backups']
        self.aws_key_id = options['aws_key_id']
        if self.aws_key_id is None:
            self.stdout.write('No aws key id specified. Exiting.')
            return
        self.aws_secret_key = options['aws_secret_key']
        if self.aws_secret_key is None:
            self.stdout.write('No aws secret key specified. Exiting.')
            return
        self.backup_directory = options['backup_dir']
        if os.path.isdir(self.backup_directory) is False:
            self.stdout.write('{} is not a valid directory. Exiting.'.format(self.backup_directory))
            return
        self.DAILY = options['daily_backup_subdir']
        self.WEEKLY = options['weekly_backup_subdir']

        s3 = self.login()
        if s3 is None:
            return
        bucket = s3.Bucket(self.bucket_name)

        if bucket.creation_date:
            self.stdout.write('Accessing bucket: {}'.format(bucket))
        else:
            self.stdout.write('No bucket with that name, or no permission to access it! Exiting.')
            return

        if self.backup_directory:
            self.sync_files_with_s3(bucket)
        else:
            self.stdout.write('Backup directory not set. Exiting.')
            return

        if self.DAILY:
            self.handle_old_files(bucket, self.DAILY)
        if self.WEEKLY:
            self.handle_old_files(bucket, self.WEEKLY)


# Callback used to keep progress of the uploads
class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()

    def __del__(self):
        sys.stdout.write('\n')

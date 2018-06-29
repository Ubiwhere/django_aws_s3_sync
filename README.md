# Django AWS S3 Synchronization

Django management command that synchronizes local files with a given S3 bucket and performs backup rotation on S3 keeping only the most recent

## Features:

Additionally to synchronizing the local directory with S3 this management command will also analyze the files in the backup directories (meant for postgres backups and media backups) and it will only keep the more recent ones, how many are kept is defined in  `AWS_NUMBER_BACKUPS_TO_KEEP` in django settings and defaults to 2 if not present.  

## Usage:

After installing (eg. `pip install git+https://github.com/Ubiwhere/django_aws_s3_sync.git`) just add `django_aws_s3_sync` to the installed apps:

```python
INSTALLED_APPS = {
    (...),
    'django_aws_s3_sync',
}
```

Optionally you can also add the following to the settings.py, they will work as defaults:

```python
AWS_STORAGE_BACKUPS_BUCKET_NAME = 'test-bucket'
AWS_NUMBER_BACKUPS_TO_KEEP = 4
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_LOCAL_BASE_DIRECTORY = '/some/dir/example/'
AWS_DAILY_BACKUP_SUBDIR = 'daily'
AWS_WEEKLY_BACKUP_SUBDIR = 'weekly'
```
Note: the daily/weekly directories should point to the location of the backups performed by dbbackup and mediabackup

`python manage.py aws_s3_sync --help` will give you the following

```bash
optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output,
                        2=verbose output, 3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g.
                        "myproject.settings.main". If this isn't provided, the
                        DJANGO_SETTINGS_MODULE environment variable will be
                        used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g.
                        "/home/djangoprojects/myproject".
  --traceback           Raise on CommandError exceptions
  --no-color            Don't colorize the command output.
  --progress            Shows the progress of the upload files
  --bucket_name BUCKET_NAME
                        Specify Amazon S3 Bucket name. Default:
                        AWS_STORAGE_BACKUPS_BUCKET_NAME in django settings
  --n_backups N_BACKUPS
                        Number of Postgres backups to keep in S3. Default=2 or
                        AWS_NUMBER_BACKUPS_TO_KEEP defined in django settings
  --aws_key_id AWS_KEY_ID
                        Amazon S3 username. Default: AWS_ACCESS_KEY_ID in
                        django settings.
  --aws_secret_key AWS_SECRET_KEY
                        Amazon S3 password. Default: AWS_SECRET_ACCESS_KEY in
                        django settings
  --backup_dir BACKUP_DIR
                        Directory to sync with Amazon. Default:
                        AWS_LOCAL_BASE_DIRECTORY in django settings
  --daily_backup_subdir DAILY_BACKUP_SUBDIR
                        Directory that contains the daily backups. Default:
                        AWS_DAILY_BACKUP_SUBDIR in django settings
  --weekly_backup_subdir WEEKLY_BACKUP_SUBDIR
                        Directory that contains the weekly backups. Default:
                        AWS_WEEKLY_BACKUP_SUBDIR in django settings
``` 

## Todo:

- Customize extensions for the backups (psql, psql.bin, tar, tar.gz, etc)
- Add parameter for custom regex expressions for other file patterns
- Currently it is checking the timestamp from the file name instead of the modified date
- Add argument for healthcheck after a successful synchronization
- Add exclude parameter for directories and files
- Tests...
# Django AWS S3 Synchronization

## Usage:

After installing (eg. `pip install git+https://github.com/Ubiwhere/django_aws_s3_sync.git`) just add `django_aws_s3_sync` to the installed apps:

```python
INSTALLED_APPS = {
    (...),
    'django_aws_s3_sync',
}
```

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
                        Number of Postgres backups to keep in S3. Default=2
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

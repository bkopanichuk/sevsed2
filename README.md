## Installation

Створити базу даних postgresql

```bash
sudo su postgres

#створити базу
createdb sed_test_db

psql
```
```sql
CREATE USER sed_user WITH PASSWORD 'sed_user';
ALTER USER sed_user CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE "sed_test_db" to sed_user;
ALTER ROLE sed_user SUPERUSER;
CREATE EXTENSION IF NOT EXISTS ltree;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION postgis version '3.0.1';
\q
```

## Імпорт базових налаштувань

```bash
python manage.py loaddata apps/l_core/fixtures/initial_auth_data.json
python manage.py loaddata apps/l_core/fixtures/initial_lcore.json
python manage.py loaddata apps/document/fixtures/inital_dict.json
```
Прописати вірний абсолютний члях до папки з кореневими сертифікатами в файлі  osplm.ini.
змінити параметр Path в блоці [\SOFTWARE\Institute of Informational Technologies\Certificate Authority-1.3\End User\FileStore]

## Запуск celery  в дебаг режимі
```bash
celery -A config worker -l INFO
```

[program:celery_tasks]
command=/data/sev_statement_env/bin/celery worker -A sev_statement  --loglevel=INFO
directory=/data/sev_statement
user=root
numprocs=1
stdout_logfile=/var/log/celery/sev_celery_worker.log
stderr_logfile=/var/log/celery/sev_celery_worker_error.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs = 600
killasgroup=true
priority=998

supervisord -n -c /etc/supervisord.conf



## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
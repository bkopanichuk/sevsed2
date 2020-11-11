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
python manage.py loaddata apps/l_core/fixtures/initial_organization.json
python manage.py loaddata apps/document/fixtures/inital_dict.json
```
Прописати вірний абсолютний члях до папки з кореневими сертифікатами в файлі  osplm.ini.
змінити параметр Path в блоці [\SOFTWARE\Institute of Informational Technologies\Certificate Authority-1.3\End User\FileStore]

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
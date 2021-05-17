## Create and Activate Virtual Environment
```PowerShell
.\daft\Scripts\activate
```

## Start Localhost Server with Unicorn
```PowerShell
python -m uvicorn main:app --port 5555
# Uvicorn running on http://127.0.0.1:5555
```

## Run Pytest's test cases
```PowerShell
pytest tests.py
```

<hr>

# Docer and Postgres and Heroku
## 0. Download Postgres (add to PATH), Docker, Docker Compose and Heroku CLI

## 1. Start Postgres DB locally. Make sure docker is running.
```PowerShell
docker-compose up -d postgres
docker-compose up 
docker ps
docker exec -it daftacademy_postgres_1 /bin/bash # root@d6b636ef2239:/#
```

## 2. Inside Postgres Containter
```PowerShell
psql -U postgres # postgres=#
```

## 3. Import to Postgres and provide password from docker-compose.yml
```PowerShell
psql -h 127.0.0.1 -p 5555 -U postgres -f northwind.postgre.sql
# 5555 - Postgres Containter port exposed by Docker 
```

## 4. Inside Postgres Container - better way
```PowerShell
psql postgresql://postgres:DaftAcademy@127.0.0.1:5555/postgres
```

## 5. View Tables
```psql
postgres=# \d
                List of relations
 Schema |         Name         | Type  |  Owner
--------+----------------------+-------+----------
 public | categories           | table | postgres
 public | customercustomerdemo | table | postgres
 public | customerdemographics | table | postgres
 public | customers            | table | postgres
 public | employees            | table | postgres
 public | employeeterritories  | table | postgres
 public | order_details        | table | postgres
 public | orders               | table | postgres
 public | products             | table | postgres
 public | region               | table | postgres
 public | shippers             | table | postgres
 public | shippers_tmp         | table | postgres
 public | suppliers            | table | postgres
 public | territories          | table | postgres
 public | usstates             | table | postgres
(15 rows)
```

## 6. Dump Database
```PowerShell
pg_dump --format=c --no-owner --no-acl -h 127.0.0.1 -p 5555 -U postgres > northwind.sql.dump 
```
## 7. Export dumped DB to Heroku
```PowerShell
 heroku pg:backups:restore 'https://github.com/daftcode/daftacademy-python_levelup-spring2021/raw/master/5_O_jak_ORM/dumps/northwind.sql.dump' postgresql-defined-18177 --app daftacademy2021 --confirm daftacademy2021
```

## 8. Connect to Database on Heroku via Heroku CLI
```PowerShell
heroku pg:psql postgresql-defined-18177 --app daftacademy2021
```

## 9. Create models from database:
Modele odwzorowują struktury tabeli w bazie danych - potrzebne do ORM.
Schemas - to w jakiej formie dane zwraca Python (modele Pydentic - nie mylić!)
```PowerShell
sqlacodegen 'postgresql://postgres:DaftAcademy@127.0.0.1:5555' > models_postgres.py
```

## 10. Run App Locally - add to env!
```PowerShell
$env:SQLALCHEMY_DATABASE_URL="postgresql://postgres:DaftAcademy@127.0.0.1:5555/postgres";  uvicorn main:app
```

### CURL Testing Commands
```PowerShell
HTTP 401:

curl -i "http://127.0.0.1:5555/auth?password=haslo&password_hash=f34ad4b3ae1e2cf33092e2abb60dc0444781c15d0e2e9ecdb37e4b14176a0164027b05900e09fa0f61a1882e0b89fbfa5dcfcc9765dd2ca4377e2c794837e091"

HTTP 204:

curl -i "http://127.0.0.1:5555/auth?password=haslo&password_hash=013c6889f799cd986a735118e1888727d1435f7f623d05d58c61bf2cd8b49ac90105e5786ceaabd62bbc27336153d0d316b2d13b36804080c44aa6198c533215"

Register Patient:
curl -i -X POST -H "Content-Type: application/json" -d "{\"name\":\"Krzysztof\", \"surname\":\"Jakubiak\"}" http://127.0.0.1:5555/register

Get Patient:
curl -i -X GET http://127.0.0.1:5555/patient/1
```
# MOM

## Client

## Server

Set up MySQL database (if needed):

- Need to have docker and docker compose installed

```bash
docker compose up -d
```

Set up .env file:

```bash
touch .env
```

Edit `.env` file contents:

```bash
DATABASE_URL=mysql+pymysql://user:root@localhost:3306/mom
```

Run migrations and server:

```bash
cd server
pip install -r requirements.txt
alembic init alembic
alembic upgrade head
python main.py
```

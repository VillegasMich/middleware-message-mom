# MOM

## Client

Edit `boostrap.py` file contents:

```python
SERVER_URL = "http://{SERVER_IP}:{PORT}"
```

Run client:

```bash
cd client
pip install -r requirements.txt
python main.py
```

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
fastapi main
```

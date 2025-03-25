# MOM

## Client

Run client:

```bash
cd client
pip install -r requirements.txt
python main.py
```

## Server

### Set up MySQL database and/or ZooKeeper:

- Need to have docker and docker-compose installed to start the container

```bash
docker-compose up -d
```

- For monitoring the ZooKeeper use the nest command:

```bash
docker exec -it zookeeper zkCli.sh -server localhost:2181
```

### Set up .env file:

```bash
touch .env
nano .env
```

### Edit `.env` file contents:

```bash
DATABASE_URL=mysql+pymysql://user:root@localhost:3306/mom
SECRET_KEY=...
ALGORITHM=HS256
SERVER_ELASTIC_IP=...
```

#### Secret Key

- The SECRET_KEY enviroment variable must be generated with the following code (can be generated with ChatGPT):

```python
import secrets
print(secrets.token_hex(32))
```

#### Server Elastic IP

- This is the IP of the EC2 Instance if the server is running on AWS

### Run migrations and server:

```bash
cd server
pip install -r requirements.txt
alembic upgrade head
fastapi run main.py
```

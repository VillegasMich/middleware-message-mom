"""
This file defines the authentication-related routes for the server side application.
It includes endpoints for user registration and login, handling JWT token generation,
and interacting with the ZooKeeper service for user and server metadata management.
"""

from datetime import datetime, timedelta

from app.core.auth_helpers import get_current_user
from app.core.config import ALGORITHM, SECRET_KEY
from app.core.database import get_db
from app.models.user import User
from ..grpc.Client import Client
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session
from zookeeper import SERVER_IP, SERVER_PORT, ZK_NODE_USERS, zk


class UserCreate(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


ACCESS_TOKEN_EXPIRE_MINUTES = 120

router = APIRouter()


@router.post("/register/")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    #Registers a new user and ensures the username is unique across all servers.
    
    username = user_data.username
    password = user_data.password

    if db.query(User).filter(User.name == username).first():
        raise HTTPException(status_code=400, detail="User already exists")

    new_id = 1
    servers: list[str] = zk.get_children("/servers") or []
    for server in servers:
        server_users: list[str] = (
            zk.get_children(f"/servers-metadata/{server}/Users") or []
        )
        for users_id in server_users:
            if int(users_id) >= new_id:
                new_id = int(users_id) + 1

    new_user = User(id=new_id, name=username)
    new_user.set_password(password)

    db.add(new_user)
    db.commit()

    zk.ensure_path(f"{ZK_NODE_USERS}/{new_user.id}")

    #Send the new user data to all other servers
    servers: list[str] = zk.get_children("/servers") or []
    for server in servers:
        if server != f"{SERVER_IP}:{SERVER_PORT}":
            server_ip, _ = server.split(":")
            response = Client.send_grpc_register(username,password,new_id,server_ip + ":8080")

    return {"message": "User registered successfully"}


@router.post("/login/")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    #Logs in a user and generates a JWT token for authentication.
    
    username = request.username
    password = request.password

    user = db.query(User).filter(User.name == username).first()

    #Check if the user exists locally and verify the password
    if user:
        expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = jwt.encode(
            {"sub": user.name, "exp": expires_at.timestamp()},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        return {"access_token": access_token, "token_type": "bearer"}

    #If the user is not found locally, check other servers
    else:
        servers = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_users = zk.get_children(
                    f"servers-metadata/{server}/Users") or []
                for user in server_users:
                    print(f"User {user} found on server {server}")
    raise HTTPException(status_code=400, detail="Invalid credentials")

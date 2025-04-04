from sqlalchemy.orm import Session

from fastapi import HTTPException
from ..models.user import User
from zookeeper import ZK_NODE_USERS, zk

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def register(self, request):
        username = request.user_name
        password = request.user_password

        if self.db.query(User).filter(User.name == username).first():
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

        self.db.add(new_user)
        self.db.commit()

        zk.ensure_path(f"{ZK_NODE_USERS}/{new_user.id}")

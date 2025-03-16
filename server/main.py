from fastapi import FastAPI, Depends
from app.routes.queue import router as queue_router

app = FastAPI()

app.include_router(queue_router)

@app.get("/")
def root():
    return {"message": "Records successfully created"}

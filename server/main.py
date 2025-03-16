from fastapi import FastAPI, Depends

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Records successfully created"}

from fastapi import FastAPI

from tracelite.core.config import load_config
from tracelite.core.storage.sqlite import SQLiteStorage
from tracelite.middleware.fastapi import TraceliteMiddleware

app = FastAPI()

# Load configuration and storage
config = load_config()
storage = SQLiteStorage(db_path=config.db_path)

# Apply Tracelite middleware
app.add_middleware(TraceliteMiddleware, storage=storage, config=config)


@app.get("/")
def read_root():
    return {"message": "Welcome to Tracelite FastAPI Demo"}


@app.get("/ping")
def ping():
    return {"message": "pong"}

import time
from sqlalchemy.exc import OperationalError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from models import User
from database import SessionLocal, engine, Base

app = FastAPI(title="Auth Service")

def wait_for_db(retries=10, delay=2):
    for i in range(retries):
        try:
            with engine.connect() as connection:
                print("Database connection established.", flush=True)
            return
        except OperationalError:
            print(f"Database not ready. Retrying in {delay} seconds... ({i+1}/{retries})", flush=True)
            time.sleep(delay)
    raise Exception("Database connection failed after several retries.")

wait_for_db()
Base.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    username: str
    password: str

@app.on_event("startup")
def seed_db():
    db = SessionLocal()
    try:
        if not db.query(User).first():
            default_user = User(username="admin", password="adminpass")
            db.add(default_user)
            db.commit()
            print("Inserted default admin user.", flush=True)
    except Exception as e:
        print("Error seeding DB:", e, flush=True)
    finally:
        db.close()

@app.post("/register")
def register(user: UserCreate):
    db = SessionLocal()
    # (Optional: Add duplicate user checking)
    db_user = User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"msg": "User registered", "user_id": db_user.id}

@app.post("/login")
def login(user: UserCreate):
    db = SessionLocal()
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"msg": "Login successful", "user_id": db_user.id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

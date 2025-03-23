import time
from sqlalchemy.exc import OperationalError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from models import Task
from database import SessionLocal, engine, Base

app = FastAPI(title="Tasks Service")

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

class TaskCreate(BaseModel):
    title: str
    description: str = None

@app.post("/tasks")
def create_task(task: TaskCreate):
    db = SessionLocal()
    db_task = Task(title=task.title, description=task.description)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return {"msg": "Task created", "task_id": db_task.id}

@app.get("/tasks")
def get_tasks():
    db = SessionLocal()
    tasks = db.query(Task).all()
    return tasks

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"msg": "Task deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

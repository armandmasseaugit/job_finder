from fastapi import FastAPI
from routes import jobs

app = FastAPI()
app.include_router(jobs.router)

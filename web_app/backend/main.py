from fastapi import FastAPI

from web_app.backend.routes import jobs

app = FastAPI()
app.include_router(jobs.router)

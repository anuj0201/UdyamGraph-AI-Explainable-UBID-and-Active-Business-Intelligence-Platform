from fastapi import FastAPI
from app.api.routes import router
from app.db.postgres import engine
from app.models.db_models import Base

app = FastAPI()

# CREATE TABLES
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "UdyamGraph AI Backend Running"}


app.include_router(router)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
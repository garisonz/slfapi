from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routes.auth import router as auth_router

app = FastAPI(title="SELF API")

# Allow the frontend to access the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/api/v1/hello")
def hello():
    return {"message": "Hello from SELF API!"}

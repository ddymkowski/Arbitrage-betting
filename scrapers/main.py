from fastapi import FastAPI

from src.routes import router

app = FastAPI()
app.include_router(router=router)

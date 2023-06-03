from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import conn

from routes.users import user_router
from routes.converter import file_router

import uvicorn

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router,  prefix="/user")
app.include_router(file_router, prefix="/file")


@app.on_event("startup")
def on_startup():
    conn()


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

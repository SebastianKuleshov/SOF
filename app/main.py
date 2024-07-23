from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.users.routes import router as users_router
from app.auth.routes import router as auth_router
from app.comments.routes import router as comments_router
from app.answers.routes import router as answers_router
from app.questions.routes import router as questions_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(comments_router)
app.include_router(answers_router)
app.include_router(questions_router)

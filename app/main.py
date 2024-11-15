from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.answers.routes import router as answers_router
from app.auth.routes import router as auth_router
from app.comments.routes import router as comments_router
from app.dependencies import get_settings
from app.permissions.routes import router as permissions_router
from app.questions.routes import private_router as private_questions_router
from app.questions.routes import public_router as public_questions_router
from app.questions.routes import search_router as search_questions_router
from app.tags.routes import private_router as private_tags_router
from app.tags.routes import public_router as public_tags_router
from app.users.routes import private_router as private_user_router
from app.users.routes import public_router as public_user_router

settings = get_settings()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS.split(','),
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(public_user_router)
app.include_router(private_user_router)
app.include_router(auth_router)
app.include_router(comments_router)
app.include_router(answers_router)
app.include_router(public_questions_router)
app.include_router(private_questions_router)
app.include_router(search_questions_router)
app.include_router(public_tags_router)
app.include_router(private_tags_router)
app.include_router(permissions_router)

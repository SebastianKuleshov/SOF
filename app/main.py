from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import get_settings
from app.auth.routes import router as auth_router
from app.users.routes import public_router as public_user_router
from app.users.routes import private_router as private_user_router
from app.common.routes import router as common_router
from app.answers.routes import private_router as private_answers_router
from app.comments.routes import private_router as private_comments_router
from app.questions.routes import public_router as public_questions_router
from app.questions.routes import private_router as private_questions_router
from app.tags.routes import public_router as public_tags_router

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
app.include_router(private_comments_router)
app.include_router(private_answers_router)
app.include_router(public_questions_router)
app.include_router(private_questions_router)
app.include_router(public_tags_router)
app.include_router(common_router)

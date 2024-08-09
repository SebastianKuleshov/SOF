from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.answers.routes import router as answers_router
from app.auth.routes import router as auth_router
from app.comments.routes import router as comments_router
from app.common.routes import router as common_router
from app.dependencies import get_settings
from app.questions.routes import router as questions_router
from app.tags.routes import router as tags_router
from app.users.routes import router as users_router

settings = get_settings()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS.split(','),
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(comments_router)
app.include_router(answers_router)
app.include_router(questions_router)
app.include_router(tags_router)
app.include_router(common_router)

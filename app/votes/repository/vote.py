from app.common.repositories.base_repository import BaseRepository
from app.votes.models import VotesModel


class VoteRepository(BaseRepository):
    model = VotesModel

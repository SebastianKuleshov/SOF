from fastapi import HTTPException
from sqlalchemy import select, Select, text, func, case
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.answers.models import AnswerModel
from app.common.repositories.base_repository import BaseRepository
from app.questions.models import QuestionModel
from app.roles.models import RoleModel
from app.users.models import UserModel
from app.votes.models import VotesModel


class UserRepository(BaseRepository):
    model = UserModel

    def _get_default_stmt(self) -> Select:
        return select(self.model).options(
            joinedload(self.model.roles).joinedload(RoleModel.permissions)
        )

    async def update_reputation(
            self,
            user_id: str,
            is_upvote: bool
    ) -> int:
        user = await self.get_by_id(user_id)
        user.reputation += 1 if is_upvote else -1
        await self.session.commit()
        return user.reputation

    async def get_by_id_with_roles(
            self,
            user_id: str
    ) -> UserModel:
        stmt = (
            select(self.model)
            .options(
                joinedload(self.model.roles)
                .joinedload(RoleModel.permissions),
            )
            .where(user_id == self.model.id)
        )
        return await self.session.scalar(stmt)

    async def get_user_permissions(
            self,
            user_id: str
    ) -> set[str]:
        stmt = text(
            '''SELECT permissions_1.name
            FROM users LEFT OUTER JOIN (role_user AS role_user_1 JOIN permission_role AS permission_role_1 ON role_user_1.role_id = permission_role_1.role_id JOIN permissions AS permissions_1 ON permissions_1.id = permission_role_1.permission_id) ON users.id = role_user_1.user_id
            WHERE users.id = :user_id;
            '''
        )
        result = await self.session.scalars(stmt, {'user_id': user_id})
        return set(result.all())

    async def attach_roles_to_user(
            self,
            user_id: str,
            roles: list[RoleModel]
    ) -> bool:
        user = await self.get_by_id_with_roles(user_id)
        for role in roles:
            user.roles.append(role)
        try:
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail='Role is already attached to the user'
            )
        return True

    async def detach_roles_from_user(
            self,
            user_id: str,
            roles: list[RoleModel]
    ) -> bool:
        user = await self.get_by_id_with_roles(user_id)
        try:
            for role in roles:
                user.roles.remove(role)
            await self.session.commit()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail='Role is not attached to the user'
            )
        return True

    async def get_top_contributors(self):
        question_votes_subquery = (
            select(
                VotesModel.question_id,
                func.sum(
                    case(
                        (VotesModel.is_upvote == True, 1),
                        else_=0
                    )
                ).label('questions_upvotes'),
            ).group_by(VotesModel.question_id).subquery()
        )

        answers_votes_subquery = (
            select(
                VotesModel.answer_id,
                func.sum(
                    case(
                        (VotesModel.is_upvote == True, 1),
                        else_=0
                    )
                ).label('answers_upvotes'),
            ).group_by(VotesModel.answer_id).subquery()
        )



        stmt = (
            select(
                self.model.id,
                func.coalesce(
                    question_votes_subquery.c.questions_upvotes,
                    0
                ).label('questions_upvotes'),
                func.coalesce(
                    answers_votes_subquery.c.answers_upvotes,
                    0
                ).label('answers_upvotes')
            ).outerjoin(
                QuestionModel,
                QuestionModel.user_id == self.model.id
            ).outerjoin(
                AnswerModel,
                AnswerModel.user_id == self.model.id
            ).outerjoin(
                question_votes_subquery,
                question_votes_subquery.c.question_id == QuestionModel.id
            ).outerjoin(
                answers_votes_subquery,
                answers_votes_subquery.c.answer_id == AnswerModel.id
            ).group_by(
                self.model.id,
                question_votes_subquery.c.questions_upvotes,
                answers_votes_subquery.c.answers_upvotes
            )
        )

        result = await self.session.execute(stmt)
        return result.unique().all()

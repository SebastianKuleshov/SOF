from fastapi import HTTPException
from sqlalchemy import select, Select, text, case, distinct, Numeric, cast, \
    desc, Sequence
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.functions import coalesce, func

from app.answers.models import AnswerModel
from app.common.repositories.base_repository import BaseRepository
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
            user_id: int,
            is_upvote: bool
    ) -> int:
        user = await self.get_by_id(user_id)
        user.reputation += 1 if is_upvote else -1
        await self.session.commit()
        return user.reputation

    async def get_by_id_with_roles(
            self,
            user_id: int
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
            user_id: int
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
            user_id: int,
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
            user_id: int,
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

    async def get_top_contributors(
            self
    ) -> Sequence[UserModel]:

        answers_count_subquery = (
            select(
                AnswerModel.user_id,
                func.count(distinct(AnswerModel.id)).label('total_answers'),
                func.sum(
                    case(
                        (AnswerModel.created_at >= func.now() -
                         func.cast(func.concat(24, ' HOURS'), INTERVAL), 1),
                        else_=0
                    ),
                ).label('answers_amount_24h'),
                case(
                    (
                        func.min(
                            AnswerModel.created_at
                        ) is not None and func.count(AnswerModel.id) > 0,
                        func.count(AnswerModel.id) / func.ceil(
                            func.greatest(
                                func.date_part(
                                    'days', func.now() - func.min(
                                        AnswerModel.created_at
                                    )
                                ),
                                1
                            )
                            / 7.0
                        ),
                    ),
                    else_=0
                ).label('average_answers_amount_7d')
            ).select_from(
                AnswerModel
            ).group_by(AnswerModel.user_id).subquery()
        )

        votes_count_subquery = (
            select(
                AnswerModel.user_id,
                func.sum(
                    case(
                        (True == VotesModel.is_upvote, 1),
                        else_=0
                    )
                ).label('total_answer_upvotes'),
                func.sum(
                    case(
                        (False == VotesModel.is_upvote, 1),
                        else_=0
                    )
                ).label('total_answer_downvotes')
            ).select_from(
                VotesModel
            ).join(
                AnswerModel,
                AnswerModel.id == VotesModel.answer_id
            ).group_by(AnswerModel.user_id).subquery()
        )

        stmt = (
            select(
                self.model.id,
                self.model.nick_name,
                coalesce(
                    answers_count_subquery.c.total_answers, 0
                ).label('total_answers'),
                coalesce(
                    answers_count_subquery.c.answers_amount_24h, 0
                ).label('answers_amount_24h'),
                func.round(
                    coalesce(
                        answers_count_subquery.c.average_answers_amount_7d, 0
                    ), 3
                ).label('average_answers_amount_7d'),
                coalesce(
                    votes_count_subquery.c.total_answer_upvotes, 0
                ).label('total_answer_upvotes'),
                func.round(
                    coalesce(
                        votes_count_subquery.c.total_answer_upvotes, 0
                    ) / coalesce(
                        cast(
                            answers_count_subquery.c.total_answers, Numeric
                        ), 1.0
                    ), 3
                ).label('average_upvotes_per_answer'),
                coalesce(
                    votes_count_subquery.c.total_answer_downvotes, 0
                ).label('total_answer_downvotes'),
                func.round(
                    coalesce(
                        votes_count_subquery.c.total_answer_downvotes, 0
                    ) / coalesce(
                        cast(
                            answers_count_subquery.c.total_answers, Numeric
                        ), 1.0
                    ), 3
                ).label('average_downvotes_per_answer'),
            ).outerjoin(
                answers_count_subquery,
                answers_count_subquery.c.user_id == self.model.id
            ).outerjoin(
                votes_count_subquery,
                votes_count_subquery.c.user_id == self.model.id
            ).order_by(
                desc(
                    coalesce(
                        answers_count_subquery.c.total_answers, 0
                    )
                ),
                desc(
                    coalesce(
                        votes_count_subquery.c.total_answer_upvotes, 0
                    )
                )
            ).limit(5)
        )

        top_contributors = await self.session.execute(stmt)
        return top_contributors.unique().fetchall()

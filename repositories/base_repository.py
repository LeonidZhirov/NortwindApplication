from typing import TypeVar, Generic, Type, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_by_id(self, session: Session, entity_id: Any) -> Optional[ModelType]:
        return session.get(self.model, entity_id)

    def get_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[ModelType]:
        stmt = select(self.model).limit(limit).offset(offset)
        return list(session.execute(stmt).scalars().all())

    def get_by_ids(self, session: Session, entity_ids: List[Any]) -> List[ModelType]:
        if not entity_ids:
            return []
        stmt = select(self.model).where(self.model.id.in_(entity_ids))
        return list(session.execute(stmt).scalars().all())

    def add(self, session: Session, entity: ModelType) -> ModelType:
        session.add(entity)
        session.flush()
        return entity

    def add_all(self, session: Session, entities: List[ModelType]) -> List[ModelType]:
        session.add_all(entities)
        session.flush()
        return entities

    def update(self, session: Session, entity_id: Any, **kwargs) -> Optional[ModelType]:
        entity = self.get_by_id(session, entity_id)
        if not entity:
            return None

        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        session.flush()
        session.refresh(entity)

        return entity

    def delete(self, session: Session, entity_id: Any) -> bool:
        entity = self.get_by_id(session, entity_id)
        if entity:
            session.delete(entity)
            session.flush()
            return True
        return False

    def exists(self, session: Session, entity_id: Any) -> bool:
        return self.get_by_id(session, entity_id) is not None

    def count(self, session: Session) -> int:
        stmt = select(func.count()).select_from(self.model)
        return session.execute(stmt).scalar() or 0
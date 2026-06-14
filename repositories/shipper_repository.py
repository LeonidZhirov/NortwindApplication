from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.shipper_model import Shipper


class ShipperRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Shipper]:
        return list(self.session.execute(
            select(Shipper).order_by(Shipper.company_name)
        ).scalars().all())


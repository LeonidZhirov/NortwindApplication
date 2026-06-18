# repositories/employee_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from models.employee_model import Employee
from repositories.base_repository import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self):
        super().__init__(Employee)

    def get_by_id(self, session: Session, employee_id: int) -> Optional[Employee]:
        return super().get_by_id(session, employee_id)

    def get_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[Employee]:
        stmt = select(Employee).order_by(Employee.last_name, Employee.first_name).limit(limit).offset(offset)
        return list(session.execute(stmt).scalars().all())

    def get_manager(self, session: Session, employee_id: int) -> Optional[Employee]:
        stmt = select(Employee).where(Employee.employee_id == employee_id).options(
            joinedload(Employee.manager)
        )
        employee = session.execute(stmt).scalar_one_or_none()
        return employee.manager if employee else None

    def get_subordinates(self, session: Session, employee_id: int) -> List[Employee]:
        stmt = select(Employee).where(
            Employee.manager.has(Employee.employee_id == employee_id)
        ).order_by(Employee.last_name, Employee.first_name)
        return list(session.execute(stmt).scalars().all())

    def get_employee_with_managed_team(self, session: Session, employee_id: int) -> Optional[Employee]:
        stmt = select(Employee).where(Employee.employee_id == employee_id).options(
            joinedload(Employee.subordinates)
        )
        return session.execute(stmt).scalar_one_or_none()

    def get_hierarchy(self, session: Session) -> List[Employee]:
        stmt = select(Employee).options(
            joinedload(Employee.manager),
            joinedload(Employee.subordinates)
        ).order_by(Employee.last_name, Employee.first_name)
        return list(session.execute(stmt).scalars().all())
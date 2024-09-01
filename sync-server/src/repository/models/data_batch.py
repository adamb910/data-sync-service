from sqlalchemy import String, Column, DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from repository.models.base import Base

class DataBatch(Base):
    __tablename__ = "databatch"
    #TODO: internal ID shouldn't be the one sent around across the network
    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(8))
    #TODO: index needed on updated_at as it is a field which we search through
    updated_at = Column(DateTime)

    def __repr__(self) -> str:
        return f"DataBatch(id={self.id!r}, data={self.data!r}, status={self.status!r}, updated_at={self.updated_at!r})"
    
    def to_dict(self):
        return {
            "id": self.id,
            "data": self.data,
            "status": self.status,
            "updated_at": self.updated_at.isoformat()
        }
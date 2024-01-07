from typing import List
from sqlalchemy import Text, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
  pass

class BCPRequest(Base):
  __tablename__ = "BCPRequest"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  
  # for multiple users, just serialize array of names to JSON and store as string
  rank_name: Mapped[str] = mapped_column(Text())
  
  time: Mapped[int] = mapped_column(Float())
  purpose: Mapped[str] = mapped_column(Text())
  info: Mapped[str] = mapped_column(Text())

  def __repr__(self):
    return f"BCPRequest(id={self.id!r}, rank_name={self.rank_name!r}, time={self.time!r}, purpose={self.purpose!r}, info={self.info!r})"

class RSORequest(Base):
  __tablename__ = "RSORequest"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  rank_name: Mapped[str] = mapped_column(Text())
  location: Mapped[str] = mapped_column(Text())
  time: Mapped[int] = mapped_column(Float())
  reason: Mapped[str] = mapped_column(Text())
  info: Mapped[str] = mapped_column(Text())

  def __repr__(self):
    return f"RSORequest(id={self.id!r}, rank_name={self.rank_name!r}, location={self.location!r}, time={self.time!r}, reason={self.reason!r}, info={self.info!r})"

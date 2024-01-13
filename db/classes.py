from sqlalchemy import ForeignKey, Text, Float, Integer, Boolean, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from utility.constants import RequestStatus

class Base(DeclarativeBase):
  pass

class BCPRequest(Base):
  __tablename__ = "BCPRequest"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  
  sender_id: Mapped[int] = mapped_column(Integer())

  # for multiple users, just serialize array of names to JSON and store as string
  rank_name: Mapped[str] = mapped_column(Text())
  
  time: Mapped[int] = mapped_column(Float())
  purpose: Mapped[str] = mapped_column(Text())
  info: Mapped[str] = mapped_column(Text())

  acknowledged: Mapped[bool] = mapped_column(Boolean(), default=False)
  status: Mapped[RequestStatus] = mapped_column(
    SQLEnum(RequestStatus, create_constraint=False),
    default=RequestStatus.PENDING,
  )

  messages: Mapped["BCPRequestNotification"] = relationship(back_populates="request")

  def __repr__(self):
    return f"BCPRequest(id={self.id!r}, rank_name={self.rank_name!r}, time={self.time!r}, purpose={self.purpose!r}, info={self.info!r})"

class RSORequest(Base):
  __tablename__ = "RSORequest"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  sender_id: Mapped[int] = mapped_column(Integer())
  rank_name: Mapped[str] = mapped_column(Text())
  location: Mapped[str] = mapped_column(Text())
  time: Mapped[int] = mapped_column(Float())
  reason: Mapped[str] = mapped_column(Text())
  info: Mapped[str] = mapped_column(Text())

  acknowledged: Mapped[bool] = mapped_column(Boolean())
  status: Mapped[RequestStatus] = mapped_column(SQLEnum(RequestStatus, create_constraint=False))

  messages: Mapped["RSORequestNotification"] = relationship(back_populates="request")

  def __repr__(self):
    return f"RSORequest(id={self.id!r}, rank_name={self.rank_name!r}, location={self.location!r}, time={self.time!r}, reason={self.reason!r}, info={self.info!r})"

class ChatGroup(Base):
  __tablename__ = "BotMemberGroup"

  id: Mapped[int] = mapped_column(primary_key=True)

class BCPRequestNotification(Base):
  __tablename__ = "BCPRequestNotification"

  chat_id: Mapped[int] = mapped_column(primary_key=True)
  message_id: Mapped[int] = mapped_column(primary_key=True)
  
  request_id: Mapped[int] = mapped_column(ForeignKey("BCPRequest.id"))
  request: Mapped[BCPRequest] = relationship(back_populates="messages")

class RSORequestNotification(Base):
  __tablename__ = "RSORequestNotification"

  chat_id: Mapped[int] = mapped_column(primary_key=True)
  message_id: Mapped[int] = mapped_column(primary_key=True)

  request_id: Mapped[int] = mapped_column(ForeignKey("RSORequest.id"))
  request: Mapped[RSORequest] = relationship(back_populates="messages")

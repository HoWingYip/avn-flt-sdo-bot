from sqlalchemy import ForeignKey, Boolean, Integer, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy_json import MutableJson
from typing import List, Optional

from utility.constants import RequestStatus


class Base(DeclarativeBase):
  pass


class Request(Base):
  __tablename__ = "Request"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  sender_id: Mapped[int] = mapped_column(Integer())
  info: Mapped[dict] = mapped_column(MutableJson)
  acknowledged: Mapped[bool] = mapped_column(Boolean(), default=False)
  status: Mapped[RequestStatus] = mapped_column(
    SQLEnum(RequestStatus, create_constraint=False),
    default=RequestStatus.PENDING,
  )
  
  notifications: Mapped[List["RequestNotification"]] = relationship(
    back_populates="request",
  )
  verdict_notification: Mapped[Optional["RequestVerdictNotification"]] = relationship(
    back_populates="request",
  )


class RequestNotification(Base):
  __tablename__ = "RequestNotification"

  chat_id: Mapped[int] = mapped_column(primary_key=True)
  message_id: Mapped[int] = mapped_column(primary_key=True)
  request_id: Mapped[int] = mapped_column(ForeignKey("Request.id"))
  request: Mapped["Request"] = relationship(back_populates="notifications")


class RequestVerdictNotification(Base):
  __tablename__ = "RequestVerdictNotification"

  chat_id: Mapped[int] = mapped_column(primary_key=True)
  message_id: Mapped[int] = mapped_column(primary_key=True)
  request_id: Mapped[int] = mapped_column(ForeignKey("Request.id"))
  request: Mapped["Request"] = relationship(back_populates="verdict_notification")


class ChatGroup(Base):
  __tablename__ = "BotMemberGroup"

  id: Mapped[int] = mapped_column(primary_key=True)

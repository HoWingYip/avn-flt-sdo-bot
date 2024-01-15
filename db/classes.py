from sqlalchemy import ForeignKey, Boolean, Integer, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy_json import MutableJson
from typing import List

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
  messages: Mapped[List["RequestNotification"]] = relationship(back_populates="request")


class RequestNotification(Base):
  __tablename__ = "RequestNotification"

  chat_id: Mapped[int] = mapped_column(primary_key=True)
  message_id: Mapped[int] = mapped_column(primary_key=True)
  request_id: Mapped[int] = mapped_column(ForeignKey("Request.id"))
  request: Mapped["Request"] = relationship(back_populates="messages")


class ChatGroup(Base):
  __tablename__ = "BotMemberGroup"

  id: Mapped[int] = mapped_column(primary_key=True)

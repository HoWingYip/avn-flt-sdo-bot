from sqlalchemy import ForeignKey, Boolean, Integer, Enum as SQLEnum, Float, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy_json import MutableJson
from typing import List, Optional
from datetime import datetime

from utility.constants import RequestStatus

# TODO: define indices for faster queries


class Base(DeclarativeBase):
  pass


class Request(Base):
  __tablename__ = "Request"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  sender_id: Mapped[int] = mapped_column(Integer())
  info: Mapped[dict] = mapped_column(MutableJson)
  status: Mapped[RequestStatus] = mapped_column(
    SQLEnum(RequestStatus, create_constraint=False),
    default=RequestStatus.PENDING_ACKNOWLEDGEMENT,
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


class SDOLogEntry(Base):
  __tablename__ = "SDOLogEntry"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

  # don't set time automatically because all incoming SDOs must be
  # logged at the EXACT SAME time
  # the time difference between insertion of two different rows will
  # make it impossible to reliably retrieve all incoming SDOs
  # associated with the most recent HOTO
  time: Mapped[float] = mapped_column(Float())
  sdo_id: Mapped[int] = mapped_column(Integer())
  sdo_info: Mapped[str] = mapped_column(Text())


class ChatGroup(Base):
  __tablename__ = "BotMemberGroup"

  id: Mapped[int] = mapped_column(primary_key=True)

from sqlalchemy import create_engine

from .classes import Base

engine = create_engine("sqlite:///./db/db.sqlite", echo=True)
Base.metadata.create_all(engine)

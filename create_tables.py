from database.models import *
from database.db_manager import Base, engine, get_db

Base.metadata.create_all(engine)

db = next(get_db())




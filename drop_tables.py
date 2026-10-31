from database.models import *
from database.db_manager import Base, engine


Base.metadata.drop_all(engine)


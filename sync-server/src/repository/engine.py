from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

# import database table types to guarantee creation by engine
from repository.models.base import Base
from repository.models.data_batch import DataBatch

username = "postgres" # os.getenv() to get from docker-compose variables for all these
password = "postgres"
database = "sync_db"
host = "postgres"
port = 5432

connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"

engine = create_engine(connection_string, echo=True)
if not database_exists(engine.url):
    create_database(engine.url)

print(f"Database exists: {database_exists(engine.url)}")
print(Base.metadata.tables)
Base.metadata.create_all(engine)
from sqlmodel import Session, SQLModel, create_engine
from app.models import User, Video, Interaction

sql_alchemy_database_url = f"postgresql+psycopg2://postgres:Student%40eacc18@localhost:3453/reconova"

# Create the SQLAlchemy engine

engine = create_engine(sql_alchemy_database_url, echo=True)

# Create the database tables
def create_db_and_tables():
    """Create the database and tables."""
    SQLModel.metadata.create_all(engine)
    print("Database and tables created successfully")

# Create a session to interact with the database
def get_session():
    """Create a new session to interact with the database."""
    with Session(engine) as session:
        # Commit the transaction
        yield session

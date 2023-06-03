from sqlmodel import SQLModel, Session, create_engine

database_host = "database"
database_port = "5432"
database_name = "postgres"
database_user = "postgres"
database_password = "susel"

database_connection_string = (f"postgresql://{database_user}:"
                              f"{database_password}"
                              f"@{database_host}:"
                              f"{database_port}/"
                              f"{database_name}")
engine_url = create_engine(database_connection_string, echo=True)


def conn():
    SQLModel.metadata.create_all(engine_url)


def get_session():
    with Session(engine_url) as session:
        yield session

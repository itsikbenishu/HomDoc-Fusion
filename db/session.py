from sqlmodel import Session, create_engine
from typing import Annotated
from fastapi import Depends
from urllib.parse import quote_plus
from db.config import db_settings

password_encoded = quote_plus(db_settings.POSTGRES_PASSWORD)
DATABASE_URL = (
    f"postgresql+psycopg://{db_settings.POSTGRES_USER}:{password_encoded}"
    f"@{db_settings.POSTGRES_HOST}:{db_settings.POSTGRES_PORT}/{db_settings.POSTGRES_DB}"
)

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

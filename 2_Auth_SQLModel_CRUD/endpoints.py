from schema import Users
from sqlmodel import SQLModel, create_engine, Session, select
from fastapi import FastAPI, Depends, HTTPException
from services.hashing import hash_password, verify_password

POSTGRES_CONNECTION_STRING = "postgresql+psycopg2://postgres:Sheam000@localhost:5432/auth"
engine = create_engine(POSTGRES_CONNECTION_STRING)

app = FastAPI()

# database access
def create_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)

# endpoints, and on events
@app.on_event('startup')
def on_start():
    create_db()

@app.get('/')
def health():
    return {
        'version':'1.0',
        'message':'Welcome to the Authentication'
    }

@app.post('/signup/', response_model=Users)
def sign_up(user: Users, session: Session = Depends(get_session)):
    existing_user = session.exec(select(Users).where(Users.email == user.email)).first()    
    if existing_user:
        raise HTTPException(status_code=409, detail="The email is already in use!")
    
    user.hashed_password = hash_password(user.hashed_password)
    session.add(user)
    session.commit()

    session.refresh(user)
    return user



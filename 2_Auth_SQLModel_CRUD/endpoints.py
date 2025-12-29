from schema import UserAuth, UserInfo, UserSignup
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
    with Session(engine) as session:
        yield session

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

@app.post('/signup/', response_model=dict)
def signup(user:UserSignup, session: Session=Depends(get_session)):
    existing_user = session.exec(select(UserAuth).where(UserAuth.email==user.email)).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="This email already holds an account!")
    
    hashed_password = hash_password(user.password)
    user_auth = UserAuth(email=user.email, hashed=hashed_password)

    user_info = UserInfo(
        full_name=user.full_name,
        age=user.age, 
        gender=user.gender,
        auth=user_auth
    )

    session.add(user_info)
    session.commit()

    return {
        'status_code': 201,
        'message': 'Signed up successfully!'
    }

@app.post('/login/', response_model=dict)
def login(user: UserAuth, session: Session=Depends(get_session)):
    existing_user = session.exec(select(UserAuth).where(UserAuth.email==user.email)).first()
    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid Email!")

    if not verify_password(user.hashed, existing_user.hashed):
        raise HTTPException(status_code=401, detail="Invalid password!")
    
    return {
        'status_code':200,
        'message':'Login successful'
    }
from sqlmodel import SQLModel, Session, create_engine, select
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from typing import  Dict
from schema import BlogPost

POSTGRES_CONNECTION_STRING = "postgresql+psycopg2://postgres:Sheam000@localhost:5432/blogdb"
engine = create_engine(POSTGRES_CONNECTION_STRING)

app = FastAPI()

def create_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)

@app.on_event('startup')
def on_startup():
    create_db()

@app.post('/blog', response_model=BlogPost)
def create_post(post:BlogPost, session: Session = Depends(get_session)):
    session.add(post)
    session.commit()

    session.refresh(post)
    return post

@app.get('/blog', response_model=list[BlogPost])
def get_all_post(session: Session = Depends(get_session)):
        posts = session.exec(select(BlogPost)).all()
        return posts

@app.get('/blog/{post_id}', response_model=BlogPost)
def view_post(post_id: int, session: Session = Depends(get_session)):
    post = session.get(BlogPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="No post with that id!")
    else: 
        return post
        
@app.put('/blog/{post_id}', response_model=BlogPost)
def update_blog(post_id:int, updated_post:BlogPost, session: Session = Depends(get_session)):
    post = session.get(BlogPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="No post with that id!")
    
    post.title = updated_post.title
    post.text = updated_post.text
    post.date = datetime.utcnow()

    session.add(post)
    session.commit()

    session.refresh(post)
    return post
    

@app.delete('/blog/{post_id}', response_model=Dict)
def delete_blog(post_id:int, session: Session = Depends(get_session)):
    post = session.get(BlogPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="No post with that id!")
    
    session.delete(post)
    session.commit()

    return {'message': "Post Deleted!"}
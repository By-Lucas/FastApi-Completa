from datetime import timedelta
from fastapi import FastAPI, Request, Depends, status, Form, Response, Path
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from starlette.status import HTTP_400_BAD_REQUEST
from db import SessionLocal, engine, DBContext
import models, crud, schemas
from sqlalchemy.orm import Session
from fastapi_login import LoginManager
from dotenv import load_dotenv
import os
import requests
from passlib.context import CryptContext
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
'''
DEIXEI ALGUNS CAMPO LIBERADOS PARA EFETUAR O LOGIN E CADASTRO 
O MESMO PARA TER ACESSO

USUARIO E SENHA DE TESTE CRIADO COM MESMO NOME = teste | OU fastapi
'''


load_dotenv()
#Pode  ser usar no secret_key a opcao = #os.getenv('SECRET_KEY')
SECRET_KEY = '1a30c4915edcc7136a258172641950fe0a7bed774a83418a' 
ACCESS_TOKEN_EXPIRE_MINUTES=60

manager = LoginManager(SECRET_KEY, token_url="/login", use_cookie=True)
manager.cookie_name = "auth"

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    with DBContext() as db:
        yield db

def get_hashed_password(plain_password):
    return pwd_ctx.hash(plain_password)

def verify_password(plain_password, hashed_password):
    return pwd_ctx.verify(plain_password,hashed_password)

@manager.user_loader()
def get_user(username: str, db: Session = None):
    if db is None:
        with DBContext() as db:
            return crud.get_user_by_username(db=db,username=username)
    return crud.get_user_by_username(db=db,username=username)

def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db=db,username=username)
    if not user:
        return None
    if not verify_password(plain_password=password,hashed_password=user.hashed_password):
        return None
    return user

class NotAuthenticatedException(Exception):
    pass

def not_authenticated_exception_handler(request, exception):
    return RedirectResponse("/login")

manager.not_authenticated_exception = NotAuthenticatedException
app.add_exception_handler(NotAuthenticatedException, not_authenticated_exception_handler)

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Home"})

#tasks são as tarefas em inglês
@app.get("/tasks")
def obter_tarefas(request: Request, db: Session = Depends(get_db), user: schemas.User = Depends(manager)):
    return templates.TemplateResponse("tasks.html", {"request": request, 
    "title": "Tasks", 
    "user": user, 
    "tasks": crud.get_tasks_by_user_id(db=db,id=user.id)})

@app.post("/tasks")
def adicionar_tarefas(request: Request, text: str = Form(...), db: Session = Depends(get_db), user: schemas.User = Depends(manager)):
    added = crud.add_task(db=db,task=schemas.TaskCreate(text=text),id=user.id)
    if not added:
        return templates.TemplateResponse("tasks.html", {"request": request,
        "title": "Tasks",
        "user": user,
        "tasks": crud.get_tasks_by_user_id(db=db,id=user.id),
        "invalid": True}, status_code=status.HTTP_400_BAD_REQUEST)
    else:
        return RedirectResponse("/tasks", status_code=status.HTTP_302_FOUND)

@app.get("/tasks/delete/{id}", response_class=RedirectResponse)
def deteltar_tarefas(id: str = Path(...), db: Session = Depends(get_db), user: schemas.User = Depends(manager)):
    crud.delete_task(db=db,id=id)
    return RedirectResponse("/tasks")

# RESPOST A REQUISIÇÃO DA API = https://api.openbrewerydb.org/breweries/
@app.get("/cervejas", response_class=HTMLResponse)
def todas_as_cervejas_brewery(request: Request, db: Session = Depends(get_db), user: schemas.User = Depends(manager)):
    
    request_api = requests.get('https://api.openbrewerydb.org/breweries/')
    print(request_api)
    data = request_api.json()
    return templates.TemplateResponse("api_brewerydb.html", {"request": request, 
            "title": "Cervejas", 
            "todas_info":data})

# PAGINA DE LOGIN
@app.get("/login")
def pagina_de_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login"})

@app.post("/login")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(username=form_data.username,password=form_data.password,db=db)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request,
        "title": "Login",
        "invalid": True}, status_code=status.HTTP_401_UNAUTHORIZED)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = manager.create_access_token(
        data={"sub": user.username},
        expires=access_token_expires
    )
    resp = RedirectResponse("/tasks", status_code=status.HTTP_302_FOUND)
    manager.set_cookie(resp,access_token)
    return resp

# CRIAR LOGIN
@app.get("/register")
def get_registro(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "Registrar"})

@app.post("/register")
def cadastrar_usuario_de_login(request: Request,
username: str = Form(...),
email: str = Form(...),
name: str = Form(...),
password: str = Form(...),
db: Session = Depends(get_db)):
    hashed_password = get_hashed_password(password)
    invalid = False
    if crud.get_user_by_username(db=db,username=username):
        invalid = True
    if crud.get_user_by_email(db=db,email=email):
        invalid = True
    
    if not invalid:
        crud.create_user(db=db, user=schemas.UserCreate(username=username,email=email,name=name,hashed_password=hashed_password))
        response = RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
        return response
    else:
        return templates.TemplateResponse("register.html",{"request": request, "title": "Register", "invalid": True},
        status_code=HTTP_400_BAD_REQUEST)
#DESLOGAR
@app.get("/logout")
def logout(response: Response):
    response = RedirectResponse("/")
    manager.set_cookie(response,None)
    return response
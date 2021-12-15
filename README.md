# FastApi | Processo seletivo #

<p align="center">
  <img width="500" height="305" src="FastApi.gif">
</p>
                                                      
**O que tem:**

 - Autenticação com OAuth2, protegendo todas as rotas, gerando token, que expira a cada hora, e o token deve ser utilizado em todos os endpoints;
- Desenvolva um endpoint com request method POST, com payload: User (Str), Order (Float), PreviousOrder (Boolean), 
retornando um JSON com a RESPONSE 200 e os items do payload. 
- Lembrando que esse item deve seguir as regras do item 01;
- Desenvolva um endpoint com request method GET, buscando dados da API OpenBreweries (https://api.openbrewerydb.org/breweries/), 
mostrando no resultado apenas um dicionário com os nomes das cervejas que estarão em uma lista.


# Como rodar a aplicação
 - Criar um  **ambiente virtual**, pode ver como criar pesquisando no google dependendo do seu sistema operacional
 - Para rodar você deve usar o  **pip install -r requirements.txt** para instalar as bibliotecas
 - Após instalar as bibliotecas é só o **uvicorn main:app --reload**
 
 # O servidor vai rodar em : http://127.0.0.1:8000/


**Serve como base para seus projetos com FastApi utilizando Python**

## Inglish Information ##

# FastApi-Full

**What have:**

- User registration

- hourly user expiration and security token generator

- Template consumption

- Authentication with login

- Registration of tasks

- Comsumption of another api, showing in a template all the beers, contacts and creation dates


**Serve as the basis for your FastApi projects using Python**


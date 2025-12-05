from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.users import router as users_router
from api.routes.catalog import router as catalog_router
from api.routes.events import router as events_router
from api.routes.usuarios import router as usuarios_router
from api.database import conectar as get_connection

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas organizadas por módulo
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(catalog_router, prefix="/api/catalog", tags=["Catalog"])
app.include_router(events_router, prefix="/api/events", tags=["Events"])
app.include_router(usuarios_router, prefix="/api/usuarios", tags=["Usuários"])

@app.get("/")
def home():
    return {"status": "online", "message": "API do Sistema Ateliê funcionando!"}

@app.get("/testdb")
def test_db():
    con = get_connection()
    if con:
        return {"status": "ok", "message": "Conexão MySQL funcionando!"}
    else:
        return {"status": "erro", "message": "Falha ao conectar ao MySQL"}

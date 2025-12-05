from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.categorias import router as categorias_router
from api.routes.itens import router as itens_router
# outros routers úteis (ex.: usuarios, eventos, auth)
from api.routes.usuarios import router as usuarios_router
from api.routes.eventos import router as eventos_router
from api.routes.auth import router as auth_router

app = FastAPI()

# Permitir requisições do App Kivy/Android
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers (APIRouter já define prefixes onde aplicável)
app.include_router(categorias_router)
app.include_router(itens_router)
app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(eventos_router)


@app.get("/")
def home():
    return {"status": "API funcionando!"}

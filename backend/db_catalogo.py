# backend/db_catalogo.py
from backend.api_client import api


# -----------------------------
# 1) LISTAR CATEGORIAS
# -----------------------------
def listar_categorias(id_usuario=None):
    """Lista todas as categorias"""
    resultado = api.get("/categorias")
    
    if "error" in resultado:
        print("Erro ao listar categorias:", resultado["error"])
        return []
    
    return resultado if isinstance(resultado, list) else []


# -----------------------------
# 2) ADICIONAR CATEGORIA
# -----------------------------
def adicionar_categoria(nome, id_usuario, icone_blob=None):
    """Adiciona uma nova categoria"""
    dados = {
        "nome_categoria": nome,
        "id_usuario": id_usuario
    }
    
    resultado = api.post("/categorias", data=dados)
    
    if "error" in resultado:
        print("Erro ao adicionar categoria:", resultado["error"])
        return False
    
    return True


# -----------------------------
# 3) EXCLUIR CATEGORIA
# -----------------------------
def excluir_categoria(id_categoria, id_usuario=None):
    """Exclui uma categoria"""
    resultado = api.delete(f"/categorias/{id_categoria}")
    
    if "error" in resultado:
        print("Erro ao excluir categoria:", resultado["error"])
        return False
    
    return True

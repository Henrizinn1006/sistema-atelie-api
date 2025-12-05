# backend/db_itens.py
from backend.api_client import api


# -----------------------------
# 1) LISTAR ITENS DE UMA CATEGORIA
# -----------------------------
def listar_itens(id_categoria, id_usuario=None):
    """Lista itens de uma categoria"""
    resultado = api.get(f"/categorias/{id_categoria}/itens")
    
    if "error" in resultado:
        print("Erro ao listar itens:", resultado["error"])
        return []
    
    return resultado if isinstance(resultado, list) else []


# -----------------------------
# 2) ADICIONAR ITEM
# -----------------------------
def adicionar_item(id_categoria, nome, abreviacao, qtd_total, img_blob, id_usuario):
    """Adiciona um novo item"""
    dados = {
        "nome_item": nome,
        "abreviacao": abreviacao,
        "quantidade_total": qtd_total,
        "id_categoria": id_categoria,
        "id_usuario": id_usuario
    }
    
    resultado = api.post(f"/categorias/{id_categoria}/itens", data=dados)
    
    if "error" in resultado:
        print("Erro ao adicionar item:", resultado["error"])
        return False
    
    return True


# -----------------------------
# 3) ATUALIZAR ITEM
# -----------------------------
def atualizar_item(id_item, nome, abreviacao, qtd_total, qtd_disp, img_blob, id_usuario):
    """Atualiza um item existente"""
    dados = {
        "nome_item": nome,
        "abreviacao": abreviacao,
        "quantidade_total": qtd_total,
        "quantidade_disponivel": qtd_disp
    }
    
    resultado = api.put(f"/itens/{id_item}", data=dados)
    
    if "error" in resultado:
        print("Erro ao atualizar item:", resultado["error"])
        return False
    
    return True


# -----------------------------
# 4) EXCLUIR ITEM
# -----------------------------
def excluir_item(id_item, id_usuario=None):
    """Exclui um item"""
    resultado = api.delete(f"/itens/{id_item}")
    
    if "error" in resultado:
        print("Erro ao excluir item:", resultado["error"])
        raise ValueError(resultado["error"])
    
    return True


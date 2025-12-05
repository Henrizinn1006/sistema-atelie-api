# backend/db_eventos.py
from backend.api_client import api
from datetime import datetime


# --------------------------------------------------------
# 🔹 1. CRIAR EVENTO
# --------------------------------------------------------
def criar_evento(nome_evento, data_evento, nome_cliente, endereco_evento, observacoes, created_by=None):
    """Cria um novo evento"""
    dados = {
        "nome_evento": nome_evento,
        "data_evento": data_evento.isoformat() if hasattr(data_evento, 'isoformat') else str(data_evento),
        "nome_cliente": nome_cliente,
        "endereco_evento": endereco_evento,
        "observacoes": observacoes,
        "created_by": created_by
    }
    
    resultado = api.post("/eventos", data=dados)
    
    if "error" in resultado:
        raise RuntimeError(f"Erro ao criar evento: {resultado['error']}")
    
    return resultado


# --------------------------------------------------------
# 🔹 2. LISTAR EVENTOS
# --------------------------------------------------------
def listar_eventos(id_usuario=None):
    """Lista todos os eventos"""
    resultado = api.get("/eventos")
    
    if "error" in resultado:
        print("Erro ao listar eventos:", resultado["error"])
        return []
    
    return resultado if isinstance(resultado, list) else []


# --------------------------------------------------------
# 🔹 3. BUSCAR EVENTO POR ID
# --------------------------------------------------------
def buscar_evento(id_evento):
    """Busca um evento específico"""
    resultado = api.get(f"/eventos/{id_evento}")
    
    if "error" in resultado:
        print("Erro ao buscar evento:", resultado["error"])
        return None
    
    return resultado


# --------------------------------------------------------
# 🔹 4. ATUALIZAR EVENTO
# --------------------------------------------------------
def atualizar_evento(id_evento, nome_evento, data_evento, nome_cliente, endereco_evento, observacoes):
    """Atualiza um evento existente"""
    dados = {
        "nome_evento": nome_evento,
        "data_evento": data_evento.isoformat() if hasattr(data_evento, 'isoformat') else str(data_evento),
        "nome_cliente": nome_cliente,
        "endereco_evento": endereco_evento,
        "observacoes": observacoes
    }
    
    resultado = api.put(f"/eventos/{id_evento}", data=dados)
    
    if "error" in resultado:
        raise RuntimeError(f"Erro ao atualizar evento: {resultado['error']}")
    
    return resultado


# --------------------------------------------------------
# 🔹 5. CANCELAR EVENTO
# --------------------------------------------------------
def cancelar_evento(id_evento):
    """Cancela um evento"""
    resultado = api.delete(f"/eventos/{id_evento}")
    
    if "error" in resultado:
        raise RuntimeError(f"Erro ao cancelar evento: {resultado['error']}")
    
    return resultado


# --------------------------------------------------------
# 🔹 6. ADICIONAR ITEM AO EVENTO
# --------------------------------------------------------
def adicionar_item_evento(id_evento, id_item, quantidade):
    """Adiciona um item ao evento"""
    dados = {
        "id_item": id_item,
        "quantidade": quantidade
    }
    
    resultado = api.post(f"/eventos/{id_evento}/itens", data=dados)
    
    if "error" in resultado:
        if "insuficiente" in resultado["error"].lower():
            raise ValueError(resultado["error"])
        raise RuntimeError(f"Erro ao adicionar item: {resultado['error']}")
    
    return resultado


# --------------------------------------------------------
# 🔹 6.1 ATUALIZAR ITEM DO EVENTO
# --------------------------------------------------------
def atualizar_item_evento(id_evento, id_item, nova_qtd, nova_obs=None):
    """Atualiza quantidade de um item no evento"""
    dados = {
        "quantidade": nova_qtd
    }
    
    resultado = api.put(f"/eventos/{id_evento}/itens/{id_item}", data=dados)
    
    if "error" in resultado:
        if "insuficiente" in resultado["error"].lower():
            raise ValueError(resultado["error"])
        raise RuntimeError(f"Erro ao atualizar item: {resultado['error']}")
    
    return resultado


# --------------------------------------------------------
# 🔹 7. LISTAR ITENS DO EVENTO
# --------------------------------------------------------
def listar_itens_evento(id_evento):
    """Lista todos os itens de um evento"""
    resultado = api.get(f"/eventos/{id_evento}/itens")
    
    if "error" in resultado:
        print("Erro ao listar itens do evento:", resultado["error"])
        return []
    
    return resultado if isinstance(resultado, list) else []


# --------------------------------------------------------
# 🔹 7.1 LISTAR ITENS DO CATÁLOGO
# --------------------------------------------------------
def listar_itens_catalogo():
    """Lista todos os itens do catálogo"""
    # A API não tem esse endpoint específico ainda
    # Por enquanto, retorna lista vazia ou busca todas as categorias
    resultado = api.get("/categorias")
    
    if "error" in resultado:
        return []
    
    # Buscar itens de todas as categorias
    todos_itens = []
    if isinstance(resultado, list):
        for cat in resultado:
            itens = api.get(f"/categorias/{cat['id_categoria']}/itens")
            if isinstance(itens, list):
                todos_itens.extend(itens)
    
    return todos_itens


# --------------------------------------------------------
# 🔹 8. ATIVAÇÃO MANUAL
# --------------------------------------------------------
def ativar_evento_manual(id_evento):
    """Ativa um evento manualmente"""
    resultado = api.post(f"/eventos/{id_evento}/ativar")
    
    if "error" in resultado:
        raise RuntimeError(f"Erro ao ativar evento: {resultado['error']}")
    
    return resultado


# --------------------------------------------------------
# 🔹 9. REGISTRAR DEVOLUÇÃO
# --------------------------------------------------------
def registrar_devolucao(id_evento, itens_devolvidos):
    """
    Registra devolução de itens
    
    itens_devolvidos: lista de dicts com formato:
    [{"id_item": 1, "devolvido": 10}, {"id_item": 2, "devolvido": 5}]
    """
    dados = {
        "itens": itens_devolvidos
    }
    
    resultado = api.post(f"/eventos/{id_evento}/concluir", data=dados)
    
    if "error" in resultado:
        raise RuntimeError(f"Erro ao registrar devolução: {resultado['error']}")
    
    return resultado


# --------------------------------------------------------
# 🔹 10. GERAR PDF DO EVENTO
# --------------------------------------------------------
def gerar_pdf_evento(id_evento):
    """
    Gera PDF do evento
    NOTA: A API não tem endpoint para PDF ainda
    Precisa implementar na API ou manter local
    """
    # TODO: Implementar endpoint na API ou manter geração local
    raise NotImplementedError("Geração de PDF precisa ser implementada")


# --------------------------------------------------------
# FUNÇÕES AUXILIARES (compatibilidade)
# --------------------------------------------------------
def ativacao_automatica():
    """Ativação automática - não implementado via API ainda"""
    # TODO: Implementar como job agendado no servidor
    pass


def _estoque_disponivel(id_item, qtd):
    """Verifica se há estoque disponível"""
    # A API já faz essa validação automaticamente
    return True


def _retirar_do_estoque(id_item, qtd):
    """Retira quantidade do estoque"""
    # A API já faz isso automaticamente na ativação
    pass


def _devolver_para_estoque(id_item, qtd):
    """Devolve quantidade ao estoque"""
    # A API já faz isso automaticamente na conclusão
    pass


def _ativar_evento(id_evento):
    """Função auxiliar de ativação"""
    return ativar_evento_manual(id_evento)

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from api.database import conectar

router = APIRouter(prefix="/eventos", tags=["Eventos"])


# ======================================================
# MODELOS
# ======================================================

class EventoCreate(BaseModel):
    nome_evento: str
    data_evento: str
    nome_cliente: str
    endereco_evento: str
    observacoes: str | None = None
    id_usuario: int


# ======================================================
# CRIAR EVENTO
# ======================================================
@router.post("/")
def criar_evento(evento: EventoCreate):

    con = conectar()
    if not con:
        raise HTTPException(500, "Erro ao conectar ao banco")

    cur = con.cursor()

    cur.execute("""
        INSERT INTO eventos 
        (nome_evento, data_evento, nome_cliente, endereco_evento, observacoes, status, id_usuario)
        VALUES (%s, %s, %s, %s, %s, 'pendente', %s)
    """, (
        evento.nome_evento,
        evento.data_evento,
        evento.nome_cliente,
        evento.endereco_evento,
        evento.observacoes,
        evento.id_usuario
    ))

    con.commit()
    novo_id = cur.lastrowid

    cur.close()
    con.close()

    return {"mensagem": "Evento criado com sucesso", "id_evento": novo_id}


# ======================================================
# LISTAR EVENTOS DO USUÁRIO
# ======================================================
@router.get("/{id_usuario}")
def listar_eventos(id_usuario: int):

    con = conectar()
    if not con:
        raise HTTPException(500, "Erro ao conectar ao banco")

    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT * FROM eventos
        WHERE id_usuario = %s
        ORDER BY data_evento ASC
    """, (id_usuario,))

    eventos = cur.fetchall()

    cur.close()
    con.close()

    return eventos


# ======================================================
# BUSCAR EVENTO POR ID
# ======================================================
@router.get("/detalhes/{id_evento}")
def buscar_evento(id_evento: int):

    con = conectar()
    if not con:
        raise HTTPException(500, "Erro ao conectar ao banco")

    cur = con.cursor(dictionary=True)

    cur.execute("SELECT * FROM eventos WHERE id_evento = %s", (id_evento,))
    evento = cur.fetchone()

    if not evento:
        raise HTTPException(404, "Evento não encontrado")

    cur.close()
    con.close()

    return evento


# ======================================================
# CANCELAR EVENTO
# ======================================================
@router.delete("/{id_evento}")
def cancelar_evento(id_evento: int):

    con = conectar()
    if not con:
        raise HTTPException(500, "Erro ao conectar ao banco")

    cur = con.cursor()

    cur.execute("""
        UPDATE eventos
        SET status = 'cancelado'
        WHERE id_evento = %s
    """, (id_evento,))

    con.commit()

    cur.close()
    con.close()

    return {"mensagem": "Evento cancelado com sucesso"}

# ======================================================
# ADICIONAR ITEM AO EVENTO
# ======================================================
@router.post("/{id_evento}/itens")
def adicionar_item_evento(id_evento: int, dados: dict):

    id_item = dados.get("id_item")
    quantidade = dados.get("quantidade")

    if quantidade <= 0:
        raise HTTPException(400, "Quantidade inválida")

    con = conectar()
    cur = con.cursor(dictionary=True)

    # Consulta quantidade disponível
    cur.execute("""
        SELECT quantidade_disponivel 
        FROM catalogo_itens 
        WHERE id_item = %s
    """, (id_item,))
    item = cur.fetchone()

    if not item:
        raise HTTPException(404, "Item não encontrado")

    if item["quantidade_disponivel"] < quantidade:
        raise HTTPException(400, "Estoque insuficiente")

    # Insere o item no evento
    cur.execute("""
        INSERT INTO eventos_itens 
        (id_evento, id_item, quantidade_locada, quantidade_devolvida, quebrado)
        VALUES (%s, %s, %s, 0, 0)
    """, (id_evento, id_item, quantidade))

    con.commit()

    cur.close()
    con.close()

    return {"mensagem": "Item adicionado ao evento"}

# ======================================================
# LISTAR ITENS DO EVENTO
# ======================================================
@router.get("/{id_evento}/itens")
def listar_itens_evento(id_evento: int):

    con = conectar()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT ei.id_item,
               ei.quantidade_locada,
               ei.quantidade_devolvida,
               ci.nome_item,
               ci.abreviacao,
               ci.imagem
        FROM eventos_itens ei
        JOIN catalogo_itens ci ON ci.id_item = ei.id_item
        WHERE ei.id_evento = %s
    """, (id_evento,))

    itens = cur.fetchall()

    cur.close()
    con.close()

    return itens

# ======================================================
# EDITAR QUANTIDADE DE ITEM NO EVENTO
# ======================================================
@router.put("/{id_evento}/itens/{id_item}")
def editar_item_evento(id_evento: int, id_item: int, dados: dict):

    nova_qtd = dados.get("quantidade")
    if nova_qtd <= 0:
        raise HTTPException(400, "Quantidade inválida")

    con = conectar()
    cur = con.cursor(dictionary=True)

    # Busca locado atual
    cur.execute("""
        SELECT quantidade_locada 
        FROM eventos_itens 
        WHERE id_evento = %s AND id_item = %s
    """, (id_evento, id_item))

    item = cur.fetchone()
    if not item:
        raise HTTPException(404, "Item não encontrado no evento")

    # Atualiza
    cur.execute("""
        UPDATE eventos_itens
        SET quantidade_locada = %s
        WHERE id_evento = %s AND id_item = %s
    """, (nova_qtd, id_evento, id_item))

    con.commit()
    cur.close()
    con.close()

    return {"mensagem": "Item atualizado"}

# ======================================================
# ATIVAR EVENTO (BAIXAR ESTOQUE)
# ======================================================
@router.post("/{id_evento}/ativar")
def ativar_evento(id_evento: int):

    con = conectar()
    cur = con.cursor(dictionary=True)

    # Busca itens do evento
    cur.execute("""
        SELECT id_item, quantidade_locada
        FROM eventos_itens
        WHERE id_evento = %s
    """, (id_evento,))
    itens = cur.fetchall()

    # Baixar estoque
    for item in itens:
        cur.execute("""
            UPDATE catalogo_itens
            SET quantidade_disponivel = quantidade_disponivel - %s
            WHERE id_item = %s
        """, (item["quantidade_locada"], item["id_item"]))

    # Mudar status do evento
    cur.execute("""
        UPDATE eventos
        SET status = 'ativo'
        WHERE id_evento = %s
    """, (id_evento,))

    con.commit()
    cur.close()
    con.close()

    return {"mensagem": "Evento ativado com sucesso"}

from fpdf import FPDF
import base64
import tempfile

# ======================================================
# GERAR PDF DO EVENTO
# ======================================================
@router.get("/{id_evento}/pdf")
def gerar_pdf_evento(id_evento: int):
    con = conectar()
    cur = con.cursor(dictionary=True)

    # Buscar info do evento
    cur.execute("""
        SELECT nome_evento, data_evento, nome_cliente, endereco_evento, observacoes
        FROM eventos
        WHERE id_evento = %s
    """, (id_evento,))
    evento = cur.fetchone()

    if not evento:
        raise HTTPException(404, "Evento não encontrado")

    # Buscar itens do evento
    cur.execute("""
        SELECT ci.nome_item,
               ci.imagem,
               ei.quantidade_locada
        FROM eventos_itens ei
        JOIN catalogo_itens ci ON ci.id_item = ei.id_item
        WHERE ei.id_evento = %s
    """, (id_evento,))
    itens = cur.fetchall()

    cur.close()
    con.close()

    # Criar PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    # Título
    pdf.cell(0, 10, "Ficha de Retirada - EventPlus", ln=True, align="C")

    pdf.ln(5)
    pdf.set_font("Arial", size=12)

    # Dados do evento
    pdf.cell(0, 8, f"Evento: {evento['nome_evento']}", ln=True)
    pdf.cell(0, 8, f"Data: {evento['data_evento']}", ln=True)
    pdf.cell(0, 8, f"Cliente: {evento['nome_cliente']}", ln=True)
    pdf.multi_cell(0, 8, f"Endereço: {evento['endereco_evento']}")
    pdf.multi_cell(0, 8, f"Observações: {evento['observacoes'] or 'Nenhuma'}")

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Itens do Evento:", ln=True)

    pdf.set_font("Arial", size=12)

    # Para cada item
    for item in itens:
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"{item['nome_item']} (Qtd: {item['quantidade_locada']})", ln=True)

        # Adicionar imagem se existir
        if item["imagem"]:
            try:
                # Decodificar imagem
                img_data = item["imagem"]
                img_bytes = img_data

                # Criar arquivo temporário
                temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                temp.write(img_bytes)
                temp.close()

                # Inserir imagem
                pdf.image(temp.name, w=40)

            except Exception as e:
                pdf.set_font("Arial", size=10)
                pdf.cell(0, 6, "(Erro ao carregar imagem)", ln=True)

    # Salvar PDF temporário e devolver como download
    output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(output.name)

    # Ler o arquivo para enviar na resposta
    with open(output.name, "rb") as f:
        pdf_bytes = f.read()

    return Response(content=pdf_bytes, media_type="application/pdf")

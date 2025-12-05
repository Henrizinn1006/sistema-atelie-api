from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from database import conectar

router = APIRouter(prefix="/itens", tags=["Itens"])


# =======================================================
# ATUALIZAR ITEM
# (PUT /itens/{id_item})
# COMPATÍVEL com db_itens.atualizar_item(...)
# =======================================================
@router.put("/{id_item}")
def atualizar_item(
    id_item: int,
    nome_item: str = Form(...),
    abreviacao: str = Form(""),
    quantidade_total: int = Form(...),
    quantidade_disponivel: int = Form(...)
):
    con = conectar()
    if not con:
        raise HTTPException(500, "Erro de conexão")

    cur = con.cursor()

    try:
        cur.execute("""
            UPDATE catalogo_itens
            SET nome_item=%s,
                abreviacao=%s,
                quantidade_total=%s,
                quantidade_disponivel=%s
            WHERE id_item=%s
        """, (
            nome_item,
            abreviacao if abreviacao is not None else "",
            quantidade_total,
            quantidade_disponivel,
            id_item
        ))

        con.commit()
        return {"mensagem": "Item atualizado com sucesso"}

    finally:
        cur.close()
        con.close()


# =======================================================
# EXCLUIR ITEM
# (DELETE /itens/{id_item})
# COMPATÍVEL com db_itens.excluir_item(...)
# =======================================================
@router.delete("/{id_item}")
def excluir_item(id_item: int):

    con = conectar()
    if not con:
        raise HTTPException(500, "Erro de conexão")

    cur = con.cursor()

    try:
        cur.execute("DELETE FROM eventos_itens WHERE id_item = %s", (id_item,))
        cur.execute("DELETE FROM catalogo_itens WHERE id_item = %s", (id_item,))
        con.commit()

        return {"mensagem": "Item excluído com sucesso"}

    finally:
        cur.close()
        con.close()


# =======================================================
# ALTERAR / ENVIAR IMAGEM DO ITEM
# (POST /itens/{id_item}/imagem)
# Para usar com galeria no Android depois
# =======================================================
@router.post("/{id_item}/imagem")
async def upload_imagem_item(id_item: int, arquivo: UploadFile = File(...)):
    con = conectar()
    if not con:
        raise HTTPException(500, "Erro de conexão")

    conteudo = await arquivo.read()

    cur = con.cursor()

    try:
        cur.execute("""
            UPDATE catalogo_itens
            SET imagem = %s
            WHERE id_item = %s
        """, (conteudo, id_item))

        con.commit()
        return {"status": "ok", "mensagem": "Imagem enviada com sucesso!"}

    finally:
        cur.close()
        con.close()

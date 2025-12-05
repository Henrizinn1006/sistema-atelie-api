from fastapi import APIRouter, HTTPException, Form
from api.database import conectar

router = APIRouter(prefix="/categorias", tags=["Categorias"])


# =======================================================
# LISTAR CATEGORIAS DO USUÁRIO
# =======================================================
@router.get("/")
def listar_categorias(id_usuario: int):

    con = conectar()
    if not con:
        raise HTTPException(500, "Erro ao conectar ao banco")

    cur = con.cursor(dictionary=True)

    try:
        cur.execute("""
            SELECT id_categoria, nome_categoria
            FROM catalogo_categorias
            WHERE id_usuario = %s
            ORDER BY nome_categoria ASC
        """, (id_usuario,))

        categorias = cur.fetchall()
        return categorias

    finally:
        cur.close()
        con.close()


# =======================================================
# CRIAR CATEGORIA
# (POST /categorias com form-data: nome_categoria, id_usuario)
# =======================================================
@router.post("/")
def criar_categoria(
    nome_categoria: str = Form(...),
    id_usuario: int = Form(...)
):

    con = conectar()
    if not con:
        raise HTTPException(500, "Erro ao conectar ao banco")

    cur = con.cursor()

    try:
        # Verifica duplicada pro mesmo usuário
        cur.execute("""
            SELECT id_categoria
            FROM catalogo_categorias
            WHERE nome_categoria = %s AND id_usuario = %s
        """, (nome_categoria, id_usuario))

        existe = cur.fetchone()
        if existe:
            raise HTTPException(400, "Já existe uma categoria com esse nome")

        cur.execute("""
            INSERT INTO catalogo_categorias (nome_categoria, id_usuario)
            VALUES (%s, %s)
        """, (nome_categoria, id_usuario))

        con.commit()
        novo_id = cur.lastrowid

        return {"mensagem": "Categoria criada", "id_categoria": novo_id}

    finally:
        cur.close()
        con.close()


# =======================================================
# EXCLUIR CATEGORIA
# (DELETE /categorias/{id_categoria})
# =======================================================
@router.delete("/{id_categoria}")
def excluir_categoria(id_categoria: int):

    con = conectar()
    if not con:
        raise HTTPException(500, "Erro ao conectar ao banco")

    cur = con.cursor()

    try:
        # Verifica se existe
        cur.execute(
            "SELECT id_categoria FROM catalogo_categorias WHERE id_categoria = %s",
            (id_categoria,)
        )
        existe = cur.fetchone()

        if not existe:
            raise HTTPException(404, "Categoria não encontrada")

        # Exclui itens da categoria (pra não ficar lixo)
        cur.execute(
            "DELETE FROM catalogo_itens WHERE id_categoria = %s",
            (id_categoria,)
        )

        # Exclui a categoria
        cur.execute(
            "DELETE FROM catalogo_categorias WHERE id_categoria = %s",
            (id_categoria,)
        )

        con.commit()
        return {"mensagem": "Categoria excluída com sucesso"}

    finally:
        cur.close()
        con.close()


# =======================================================
# LISTAR ITENS DE UMA CATEGORIA
# (GET /categorias/{id_categoria}/itens?id_usuario=X)
# COMPATÍVEL com db_itens.listar_itens(...)
# =======================================================
@router.get("/{id_categoria}/itens")
def listar_itens_categoria(id_categoria: int, id_usuario: int):

    con = conectar()
    if not con:
        raise HTTPException(500, "Erro ao conectar ao banco")

    cur = con.cursor(dictionary=True)

    try:
        cur.execute("""
            SELECT id_item, nome_item, abreviacao,
                   quantidade_total, quantidade_disponivel,
                   imagem
            FROM catalogo_itens
            WHERE id_categoria = %s AND id_usuario = %s
            ORDER BY nome_item ASC
        """, (id_categoria, id_usuario))

        itens = cur.fetchall()
        return itens

    finally:
        cur.close()
        con.close()


# =======================================================
# ADICIONAR ITEM NA CATEGORIA
# (POST /categorias/{id_categoria}/itens)
# Espera form-data igual db_itens.adicionar_item
# =======================================================
@router.post("/{id_categoria}/itens")
def adicionar_item_categoria(
    id_categoria: int,
    nome_item: str = Form(...),
    abreviacao: str = Form(""),
    quantidade_total: int = Form(...),
    id_usuario: int = Form(...)
):
    """
    OBS: por enquanto não estamos recebendo imagem aqui, porque
    o seu db_itens.py ainda não envia o blob.
    Depois podemos fazer um endpoint separado só pra imagem.
    """

    con = conectar()
    if not con:
        raise HTTPException(500, "Erro ao conectar ao banco")

    cur = con.cursor()

    try:
        cur.execute("""
            INSERT INTO catalogo_itens
            (id_categoria, nome_item, abreviacao,
             quantidade_total, quantidade_disponivel,
             id_usuario, imagem)
            VALUES (%s, %s, %s, %s, %s, %s, NULL)
        """, (
            id_categoria,
            nome_item,
            abreviacao,
            quantidade_total,
            quantidade_total,   # disponivel = total no início
            id_usuario
        ))

        con.commit()
        novo_id = cur.lastrowid

        return {"mensagem": "Item criado com sucesso", "id_item": novo_id}

    finally:
        cur.close()
        con.close()

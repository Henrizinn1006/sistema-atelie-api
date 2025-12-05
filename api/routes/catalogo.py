from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.conexao_mysql import conectar

router = APIRouter()


# =============================
# 🔹 1. LISTAR CATEGORIAS
# =============================
@router.get("/categorias")
def listar_categorias(id_usuario: int):
    con = conectar()
    cur = con.cursor(dictionary=True)

    try:
        cur.execute("""
            SELECT id_categoria, nome_categoria
            FROM catalogo_categorias
            WHERE id_usuario = %s
            ORDER BY nome_categoria ASC
        """, (id_usuario,))
        return cur.fetchall()

    except Exception as e:
        return {"error": str(e)}

    finally:
        cur.close()
        con.close()



# =============================
# 🔹 2. ADICIONAR CATEGORIA
# =============================
@router.post("/categorias")
def adicionar_categoria(
    nome_categoria: str = Form(...),
    id_usuario: int = Form(...)
):
    con = conectar()
    cur = con.cursor()

    try:
        cur.execute("""
            INSERT INTO catalogo_categorias (nome_categoria, id_usuario)
            VALUES (%s, %s)
        """, (nome_categoria, id_usuario))

        con.commit()
        return {"status": "ok"}

    except Exception as e:
        return {"error": str(e)}

    finally:
        cur.close()
        con.close()



# =============================
# 🔹 3. EXCLUIR CATEGORIA
# =============================
@router.delete("/categorias/{id_categoria}")
def excluir_categoria(id_categoria: int):
    con = conectar()
    cur = con.cursor()

    try:
        cur.execute("DELETE FROM catalogo_itens WHERE id_categoria = %s", (id_categoria,))
        cur.execute("DELETE FROM catalogo_categorias WHERE id_categoria = %s", (id_categoria,))
        con.commit()
        return {"status": "ok"}

    except Exception as e:
        return {"error": str(e)}

    finally:
        cur.close()
        con.close()



# =============================
# 🔹 4. LISTAR ITENS DA CATEGORIA (CORRIGIDO!)
# =============================
@router.get("/categorias/{id_categoria}/itens")
def listar_itens(id_categoria: int, id_usuario: int):
    """
    ESSENCIAL:
    o frontend envia id_usuario e espera itens SOMENTE dele.
    """
    con = conectar()
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

        return cur.fetchall()

    except Exception as e:
        return {"error": str(e)}

    finally:
        cur.close()
        con.close()



# =============================
# 🔹 5. ADICIONAR ITEM (COM FOTO)
# =============================
@router.post("/categorias/{id_categoria}/itens")
async def adicionar_item(
    id_categoria: int,
    nome_item: str = Form(...),
    abreviacao: str = Form(""),
    quantidade_total: int = Form(...),
    id_usuario: int = Form(...),
    imagem: UploadFile = File(None)
):
    conteudo_img = None

    if imagem:
        conteudo_img = await imagem.read()

    con = conectar()
    cur = con.cursor()

    try:
        cur.execute("""
            INSERT INTO catalogo_itens
                (id_categoria, nome_item, abreviacao,
                 quantidade_total, quantidade_disponivel, imagem, id_usuario)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            id_categoria,
            nome_item,
            abreviacao,
            quantidade_total,
            quantidade_total,
            conteudo_img,
            id_usuario
        ))

        con.commit()
        return {"status": "ok"}

    except Exception as e:
        return {"error": str(e)}

    finally:
        cur.close()
        con.close()



# =============================
# 🔹 6. ATUALIZAR ITEM
# =============================
@router.put("/itens/{id_item}")
async def atualizar_item(
    id_item: int,
    nome_item: str = Form(...),
    abreviacao: str = Form(""),
    quantidade_total: int = Form(...),
    quantidade_disponivel: int = Form(...),
    imagem: UploadFile = File(None)
):
    nova_img = None

    if imagem:
        nova_img = await imagem.read()

    con = conectar()
    cur = con.cursor()

    try:
        if nova_img:
            cur.execute("""
                UPDATE catalogo_itens
                SET nome_item=%s, abreviacao=%s,
                    quantidade_total=%s, quantidade_disponivel=%s,
                    imagem=%s
                WHERE id_item=%s
            """, (
                nome_item, abreviacao,
                quantidade_total, quantidade_disponivel,
                nova_img, id_item
            ))
        else:
            cur.execute("""
                UPDATE catalogo_itens
                SET nome_item=%s, abreviacao=%s,
                    quantidade_total=%s, quantidade_disponivel=%s
                WHERE id_item=%s
            """, (
                nome_item, abreviacao,
                quantidade_total, quantidade_disponivel,
                id_item
            ))

        con.commit()
        return {"status": "ok"}

    except Exception as e:
        return {"error": str(e)}

    finally:
        cur.close()
        con.close()



# =============================
# 🔹 7. EXCLUIR ITEM
# =============================
@router.delete("/itens/{id_item}")
def excluir_item(id_item: int):
    con = conectar()
    cur = con.cursor()

    try:
        cur.execute("DELETE FROM catalogo_itens WHERE id_item = %s", (id_item,))
        con.commit()
        return {"status": "ok"}

    except Exception as e:
        return {"error": str(e)}

    finally:
        cur.close()
        con.close()



# =============================
# 🔹 8. ATUALIZAR SOMENTE A FOTO
# =============================
@router.post("/itens/{id_item}/imagem")
async def upload_imagem_item(id_item: int, arquivo: UploadFile = File(...)):
    conteudo = await arquivo.read()

    con = conectar()
    cur = con.cursor()

    try:
        cur.execute("""
            UPDATE catalogo_itens
            SET imagem = %s
            WHERE id_item = %s
        """, (conteudo, id_item))

        con.commit()
        return {"status": "ok"}

    except Exception as e:
        return {"error": str(e)}

    finally:
        cur.close()
        con.close()

from fastapi import APIRouter, UploadFile, File, HTTPException
from api.database import conectar

router = APIRouter(prefix="/imagens", tags=["Imagens"])

# =======================================================
# UPLOAD DE IMAGEM DE ITEM
# =======================================================
@router.post("/item/{id_item}")
async def upload_imagem_item(id_item: int, arquivo: UploadFile = File(...)):

    # Verifica extensão permitida
    extensoes_validas = ["image/jpeg", "image/png", "image/jpg"]
    if arquivo.content_type not in extensoes_validas:
        raise HTTPException(400, "Formato inválido. Use JPG ou PNG.")

    # Lê o arquivo inteiro como bytes
    conteudo = await arquivo.read()

    con = conectar()
    if not con:
        raise HTTPException(500, "Erro ao conectar ao banco")

    cur = con.cursor()

    cur.execute("""
        UPDATE catalogo_itens
        SET imagem = %s
        WHERE id_item = %s
    """, (conteudo, id_item))

    con.commit()
    cur.close()
    con.close()

    return {"mensagem": "Imagem enviada com sucesso!"}

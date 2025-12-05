from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.database import conectar
import random
import smtplib
from email.mime.text import MIMEText

router = APIRouter(prefix="/auth", tags=["Autenticação"])


# ===========================================================
# 🔹 MODELOS
# ===========================================================

class Recuperar(BaseModel):
    email: str

class Verificar(BaseModel):
    email: str
    codigo_digitado: str

class NovaSenha(BaseModel):
    email: str
    nova_senha: str


# ===========================================================
# 🔹 FUNÇÃO PARA ENVIAR E-MAIL
# ===========================================================

def enviar_email(destino, codigo):
    try:
        remetente = "eventmaster78@gmail.com"
        senha_app = "tadi gnsd znjd cxxn"

        msg = MIMEText(f"Seu código de recuperação é: {codigo}")
        msg["Subject"] = "Recuperação de Senha - EventPlus"
        msg["From"] = remetente
        msg["To"] = destino

        servidor = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        servidor.login(remetente, senha_app)
        servidor.sendmail(remetente, destino, msg.as_string())
        servidor.quit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar email: {e}")


# ===========================================================
# 🔹 1) GERAR E ENVIAR CÓDIGO DE RECUPERAÇÃO
# ===========================================================

@router.post("/recuperar")
def recuperar_senha(dados: Recuperar):

    email = dados.email

    con = conectar()
    cur = con.cursor(dictionary=True)

    # Verifica se email existe
    cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    usuario = cur.fetchone()

    if not usuario:
        raise HTTPException(404, "Email não cadastrado")

    # Gera código
    codigo = str(random.randint(100000, 999999))

    # Salva temporariamente na tabela
    cur.execute("""
        UPDATE usuarios
        SET codigo_recuperacao = %s
        WHERE email = %s
    """, (codigo, email))

    con.commit()

    # Envia email
    enviar_email(email, codigo)

    cur.close()
    con.close()

    return {"mensagem": "Código enviado!"}



# ===========================================================
# 🔹 2) VERIFICAR CÓDIGO DIGITADO
# ===========================================================

@router.post("/verificar")
def verificar_codigo(dados: Verificar):

    email = dados.email
    codigo_digitado = dados.codigo_digitado

    con = conectar()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT codigo_recuperacao 
        FROM usuarios 
        WHERE email = %s
    """, (email,))

    row = cur.fetchone()

    if not row:
        raise HTTPException(404, "Usuário não encontrado")

    if row["codigo_recuperacao"] != codigo_digitado:
        raise HTTPException(400, "Código incorreto")

    cur.close()
    con.close()

    return {"mensagem": "Código correto"}


# ===========================================================
# 🔹 3) DEFINIR NOVA SENHA
# ===========================================================

@router.post("/nova-senha")
def nova_senha(dados: NovaSenha):

    email = dados.email
    nova_senha = dados.nova_senha

    con = conectar()
    cur = con.cursor()

    cur.execute("""
        UPDATE usuarios
        SET senha = %s, codigo_recuperacao = NULL
        WHERE email = %s
    """, (nova_senha, email))

    con.commit()

    cur.close()
    con.close()

    return {"mensagem": "Senha alterada com sucesso!"}

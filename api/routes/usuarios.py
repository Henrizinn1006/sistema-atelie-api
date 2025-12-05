from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from database import conectar
import random
from datetime import datetime, timedelta

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

# =======================================================
# MODELOS
# =======================================================

class UsuarioCadastro(BaseModel):
    nome: str
    email: EmailStr
    senha: str

class UsuarioLogin(BaseModel):
    nome: str
    senha: str

class UsuarioNovaSenha(BaseModel):
    email: EmailStr
    nova_senha: str

class UsuarioCodigo(BaseModel):
    email: EmailStr
    codigo_digitado: str

# =======================================================
# CADASTRAR USUÁRIO
# =======================================================
@router.post("/cadastrar")
def cadastrar_usuario(dados: UsuarioCadastro):

    con = conectar()
    if not con:
        raise HTTPException(500, "Erro ao conectar no banco")

    cur = con.cursor(dictionary=True)

    # Verifica duplicidade
    cur.execute("SELECT id_usuario FROM usuarios WHERE email=%s OR nome=%s",
                (dados.email, dados.nome))
    existe = cur.fetchone()

    if existe:
        raise HTTPException(400, "Usuário ou email já cadastrado.")

    # Inserir usuário
    cur.execute(
        "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)",
        (dados.nome, dados.email, dados.senha)
    )
    con.commit()

    cur.close()
    con.close()

    return {"mensagem": "Usuário cadastrado com sucesso!"}

# =======================================================
# LOGIN
# =======================================================
@router.post("/login")
def login(dados: UsuarioLogin):

    con = conectar()
    if not con:
        raise HTTPException(500, "Erro ao conectar")

    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM usuarios WHERE nome=%s AND senha=%s",
                (dados.nome, dados.senha))
    user = cur.fetchone()

    cur.close()
    con.close()

    if not user:
        raise HTTPException(401, "Usuário ou senha inválidos")

    return {"status": "ok", "usuario": user}

# =======================================================
# GERAR CÓDIGO PARA RECUPERAÇÃO DE SENHA
# =======================================================
@router.post("/recuperar")
def recuperar_senha(email: EmailStr):

    con = conectar()
    if not con:
        raise HTTPException(500, "Erro ao conectar")

    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
    user = cur.fetchone()

    if not user:
        raise HTTPException(404, "Email não encontrado.")

    codigo = random.randint(100000, 999999)
    validade = datetime.now() + timedelta(minutes=10)

    cur.execute("""
        INSERT INTO recuperacao_senha (email, codigo, validade)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE codigo=%s, validade=%s
    """, (email, codigo, validade, codigo, validade))

    con.commit()
    cur.close()
    con.close()

    # ⚠️ No futuro enviaremos por email de verdade
    return {"mensagem": "Código enviado!", "codigo_debug": codigo}

# =======================================================
# VALIDAR CÓDIGO DE RECUPERAÇÃO
# =======================================================
@router.post("/verificar")
def verificar_codigo(dados: UsuarioCodigo):

    con = conectar()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT * FROM recuperacao_senha
        WHERE email=%s AND codigo=%s
    """, (dados.email, dados.codigo_digitado))

    row = cur.fetchone()

    if not row:
        raise HTTPException(401, "Código inválido")

    if datetime.now() > row["validade"]:
        raise HTTPException(401, "Código expirado")

    return {"status": "ok"}

# =======================================================
# DEFINIR NOVA SENHA
# =======================================================
@router.post("/nova-senha")
def nova_senha(dados: UsuarioNovaSenha):

    con = conectar()
    cur = con.cursor()

    cur.execute("UPDATE usuarios SET senha=%s WHERE email=%s",
                (dados.nova_senha, dados.email))

    con.commit()
    cur.close()
    con.close()

    return {"mensagem": "Senha alterada com sucesso!"}

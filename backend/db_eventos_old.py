import os
from datetime import datetime, timedelta
from backend.conexao_mysql import conectar


# --------------------------------------------------------
# 🔹 1. CRIAR EVENTO
# --------------------------------------------------------
def criar_evento(nome_evento, data_evento, nome_cliente, endereco_evento, observacoes, created_by=None):
    con = conectar()
    if not con:
        raise RuntimeError("Não foi possível conectar ao banco de dados")
    cur = con.cursor()

    try:
        cur.execute("""
            INSERT INTO eventos (nome_evento, data_evento, nome_cliente, endereco_evento, observacoes, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nome_evento, data_evento, nome_cliente, endereco_evento, observacoes, created_by))
        con.commit()
    finally:
        try: cur.close()
        except: pass
        try: con.close()
        except: pass


# --------------------------------------------------------
# 🔹 2. LISTAR EVENTOS
# --------------------------------------------------------
def listar_eventos(id_usuario):
    con = conectar()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT * FROM eventos
        WHERE created_by = %s
        ORDER BY data_evento ASC
    """, (id_usuario,))

    dados = cur.fetchall()
    cur.close()
    con.close()
    return dados


# --------------------------------------------------------
# 🔹 3. BUSCAR EVENTO POR ID
# --------------------------------------------------------
def buscar_evento(id_evento):
    con = conectar()
    cur = con.cursor(dictionary=True)

    cur.execute("SELECT * FROM eventos WHERE id_evento = %s", (id_evento,))
    dado = cur.fetchone()

    cur.close()
    con.close()
    return dado


# --------------------------------------------------------
# 🔹 4. ATUALIZAR EVENTO
# --------------------------------------------------------
def atualizar_evento(id_evento, nome_evento, data_evento, nome_cliente, endereco_evento, observacoes):
    con = conectar()
    cur = con.cursor()

    cur.execute("""
        UPDATE eventos
        SET nome_evento=%s, data_evento=%s, nome_cliente=%s,
            endereco_evento=%s, observacoes=%s
        WHERE id_evento=%s
    """, (nome_evento, data_evento, nome_cliente, endereco_evento, observacoes, id_evento))

    con.commit()
    cur.close()
    con.close()


# --------------------------------------------------------
# 🔹 5. CANCELAR EVENTO
# --------------------------------------------------------
def cancelar_evento(id_evento):
    con = conectar()
    cur = con.cursor()

    itens = listar_itens_evento(id_evento)
    evento = buscar_evento(id_evento)

    # se estava ativo → devolve estoque
    if evento["status"] == "ativo":
        for it in itens:
            _devolver_para_estoque(it["id_item"], it["quantidade_locada"])

    cur.execute("UPDATE eventos SET status='cancelado' WHERE id_evento = %s", (id_evento,))
    con.commit()

    cur.close()
    con.close()


# --------------------------------------------------------
# 🔹 6. ADICIONAR ITEM AO EVENTO (com validação de estoque)
# --------------------------------------------------------
def adicionar_item_evento(id_evento, id_item, quantidade):
    con = conectar()
    cur = con.cursor(dictionary=True)

    cur.execute("SELECT quantidade_disponivel FROM catalogo_itens WHERE id_item=%s", (id_item,))
    dado = cur.fetchone()

    if not dado:
        cur.close()
        con.close()
        raise ValueError("Item não encontrado.")

    estoque = dado["quantidade_disponivel"]

    if quantidade > estoque:
        cur.close()
        con.close()
        raise ValueError(f"Estoque insuficiente. Disponível: {estoque}")

    cur = con.cursor()
    cur.execute("""
        INSERT INTO itens_evento (id_evento, id_item, quantidade_locada)
        VALUES (%s, %s, %s)
    """, (id_evento, id_item, quantidade))

    con.commit()
    cur.close()
    con.close()


# --------------------------------------------------------
# 🔹 6.1 ATUALIZAR ITEM DO EVENTO (edição)
# --------------------------------------------------------
def atualizar_item_evento(id_evento, id_item, nova_qtd, nova_obs=None):
    con = conectar()

    # 1) Buscar quantidade antiga
    cur = con.cursor(dictionary=True)
    cur.execute("""
        SELECT quantidade_locada
        FROM itens_evento
        WHERE id_evento=%s AND id_item=%s
    """, (id_evento, id_item))
    row = cur.fetchone()
    qtd_antiga = row["quantidade_locada"] if row else 0

    delta = nova_qtd - qtd_antiga

    # 2) Ajustar estoque pela diferença
    if delta > 0:
        # Quer aumentar → precisa tirar mais do estoque
        if not _estoque_disponivel(id_item, delta):
            cur.close()
            con.close()
            raise ValueError("Estoque insuficiente para aumentar a quantidade.")
        _retirar_do_estoque(id_item, delta)
    elif delta < 0:
        # Diminuiu a quantidade → devolve diferença
        _devolver_para_estoque(id_item, -delta)

    # 3) Atualizar registro do item no evento
    cur = con.cursor()
    try:
        cur.execute(
            """
            UPDATE itens_evento
            SET quantidade_locada=%s
            WHERE id_evento=%s AND id_item=%s
            """,
            (nova_qtd, id_evento, id_item)
        )
    except Exception as e:
        # Caso exista coluna de observações no seu schema, ajuste aqui:
        # SET quantidade_locada=%s, observacoes=%s
        # e passe (nova_qtd, nova_obs, id_evento, id_item)
        raise

    con.commit()
    cur.close()
    con.close()


# --------------------------------------------------------
# 🔹 7. LISTAR ITENS DO EVENTO
# --------------------------------------------------------
def listar_itens_evento(id_evento):
    con = conectar()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT ie.*, ci.nome_item, ci.abreviacao, ci.imagem
        FROM itens_evento ie
        JOIN catalogo_itens ci ON ci.id_item = ie.id_item
        WHERE ie.id_evento=%s
    """, (id_evento,))

    dados = cur.fetchall()

    cur.close()
    con.close()
    return dados


# --------------------------------------------------------
# 🔹 7.1 LISTAR ITENS DO CATÁLOGO (FALTAVA — agora incluída)
# --------------------------------------------------------
def listar_itens_catalogo():
    con = conectar()
    cur = con.cursor(dictionary=True)

    cur.execute("SELECT * FROM catalogo_itens ORDER BY nome_item ASC")
    dados = cur.fetchall()

    cur.close()
    con.close()
    return dados


# --------------------------------------------------------
# 🔹 8. ATIVAÇÃO MANUAL
# --------------------------------------------------------
def ativar_evento_manual(id_evento):
    return _ativar_evento(id_evento)


# --------------------------------------------------------
# 🔹 9. ATIVAÇÃO AUTOMÁTICA
# --------------------------------------------------------
def ativacao_automatica():
    con = conectar()
    cur = con.cursor(dictionary=True)

    hoje = datetime.now().date()
    alvo = hoje + timedelta(days=2)

    cur.execute("""
        SELECT id_evento FROM eventos
        WHERE status='agendado' AND data_evento = %s
    """, (alvo,))

    eventos = cur.fetchall()

    cur.close()
    con.close()

    for ev in eventos:
        _ativar_evento(ev["id_evento"])


# --------------------------------------------------------
# 🔹 10. FUNÇÃO INTERNA PARA ATIVAR
# --------------------------------------------------------
def _ativar_evento(id_evento):
    con = conectar()
    cur = con.cursor()

    itens = listar_itens_evento(id_evento)

    # verificação de estoque
    for it in itens:
        if not _estoque_disponivel(it["id_item"], it["quantidade_locada"]):
            cur.close()
            con.close()
            return False

    # retira estoque
    for it in itens:
        _retirar_do_estoque(it["id_item"], it["quantidade_locada"])

    cur.execute("UPDATE eventos SET status='ativo' WHERE id_evento=%s", (id_evento,))
    con.commit()

    cur.close()
    con.close()
    return True


# --------------------------------------------------------
# 🔹 11. REGISTRAR DEVOLUÇÃO COM PROTEÇÃO
# --------------------------------------------------------
def registrar_devolucao(id_evento, devolucoes):
    con = conectar()
    cur = con.cursor()

    # Ver status do evento
    evento = buscar_evento(id_evento)
    status_evento = evento.get("status") if evento else None

    for d in devolucoes:
        locado = d["locado"]
        devolvido = d["devolvido"]

        # Nunca registra mais que foi locado
        devolucao_real = min(devolvido, locado)

        cur.execute("""
            UPDATE itens_evento
            SET quantidade_devolvida=%s,
                devolvido=%s,
                quebrado=%s
            WHERE id_evento=%s AND id_item=%s
        """, (
            devolucao_real,
            devolucao_real == locado,          # True se devolveu tudo
            devolucao_real < locado,           # True se ficou faltando (quebrado/perdido)
            id_evento,
            d["id_item"]
        ))

        # ⚠️ Só devolve pro estoque se o evento estava ATIVO
        if status_evento == "ativo" and devolucao_real > 0:
            _devolver_para_estoque(d["id_item"], devolucao_real)

        # Registra item quebrado se devolveu menos que locado
        if devolucao_real < locado:
            cur.execute("""
                INSERT INTO itens_quebrados (id_item, id_evento)
                VALUES (%s, %s)
            """, (d["id_item"], id_evento))

    # Marca evento como concluído
    cur.execute("UPDATE eventos SET status='concluido' WHERE id_evento=%s", (id_evento,))
    con.commit()
    cur.close()
    con.close()


# --------------------------------------------------------
# 🔹 12. ESTOQUE — VERIFICAR / TIRAR / DEVOLVER
# --------------------------------------------------------
def _estoque_disponivel(id_item, qtd):
    con = conectar()
    cur = con.cursor(dictionary=True)

    cur.execute("SELECT quantidade_disponivel FROM catalogo_itens WHERE id_item=%s", (id_item,))
    dado = cur.fetchone()

    cur.close()
    con.close()
    return dado["quantidade_disponivel"] >= qtd


def _retirar_do_estoque(id_item, qtd):
    con = conectar()
    cur = con.cursor()

    cur.execute("""
        UPDATE catalogo_itens
        SET quantidade_disponivel = quantidade_disponivel - %s
        WHERE id_item=%s
    """, (qtd, id_item))

    con.commit()
    cur.close()
    con.close()


def _devolver_para_estoque(id_item, qtd):
    con = conectar()
    cur = con.cursor()

    cur.execute("""
        UPDATE catalogo_itens
        SET quantidade_disponivel = quantidade_disponivel + %s
        WHERE id_item=%s
    """, (qtd, id_item))

    con.commit()
    cur.close()
    con.close()


# --------------------------------------------------------
# 🔹 13. GERAR PDF PROFISSIONAL (IMAGEM RLImage)
# --------------------------------------------------------
def gerar_pdf_evento(id_evento, caminho_pdf):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Table, TableStyle
    from reportlab.platypus import Image as RLImage
    from reportlab.lib import colors
    import io
    from PIL import Image as PILImage

    evento = buscar_evento(id_evento)
    itens = listar_itens_evento(id_evento)

    c = canvas.Canvas(caminho_pdf, pagesize=A4)
    largura, altura = A4

    y = altura - 60

    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, y, f"Relatório do Evento: {evento['nome_evento']}")
    y -= 30

    c.setFont("Helvetica", 12)
    c.drawString(40, y, f"Cliente: {evento['nome_cliente']}")
    y -= 20

    c.drawString(40, y, f"Endereço: {evento['endereco_evento']}")
    y -= 20

    c.drawString(40, y, f"Data: {evento['data_evento']}")
    y -= 30

    data = [["Foto", "Item", "Qtd Locada"]]

    for it in itens:
        img_obj = ""
        img = it["imagem"]

        if isinstance(img, (bytes, bytearray)) and img:
            try:
                im = PILImage.open(io.BytesIO(img))
                im = im.convert("RGB")
                im.thumbnail((90, 90))
                buffer = io.BytesIO()
                im.save(buffer, format="JPEG")
                buffer.seek(0)
                img_obj = RLImage(buffer, width=70, height=70)
            except:
                img_obj = ""

        data.append([img_obj, it["nome_item"], str(it["quantidade_locada"])])

    tabela = Table(data, colWidths=[110, 240, 80])
    tabela.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    tabela.wrapOn(c, 30, y)
    tabela_height = len(data) * 50
    tabela.drawOn(c, 30, y - tabela_height)

    c.showPage()
    c.save()



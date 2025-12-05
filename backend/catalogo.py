# backend/catalogo.py — VERSÃO EVENTPLUS COMPLETA
import os
from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.utils import get_color_from_hex as rgba
from kivymd.app import MDApp

# KIVYMD
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.modalview import ModalView
from kivymd.uix.card import MDCard

# DB
from backend.db_catalogo import listar_categorias, adicionar_categoria, excluir_categoria
from backend.db_itens import listar_itens, adicionar_item, atualizar_item, excluir_item


# FUNÇÕES AUXILIARES -------------------------------------------------------
def load_image_as_blob(path):
    try:
        with open(path, "rb") as f:
            return f.read()
    except:
        return None


def blob_to_texture(blob):
    try:
        import PIL.Image as pil
        import io
        stream = io.BytesIO(blob)
        pil_image = pil.open(stream).convert("RGBA")
        tex = Texture.create(size=pil_image.size)
        tex.blit_buffer(pil_image.tobytes(), colorfmt="rgba", bufferfmt="ubyte")
        tex.flip_vertical()
        return tex
    except:
        return None


# ======================================================================
# TELA DE CATEGORIAS
# ======================================================================
class CatalogoScreen(Screen):
    categorias = ListProperty([])

    def on_pre_enter(self):
        app = MDApp.get_running_app()
        user_id = app.usuario_atual["id_usuario"]

        try:
            dados = listar_categorias(user_id)
        except Exception as e:
            print("Erro ao carregar categorias:", e)
            dados = []

        self.categorias = dados
        self.atualizar_lista()

    # ------------------------------------------------------------------
    def atualizar_lista(self):
        container = self.ids.lista_categorias
        container.clear_widgets()

        for cat in self.categorias:
            btn = MDRaisedButton(
                text=cat["nome_categoria"],
                size_hint_y=None,
                height=50,
                md_bg_color=rgba("#c6c39a"),
                text_color=(0, 0, 0, 1),
                font_name="frontend/telas/fontes/Poppins-SemiBold.ttf",
                elevation=0,
                on_release=lambda inst, c=cat: self.abrir_categoria(c)
            )
            container.add_widget(btn)

    # ------------------------------------------------------------------
    def abrir_categoria(self, categoria_dict):
        tela = self.manager.get_screen("itens_categoria")
        tela.id_categoria = categoria_dict["id_categoria"]
        tela.nome_categoria = categoria_dict["nome_categoria"]
        self.manager.current = "itens_categoria"

    # ------------------------------------------------------------------
    # Popup para adicionar categoria (versão estilizada)
    # ------------------------------------------------------------------
    def popup_adicionar_categoria(self):
        class PopupCategoria(ModalView):
            def __init__(self, salvar_callback, **kwargs):
                super().__init__(**kwargs)
                self.size_hint = (0.9, 0.5)
                self.auto_dismiss = False

                root = MDBoxLayout(
                    orientation="vertical",
                    spacing=16,
                    padding=20,
                    md_bg_color=rgba("#fcf6d2")
                )

                titulo = MDLabel(
                    text="Nova Categoria",
                    halign="center",
                    font_style="H6",
                    theme_text_color="Custom",
                    text_color=rgba("#281f20"),
                    font_name="frontend/telas/fontes/Poppins-SemiBold.ttf"
                )
                root.add_widget(titulo)

                self.input = MDTextField(
                    hint_text="Nome da categoria",
                    mode="rectangle",
                    font_name="frontend/telas/fontes/Inter-Regular.ttf"
                )
                root.add_widget(self.input)

                botoes = MDBoxLayout(size_hint_y=None, height=50, spacing=12)

                btn_cancelar = MDFlatButton(
                    text="Cancelar",
                    theme_text_color="Custom",
                    text_color=rgba("#281f20"),
                    font_name="telas/fontes/Poppins-SemiBold.ttf",
                    on_release=lambda *_: self.dismiss()
                )

                btn_salvar = MDRaisedButton(
                    text="Salvar",
                    md_bg_color=rgba("#281f20"),
                    text_color=(1, 1, 1, 1),
                    font_name="telas/fontes/Poppins-SemiBold.ttf",
                    on_release=lambda *_: salvar_callback(self.input.text)
                )

                botoes.add_widget(btn_cancelar)
                botoes.add_widget(btn_salvar)

                root.add_widget(botoes)
                self.add_widget(root)

        def salvar_categoria(nome_cat):
            app = MDApp.get_running_app()
            user_id = app.usuario_atual["id_usuario"]

            n = (nome_cat or "").strip()
            if not n:
                return

            adicionar_categoria(n, user_id)
            popup.dismiss()
            self.on_pre_enter()

        popup = PopupCategoria(salvar_callback=salvar_categoria)
        popup.open()


# ======================================================================
# TELA DE ITENS DA CATEGORIA
# ======================================================================
class ItensCategoriaScreen(Screen):
    id_categoria = NumericProperty(0)
    nome_categoria = StringProperty("")
    itens = ListProperty([])

    # ------------------------------------------------------------------
    def on_pre_enter(self):
        self.carregar_itens()

    # ------------------------------------------------------------------
    def carregar_itens(self):
        app = MDApp.get_running_app()
        user_id = app.usuario_atual["id_usuario"]

        try:
            dados = listar_itens(self.id_categoria, user_id)
        except:
            dados = []

        self.itens = dados
        container = self.ids.lista_itens
        container.clear_widgets()

        for item in dados:

            card = MDCard(
                orientation="horizontal",
                padding=12,
                spacing=15,
                size_hint_y=None,
                height=110,
                md_bg_color=rgba("#fcf6d2"),
                radius=[18, 18, 18, 18]
            )

            # imagem
            if item["imagem"]:
                tex = blob_to_texture(item["imagem"])
                img = Image(texture=tex, size_hint_x=None, width=70)
            else:
                img = MDLabel(
                    text="SEM\nIMAGEM",
                    halign="center",
                    size_hint_x=None,
                    width=70,
                    theme_text_color="Custom",
                    text_color=rgba("#281f20")
                )

            card.add_widget(img)

            # informações
            col = MDBoxLayout(orientation="vertical", spacing=4)

            nome = item["nome_item"]
            abv = item.get("abreviacao") or ""

            col.add_widget(MDLabel(
                text=f"{nome} ({abv})" if abv else nome,
                font_style="Subtitle1",
                theme_text_color="Custom",
                text_color=rgba("#281f20"),
                    font_name="frontend/telas/fontes/Poppins-SemiBold.ttf"
            ))

            col.add_widget(MDLabel(
                text=f"Total: {item['quantidade_total']}   Disponível: {item['quantidade_disponivel']}",
                theme_text_color="Custom",
                text_color=rgba("#281f20"),
                    font_name="frontend/telas/fontes/Inter-Regular.ttf",
                font_size="12sp"
            ))

            card.add_widget(col)

            # Botões Editar / Excluir
            btns = MDBoxLayout(
                orientation="vertical",
                size_hint_x=None,
                width=120,
                spacing=8
            )

            btn_editar = MDRaisedButton(
                text="Editar",
                md_bg_color=rgba("#c6c39a"),
                text_color=(0, 0, 0, 1),
                font_name="telas/fontes/Poppins-SemiBold.ttf",
                elevation=0,
                on_release=lambda inst, i=item: self.popup_editar(i)
            )

            btn_excluir = MDFlatButton(
                text="Excluir",
                theme_text_color="Custom",
                text_color=rgba("#281f20"),
                font_name="telas/fontes/Poppins-SemiBold.ttf",
                on_release=lambda inst, i=item: self.excluir(i["id_item"])
            )

            btns.add_widget(btn_editar)
            btns.add_widget(btn_excluir)
            card.add_widget(btns)

            container.add_widget(card)

    # ------------------------------------------------------------------
    def excluir(self, item_id):
        app = MDApp.get_running_app()
        user_id = app.usuario_atual["id_usuario"]

        try:
            excluir_item(item_id, user_id)
            self.carregar_itens()
        except Exception as e:
            print("Erro:", e)

    # ------------------------------------------------------------------
    def popup_adicionar(self):
        self._popup_item(edit_mode=False)

    # ------------------------------------------------------------------
    def popup_editar(self, item):
        self._popup_item(edit_mode=True, item=item)

    # ------------------------------------------------------------------
    # POPUP EVENTPLUS DE ADICIONAR / EDITAR ITEM
    # ------------------------------------------------------------------
    def _popup_item(self, edit_mode=False, item=None):
        popup = ModalView(size_hint=(0.92, 0.78), auto_dismiss=False)

        root = MDBoxLayout(
            orientation="vertical",
            spacing=14,
            padding=20,
            md_bg_color=rgba("#fcf6d2")
        )

        titulo = MDLabel(
            text="Editar item" if edit_mode else "Novo item",
            halign="center",
            font_style="H6",
            theme_text_color="Custom",
            text_color=rgba("#281f20"),
                    font_name="frontend/telas/fontes/Poppins-SemiBold.ttf"
        )
        root.add_widget(titulo)

        nome_val = item["nome_item"] if edit_mode else ""
        abv_val = item.get("abreviacao") if edit_mode else ""
        qtd_total_val = str(item["quantidade_total"]) if edit_mode else ""
        qtd_disp_val = str(item["quantidade_disponivel"]) if edit_mode else ""

        nome = MDTextField(
            text=nome_val,
            hint_text="Nome",
            mode="rectangle",
                    font_name="frontend/telas/fontes/Inter-Regular.ttf"
        )

        abv = MDTextField(
            text=abv_val,
            hint_text="Abreviação",
            mode="rectangle",
            font_name="telas/fontes/Inter-Regular.ttf"
        )

        qtd_total = MDTextField(
            text=qtd_total_val,
            hint_text="Quantidade total",
            mode="rectangle",
            input_filter="int",
            font_name="telas/fontes/Inter-Regular.ttf"
        )

        qtd_disp = MDTextField(
            text=qtd_disp_val,
            hint_text="Disponível",
            mode="rectangle",
            input_filter="int",
            font_name="telas/fontes/Inter-Regular.ttf"
        )

        root.add_widget(nome)
        root.add_widget(abv)
        root.add_widget(qtd_total)
        root.add_widget(qtd_disp)

        # Imagem
        lbl_img = MDLabel(
            text="Nenhuma imagem selecionada",
            halign="center",
            theme_text_color="Custom",
            text_color=rgba("#281f20"),
            font_name="telas/fontes/Inter-Regular.ttf"
        )
        root.add_widget(lbl_img)

        btn_img = MDRaisedButton(
            text="Escolher imagem",
            md_bg_color=rgba("#c6c39a"),
            text_color=(0, 0, 0, 1),
            elevation=0
        )
        root.add_widget(btn_img)

        # Armazena imagem escolhida
        selected = {"blob": None}

        def escolher_imagem(*_):
            from plyer import filechooser
            res = filechooser.open_file()
            if res:
                selected["blob"] = load_image_as_blob(res[0])
                lbl_img.text = os.path.basename(res[0])

        btn_img.bind(on_release=escolher_imagem)

        # BOTÕES INFERIORES
        botoes = MDBoxLayout(size_hint_y=None, height=50, spacing=10)

        btn_cancelar = MDFlatButton(
            text="Cancelar",
            theme_text_color="Custom",
            text_color=rgba("#281f20"),
                font_name="frontend/telas/fontes/Poppins-SemiBold.ttf",
            on_release=lambda *_: popup.dismiss()
        )

        btn_salvar = MDRaisedButton(
            text="Salvar",
            md_bg_color=rgba("#281f20"),
            text_color=(1, 1, 1, 1),
            font_name="telas/fontes/Poppins-SemiBold.ttf"
        )

        botoes.add_widget(btn_cancelar)
        botoes.add_widget(btn_salvar)
        root.add_widget(botoes)

        popup.add_widget(root)

        # ---------- SALVAR ----------
        def salvar(*_):
            app = MDApp.get_running_app()
            user_id = app.usuario_atual["id_usuario"]

            nome_txt = nome.text.strip()
            abv_txt = abv.text.strip()
            qt = int(qtd_total.text or "0")
            qd = int(qtd_disp.text or "0")

            img = selected["blob"] if selected["blob"] else (item["imagem"] if edit_mode else None)

            if edit_mode:
                atualizar_item(item["id_item"], nome_txt, abv_txt, qt, qd, img, user_id)
            else:
                adicionar_item(self.id_categoria, nome_txt, abv_txt, qt, img, user_id)

            popup.dismiss()
            self.carregar_itens()

        btn_salvar.bind(on_release=salvar)
        popup.open()


    # ------------------------------------------------------------------
    def voltar(self):
        self.manager.current = "catalogo"



# 🚀 Sistema do Ateliê - Resumo da Migração para API

## ✅ O que foi feito:

### 📦 Novos Arquivos Criados:
1. **backend/config.py** - Configuração da URL da API
2. **backend/api_client.py** - Cliente HTTP reutilizável
3. **api/requirements.txt** - Dependências da API
4. **docs/DEPLOY_API.md** - Guia completo de deploy

### 🔄 Arquivos Modificados:
1. **backend/usuarios.py** - Login e cadastro via API
2. **backend/db_catalogo.py** - Categorias via API
3. **backend/db_itens.py** - Itens via API
4. **backend/db_eventos.py** - Eventos via API
5. **buildozer.spec** - Removido mysql, adicionado requests

### 📁 Backups Criados:
- **backend/db_eventos_old.py** - Versão antiga (MySQL direto)

## 🎯 Como Usar:

### 1️⃣ Desenvolvimento Local:

```bash
# Terminal 1 - API
cd api/
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - App Kivy
cd ..
python frontend/main.py
```

### 2️⃣ Produção (APK):

```bash
# 1. Fazer deploy da API (ver docs/DEPLOY_API.md)
# 2. Atualizar backend/config.py com URL da API
# 3. Gerar APK
buildozer -v android debug
```

## 📱 Configuração da API:

**Para desenvolvimento (rede local):**
```python
# backend/config.py
API_BASE_URL = "http://192.168.1.9:8000"
```

**Para produção (servidor online):**
```python
# backend/config.py
API_BASE_URL = "https://sua-api.railway.app"
```

## 🔧 Endpoints Implementados na API:

### Usuários:
- `POST /usuarios` - Cadastrar usuário
- `POST /auth/login` - Login

### Categorias:
- `GET /categorias` - Listar categorias
- `POST /categorias` - Criar categoria
- `DELETE /categorias/{id}` - Excluir categoria

### Itens:
- `GET /categorias/{id}/itens` - Listar itens
- `POST /categorias/{id}/itens` - Criar item
- `PUT /itens/{id}` - Atualizar item
- `DELETE /itens/{id}` - Excluir item

### Eventos:
- `GET /eventos` - Listar eventos
- `POST /eventos` - Criar evento
- `GET /eventos/{id}` - Buscar evento
- `PUT /eventos/{id}` - Atualizar evento
- `DELETE /eventos/{id}` - Cancelar evento
- `POST /eventos/{id}/ativar` - Ativar evento
- `POST /eventos/{id}/concluir` - Concluir evento
- `GET /eventos/{id}/itens` - Listar itens do evento
- `POST /eventos/{id}/itens` - Adicionar item ao evento
- `PUT /eventos/{id}/itens/{id_item}` - Atualizar item do evento

## ⚠️ Funcionalidades Pendentes:

### Na API (precisam ser implementadas):
- [ ] Recuperação de senha por email
- [ ] Verificação de código de recuperação
- [ ] Geração de PDF dos eventos
- [ ] Autenticação JWT (opcional)
- [ ] Upload de imagens

### No App:
- [ ] Adaptar recuperação de senha (quando API estiver pronta)
- [ ] Tratamento melhor de erros de conexão
- [ ] Cache local (offline mode)

## 🐛 Troubleshooting:

**Erro "Não foi possível conectar ao servidor":**
- Verifique se a API está rodando
- Confirme a URL em `backend/config.py`
- Teste a URL no navegador

**Erro de CORS:**
- A API já tem CORS configurado
- Verifique se o middleware está ativo em `api/app.py`

**Erro no buildozer:**
```bash
# Limpar cache
buildozer android clean

# Tentar novamente
buildozer -v android debug
```

## 📊 Estrutura do Projeto:

```
sistemadoatelie/
├── api/                        # Backend API (FastAPI)
│   ├── app.py                 # API principal
│   ├── database.py            # Conexão DB
│   └── requirements.txt       # Dependências
│
├── backend/                   # Lógica do app mobile
│   ├── config.py             # Config da API ⭐
│   ├── api_client.py         # Cliente HTTP ⭐
│   ├── usuarios.py           # Login/cadastro ⭐
│   ├── db_catalogo.py        # Categorias ⭐
│   ├── db_itens.py           # Itens ⭐
│   ├── db_eventos.py         # Eventos ⭐
│   └── db_eventos_old.py     # Backup (MySQL)
│
├── frontend/                  # Interface Kivy
│   ├── main.py               # App principal
│   └── telas/                # Arquivos .kv
│
├── docs/
│   └── DEPLOY_API.md         # Guia de deploy ⭐
│
└── buildozer.spec            # Config do APK ⭐

⭐ = Arquivos modificados/criados nesta migração
```

## 🎉 Pronto para usar!

O sistema agora está preparado para funcionar como APK mobile, se comunicando com uma API hospedada em servidor.

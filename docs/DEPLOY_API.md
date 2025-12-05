# 🚀 Guia de Deploy da API

## 📋 Pré-requisitos

- Python 3.8+
- MySQL instalado e configurado
- Conta em um serviço de hospedagem (Railway, Render, Heroku, etc.)

## 🔧 Configuração Local

### 1. Instalar dependências da API

```bash
cd api/
pip install fastapi uvicorn mysql-connector-python sqlalchemy
```

### 2. Testar localmente

```bash
# Na pasta api/
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

A API estará disponível em: `http://192.168.1.9:8000`

## ☁️ Deploy em Produção

### Opção 1: Railway (Recomendado)

1. **Criar conta no Railway**: https://railway.app/
2. **Criar arquivo `requirements.txt`** na pasta `api/`:
   ```
   fastapi
   uvicorn[standard]
   mysql-connector-python
   sqlalchemy
   ```

3. **Criar arquivo `Procfile`** na pasta `api/`:
   ```
   web: uvicorn app:app --host 0.0.0.0 --port $PORT
   ```

4. **Fazer deploy**:
   - Conecte seu repositório GitHub
   - Railway detecta automaticamente o Python
   - Configure as variáveis de ambiente:
     - `API_URL` (URL pública da sua API)
     - Credenciais do MySQL (se usar MySQL do Railway)

5. **Configurar banco de dados**:
   - Adicione MySQL no Railway
   - Copie as credenciais de conexão
   - Atualize `database.py` com as novas credenciais

### Opção 2: Render

1. **Criar conta**: https://render.com/
2. **Criar Web Service**:
   - Conectar repositório
   - Escolher Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

3. **Adicionar PostgreSQL/MySQL**:
   - Criar banco de dados
   - Conectar ao serviço

## 📱 Configurar App Mobile

Após o deploy, atualize a URL da API no app:

### No arquivo `backend/config.py`:

```python
# Para desenvolvimento local (testando no computador)
API_BASE_URL = "http://192.168.1.9:8000"

# Para produção (testando no celular)
API_BASE_URL = "https://sua-api.railway.app"  # ou Render, Heroku, etc.
```

### Ou usando variável de ambiente:

No buildozer.spec, adicione:
```
android.env_vars = API_URL=https://sua-api.railway.app
```

## 🔒 Segurança

### Adicionar CORS na API (`api/app.py`):

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Adicionar autenticação JWT (opcional):

```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

## 🧪 Testar a API

### Localmente:
```bash
curl http://192.168.1.9:8000/categorias
```

### Em produção:
```bash
curl https://sua-api.railway.app/categorias
```

## 📊 Monitoramento

- **Railway**: Console integrado com logs
- **Render**: Logs em tempo real no dashboard
- **Heroku**: `heroku logs --tail`

## 🐛 Troubleshooting

### Erro de conexão no celular:
- Verifique se a API está rodando
- Confirme a URL em `backend/config.py`
- Teste a URL no navegador do celular

### Erro de banco de dados:
- Verifique credenciais em `api/database.py`
- Confirme que o banco está acessível publicamente
- Teste conexão com MySQL Workbench

### Erro de CORS:
- Adicione o middleware CORS na API
- Verifique os `allow_origins`

## 📝 Checklist Deploy

- [ ] API rodando localmente
- [ ] requirements.txt criado
- [ ] Deploy feito no Railway/Render
- [ ] Banco de dados configurado
- [ ] URL da API atualizada no app
- [ ] Testado cadastro/login pelo celular
- [ ] APK gerado com buildozer

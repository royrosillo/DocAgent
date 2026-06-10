# DocAgent 🤖📝

Agente IA que documenta tu código automáticamente. Detecta funciones sin docstring, genera documentación con Claude y abre un PR.

## Arranque rápido

### 1. Clonar e instalar dependencias

```bash
cd docagent
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Edita .env con tu ANTHROPIC_API_KEY y GITHUB_TOKEN
```

**ANTHROPIC_API_KEY** → https://console.anthropic.com/  
**GITHUB_TOKEN** → GitHub → Settings → Developer settings → Personal access tokens  
  Permisos necesarios: `repo`, `pull_requests`

### 3. Levantar el servidor

```bash
uvicorn app.main:app --reload --port 8000
```

El servidor corre en http://localhost:8000  
Documentación interactiva en http://localhost:8000/docs

---

## Probar sin webhook (modo desarrollo)

Puedes probar la generación directamente desde el navegador en `/docs`:

```bash
POST /docs-api/generate
{
  "content": "def sumar(a, b):\n    return a + b",
  "file_path": "utils.py"
}
```

---

## Configurar el webhook en GitHub

Para que el agente reaccione a pushes reales necesitas exponer tu servidor local a internet. Usa **ngrok**:

```bash
# Instalar ngrok → https://ngrok.com/download
ngrok http 8000
```

Copia la URL que te da (ej: `https://abc123.ngrok.io`) y configura el webhook:

1. Ve a tu repo en GitHub → **Settings → Webhooks → Add webhook**
2. Payload URL: `https://abc123.ngrok.io/webhooks/github`
3. Content type: `application/json`
4. Secret: el mismo que pusiste en `.env`
5. Events: selecciona **Just the push event**
6. Guardar

Ahora cada vez que hagas push, el agente analizará los archivos modificados y abrirá un PR con la documentación.

---

## Estructura del proyecto

```
docagent/
├── app/
│   ├── main.py              # Entry point FastAPI
│   ├── api/
│   │   ├── webhook.py       # Recibe eventos de GitHub
│   │   └── docs.py          # Endpoints manuales
│   ├── services/
│   │   ├── parser_service.py  # Extrae funciones con tree-sitter
│   │   ├── doc_service.py     # Genera docs con Claude
│   │   └── github_service.py  # Interactúa con GitHub API
│   └── core/
│       └── config.py          # Variables de entorno
└── requirements.txt
```

## Roadmap

- [ ] Soporte para GitLab y Bitbucket
- [ ] Dashboard Angular con cobertura por repo
- [ ] Búsqueda semántica sobre la documentación (pgvector)
- [ ] Slack bot: "¿qué hace la función X?"
- [ ] VS Code extension

import hmac
import hashlib
import httpx
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Header
from app.core.config import settings
from app.services.github_service import GitHubService
from app.services.parser_service import ParserService
from app.services.doc_service import DocService

router = APIRouter()


def verify_github_signature(payload: bytes, signature: str) -> bool:
    """Verifica que el webhook realmente viene de GitHub."""
    if not signature or not signature.startswith("sha256="):
        return False
    expected = hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


async def process_push_event(payload: dict):
    """
    Flujo principal:
    1. Obtener los archivos modificados del commit
    2. Parsear funciones/clases cambiadas
    3. Generar documentación con IA
    4. Crear un PR con los cambios
    """
    github = GitHubService()
    parser = ParserService()
    doc_service = DocService()

    repo_full_name = payload["repository"]["full_name"]
    commits = payload.get("commits", [])
    ref = payload.get("ref", "")
    branch = ref.replace("refs/heads/", "")

    print(f"[Webhook] Push recibido: {repo_full_name} @ {branch}")

    # Recopilar todos los archivos Python/JS modificados o añadidos
    modified_files: list[str] = []
    for commit in commits:
        for f in commit.get("modified", []) + commit.get("added", []):
            if f.endswith((".py", ".js", ".ts")) and f not in modified_files:
                modified_files.append(f)

    if not modified_files:
        print("[Webhook] No hay archivos relevantes modificados.")
        return

    print(f"[Webhook] Archivos a documentar: {modified_files}")

    # Procesar cada archivo
    doc_changes: dict[str, str] = {}
    for file_path in modified_files:
        # 1. Obtener contenido del archivo desde GitHub
        content = await github.get_file_content(repo_full_name, file_path, branch)
        if not content:
            continue

        # 2. Parsear y extraer funciones sin docstring o con docstring desactualizado
        functions = parser.extract_undocumented(content, file_path)
        if not functions:
            continue

        # 3. Generar documentación con Claude
        updated_content = await doc_service.generate_docs(content, functions, file_path)
        if updated_content and updated_content != content:
            doc_changes[file_path] = updated_content

    if not doc_changes:
        print("[Webhook] Todo ya está documentado correctamente.")
        return

    # 4. Crear PR con los cambios
    pr_url = await github.create_docs_pr(repo_full_name, branch, doc_changes)
    print(f"[Webhook] PR creado: {pr_url}")


@router.post("/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None),
):
    payload_bytes = await request.body()

    # Verificar firma (omitir en desarrollo local)
    if settings.GITHUB_WEBHOOK_SECRET:
        if not verify_github_signature(payload_bytes, x_hub_signature_256 or ""):
            raise HTTPException(status_code=401, detail="Firma inválida")

    payload = await request.json()

    if x_github_event == "push":
        # Procesar en background para responder a GitHub rápido
        background_tasks.add_task(process_push_event, payload)
        return {"status": "processing"}

    return {"status": "ignored", "event": x_github_event}

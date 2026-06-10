import base64
import httpx
from app.core.config import settings


class GitHubService:
    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_file_content(self, repo: str, path: str, ref: str) -> str | None:
        """Obtiene el contenido de un archivo del repositorio."""
        url = f"{self.BASE_URL}/repos/{repo}/contents/{path}?ref={ref}"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self.headers)
            if r.status_code != 200:
                print(f"[GitHub] No se pudo obtener {path}: {r.status_code}")
                return None
            data = r.json()
            return base64.b64decode(data["content"]).decode("utf-8")

    async def get_file_sha(self, repo: str, path: str, ref: str) -> str | None:
        """Obtiene el SHA del archivo (necesario para actualizarlo via API)."""
        url = f"{self.BASE_URL}/repos/{repo}/contents/{path}?ref={ref}"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self.headers)
            if r.status_code != 200:
                return None
            return r.json().get("sha")

    async def create_docs_pr(
        self,
        repo: str,
        base_branch: str,
        doc_changes: dict[str, str],
    ) -> str:
        """
        Crea una nueva rama, sube los archivos modificados y abre un PR.
        Devuelve la URL del PR creado.
        """
        # 1. Obtener SHA del branch base
        base_sha = await self._get_branch_sha(repo, base_branch)
        if not base_sha:
            raise ValueError(f"No se encontró el branch: {base_branch}")

        # 2. Crear rama nueva: docs/auto-TIMESTAMP
        import time
        new_branch = f"docs/auto-{int(time.time())}"
        await self._create_branch(repo, new_branch, base_sha)

        # 3. Subir cada archivo modificado
        for file_path, new_content in doc_changes.items():
            file_sha = await self.get_file_sha(repo, file_path, base_branch)
            await self._update_file(repo, file_path, new_content, new_branch, file_sha)

        # 4. Abrir el PR
        pr_url = await self._create_pr(repo, new_branch, base_branch, list(doc_changes.keys()))
        return pr_url

    async def _get_branch_sha(self, repo: str, branch: str) -> str | None:
        url = f"{self.BASE_URL}/repos/{repo}/git/ref/heads/{branch}"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=self.headers)
            if r.status_code != 200:
                return None
            return r.json()["object"]["sha"]

    async def _create_branch(self, repo: str, branch: str, sha: str):
        url = f"{self.BASE_URL}/repos/{repo}/git/refs"
        async with httpx.AsyncClient() as client:
            await client.post(url, headers=self.headers, json={
                "ref": f"refs/heads/{branch}",
                "sha": sha,
            })

    async def _update_file(
        self,
        repo: str,
        path: str,
        content: str,
        branch: str,
        sha: str | None,
    ):
        url = f"{self.BASE_URL}/repos/{repo}/contents/{path}"
        payload = {
            "message": f"docs: auto-generate documentation for {path}",
            "content": base64.b64encode(content.encode()).decode(),
            "branch": branch,
        }
        if sha:
            payload["sha"] = sha
        async with httpx.AsyncClient() as client:
            await client.put(url, headers=self.headers, json=payload)

    async def _create_pr(
        self,
        repo: str,
        head: str,
        base: str,
        files: list[str],
    ) -> str:
        url = f"{self.BASE_URL}/repos/{repo}/pulls"
        files_str = "\n".join(f"- `{f}`" for f in files)
        body = f"""## 📝 Documentación auto-generada

Este PR fue creado automáticamente por **DocAgent**.

### Archivos documentados:
{files_str}

### Qué se hizo:
- Se detectaron funciones y clases sin docstring
- Se generaron docstrings con contexto real del código usando IA
- No se modificó ninguna lógica de negocio

> Revisa, ajusta si es necesario y haz merge 🚀
"""
        async with httpx.AsyncClient() as client:
            r = await client.post(url, headers=self.headers, json={
                "title": "docs: auto-generated documentation",
                "body": body,
                "head": head,
                "base": base,
            })
            return r.json().get("html_url", "PR creado")

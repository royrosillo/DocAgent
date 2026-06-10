from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.parser_service import ParserService
from app.services.doc_service import DocService

router = APIRouter()


class GenerateRequest(BaseModel):
    content: str
    file_path: str


class GenerateResponse(BaseModel):
    original_content: str
    documented_content: str
    functions_found: int
    file_path: str


@router.post("/generate", response_model=GenerateResponse)
async def generate_documentation(req: GenerateRequest):
    """
    Endpoint para probar la generación de docs sin necesitar un webhook.
    Útil durante desarrollo y para el dashboard de la app.
    """
    parser = ParserService()
    doc_service = DocService()

    functions = parser.extract_undocumented(req.content, req.file_path)

    if not functions:
        return GenerateResponse(
            original_content=req.content,
            documented_content=req.content,
            functions_found=0,
            file_path=req.file_path,
        )

    documented = await doc_service.generate_docs(req.content, functions, req.file_path)

    return GenerateResponse(
        original_content=req.content,
        documented_content=documented,
        functions_found=len(functions),
        file_path=req.file_path,
    )


@router.get("/coverage")
async def get_coverage(content: str, file_path: str):
    """
    Calcula el porcentaje de funciones documentadas en un archivo.
    """
    parser = ParserService()

    # Obtener todas las funciones
    undocumented = parser.extract_undocumented(content, file_path)

    # Contar total de funciones (documentadas + no documentadas)
    import re
    if file_path.endswith(".py"):
        total = len(re.findall(r'^\s*(?:def|class)\s+\w+', content, re.MULTILINE))
    else:
        total = len(re.findall(r'function\s+\w+|const\s+\w+\s*=\s*(?:async\s+)?\(', content))

    if total == 0:
        return {"coverage": 100, "total": 0, "undocumented": 0}

    documented_count = total - len(undocumented)
    coverage = round((documented_count / total) * 100, 1)

    return {
        "coverage": coverage,
        "total": total,
        "documented": documented_count,
        "undocumented": len(undocumented),
        "undocumented_functions": [f.name for f in undocumented],
    }

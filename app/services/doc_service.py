import anthropic
from app.core.config import settings
from app.services.parser_service import FunctionInfo


class DocService:
    """Genera documentación usando Claude."""

    def __init__(self):
        """Inicializa el servicio de documentación.
        
        Crea una instancia del cliente de Anthropic usando la clave API
        configurada en las variables de entorno.
        """
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def generate_docs(
        self,
        file_content: str,
        functions: list[FunctionInfo],
        file_path: str,
    ) -> str:
        """
        Recibe el contenido completo del archivo y la lista de funciones
        sin documentar. Devuelve el archivo con docstrings insertados.
        """
        if not functions:
            return file_content

        language = functions[0].language
        func_list = self._format_functions_for_prompt(functions)

        prompt = f"""Eres un experto en documentación de código. 
Recibirás un archivo de código y una lista de funciones que necesitan documentación.

ARCHIVO: {file_path}
LENGUAJE: {language}

FUNCIONES SIN DOCUMENTAR:
{func_list}

CONTENIDO COMPLETO DEL ARCHIVO:
```{language}
{file_content}
```

Tu tarea:
1. Añade docstrings a TODAS las funciones listadas arriba
2. Para Python: usa el formato Google Style (Args:, Returns:, Raises:)
3. Para JS/TS: usa el formato JSDoc (/** @param @returns */)
4. Sé conciso pero completo. Explica QUÉ hace la función y por QUÉ existe, no cómo
5. Infiere los tipos de los parámetros del código
6. NO modifiques nada más del archivo, solo añade los docstrings

Devuelve ÚNICAMENTE el archivo completo con los docstrings añadidos, sin explicaciones, sin markdown."""

        message = self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        result = message.content[0].text.strip()

        # Limpiar si Claude envuelve en código markdown
        if result.startswith("```"):
            lines = result.splitlines()
            result = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])

        return result

    def _format_functions_for_prompt(self, functions: list[FunctionInfo]) -> str:
        """Formatea la lista de funciones para incluir en el prompt de Claude.
        
        Convierte los objetos FunctionInfo en un formato legible que incluye
        el nombre, número de línea y firma de cada función.
        
        Args:
            functions: Lista de funciones a documentar.
            
        Returns:
            Cadena con las funciones formateadas, una por línea.
        """
        lines = []
        for f in functions:
            lines.append(f"- {f.name} (línea {f.start_line + 1}): {f.signature}")
        return "\n".join(lines)
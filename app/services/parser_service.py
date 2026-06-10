import re
from dataclasses import dataclass


@dataclass
class FunctionInfo:
    """Contenedor de información sobre una función o clase sin documentar.
    
    Almacena metadatos de funciones/clases detectadas en código fuente,
    incluyendo su ubicación, firma y si posee documentación.
    
    Attributes:
        name: Nombre de la función o clase.
        signature: Firma completa de la declaración.
        body_preview: Primeras líneas del cuerpo para dar contexto a la IA.
        start_line: Número de línea donde comienza la definición.
        end_line: Número de línea estimado donde termina.
        has_docstring: Indica si la función ya tiene documentación.
        language: Lenguaje de programación del archivo.
    """
    name: str
    signature: str
    body_preview: str  # Primeras líneas del cuerpo para dar contexto a la IA
    start_line: int
    end_line: int
    has_docstring: bool
    language: str


class ParserService:
    """
    Extrae funciones y clases de archivos de código.
    Usa tree-sitter cuando está disponible; si no, fallback a regex.
    """

    def extract_undocumented(self, content: str, file_path: str) -> list[FunctionInfo]:
        """Extrae funciones y clases sin documentar de un archivo de código.
        
        Detecta el lenguaje del archivo y aplica el extractor apropiado
        para identificar funciones/clases que carecen de documentación.
        
        Args:
            content: Contenido completo del archivo a analizar.
            file_path: Ruta del archivo (usada para detectar el lenguaje).
        
        Returns:
            Lista de FunctionInfo con las funciones sin documentar encontradas.
        """
        language = self._detect_language(file_path)
        if language == "python":
            return self._extract_python(content)
        elif language in ("javascript", "typescript"):
            return self._extract_js(content)
        return []

    def _detect_language(self, file_path: str) -> str:
        """Detecta el lenguaje de programación basándose en la extensión del archivo.
        
        Args:
            file_path: Ruta del archivo cuyo lenguaje se desea detectar.
        
        Returns:
            String indicando el lenguaje ('python', 'javascript', 'typescript' o 'unknown').
        """
        if file_path.endswith(".py"):
            return "python"
        elif file_path.endswith(".ts"):
            return "typescript"
        elif file_path.endswith(".js"):
            return "javascript"
        return "unknown"

    def _extract_python(self, content: str, file_path: str = "") -> list[FunctionInfo]:
        """Extrae funciones y clases Python sin documentación.
        
        Utiliza expresiones regulares como fallback cuando tree-sitter
        no está disponible para analizar archivos Python.
        
        Args:
            content: Contenido del archivo Python a analizar.
            file_path: Ruta del archivo (parámetro reservado para extensibilidad).
        
        Returns:
            Lista de FunctionInfo con funciones/clases Python sin docstring.
        """
        return self._extract_python_regex(content)

    def _extract_python_regex(self, content: str) -> list[FunctionInfo]:
        """Fallback regex si tree-sitter no está disponible."""
        functions = []
        lines = content.splitlines()
        pattern = re.compile(r'^(\s*)(def|class)\s+(\w+)\s*[\(:]')

        for i, line in enumerate(lines):
            m = pattern.match(line)
            if not m:
                continue

            name = m.group(3)
            # Verificar si la siguiente línea no vacía es un docstring
            has_docstring = False
            for j in range(i + 1, min(i + 4, len(lines))):
                stripped = lines[j].strip()
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    has_docstring = True
                    break
                elif stripped:
                    break

            if not has_docstring:
                body_preview = "\n".join(lines[i + 1 : min(i + 9, len(lines))])
                functions.append(FunctionInfo(
                    name=name,
                    signature=line.strip(),
                    body_preview=body_preview,
                    start_line=i,
                    end_line=min(i + 20, len(lines)),
                    has_docstring=False,
                    language="python",
                ))

        return functions

    def _extract_js(self, content: str) -> list[FunctionInfo]:
        """Extrae funciones JS/TS sin JSDoc."""
        functions = []
        lines = content.splitlines()
        pattern = re.compile(
            r'^\s*(export\s+)?(async\s+)?function\s+(\w+)|'
            r'^\s*(?:const|let)\s+(\w+)\s*=\s*(?:async\s+)?\('
        )

        for i, line in enumerate(lines):
            m = pattern.match(line)
            if not m:
                continue

            name = m.group(3) or m.group(4) or "anonymous"
            # Verificar si la línea anterior tiene JSDoc
            has_jsdoc = i > 0 and lines[i - 1].strip().startswith("*/")

            if not has_jsdoc:
                body_preview = "\n".join(lines[i + 1 : min(i + 9, len(lines))])
                functions.append(FunctionInfo(
                    name=name,
                    signature=line.strip(),
                    body_preview=body_preview,
                    start_line=i,
                    end_line=min(i + 20, len(lines)),
                    has_docstring=False,
                    language="javascript",
                ))

        return functions
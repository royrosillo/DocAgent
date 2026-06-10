import re
from dataclasses import dataclass


@dataclass
class FunctionInfo:
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
        language = self._detect_language(file_path)
        if language == "python":
            return self._extract_python(content)
        elif language in ("javascript", "typescript"):
            return self._extract_js(content)
        return []

    def _detect_language(self, file_path: str) -> str:
        if file_path.endswith(".py"):
            return "python"
        elif file_path.endswith(".ts"):
            return "typescript"
        elif file_path.endswith(".js"):
            return "javascript"
        return "unknown"

    def _extract_python(self, content: str, file_path: str = "") -> list[FunctionInfo]:
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

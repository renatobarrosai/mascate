"""Parser e Chunking de documentos para o RAG.

Transforma arquivos Markdown em chunks semanticos enriquecidos com metadados.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Um pedaco de informacao indexavel."""

    content: str
    source_file: str
    section: str = "root"
    chunk_id: str = field(default="")  # Gera hash se vazio
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Gera ID unico baseado no conteudo se nao fornecido."""
        if not self.chunk_id:
            import hashlib

            # Hash do conteudo + source para garantir unicidade
            unique_str = f"{self.source_file}:{self.section}:{self.content}"
            self.chunk_id = hashlib.md5(unique_str.encode()).hexdigest()


class MarkdownParser:
    """Parser especializado em Markdown para RAG."""

    def __init__(self, chunk_size: int = 512, overlap: int = 50) -> None:
        """Inicializa o parser.

        Args:
            chunk_size: Tamanho maximo aproximado do chunk (em caracteres).
            overlap: Sobreposicao entre chunks para manter contexto.
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def parse_file(self, file_path: Path) -> list[Chunk]:
        """Lê um arquivo Markdown e retorna chunks.

        Args:
            file_path: Caminho do arquivo.

        Returns:
            Lista de objetos Chunk.
        """
        if not file_path.exists():
            logger.error("Arquivo nao encontrado: %s", file_path)
            return []

        try:
            content = file_path.read_text(encoding="utf-8")
            return self._process_content(content, file_path.name)
        except Exception as e:
            logger.error("Erro ao ler arquivo %s: %s", file_path, e)
            return []

    def _process_content(self, content: str, source_name: str) -> list[Chunk]:
        """Processa o conteudo bruto e divide em secoes/chunks."""
        chunks: list[Chunk] = []

        # Divide por headers (h1, h2, h3)
        # Regex captura (espacos opcionais)(# Header) e o conteudo seguinte
        header_pattern = re.compile(r"^\s*(#{1,3})\s+(.*)")

        lines = content.splitlines()
        current_section = "Introduction"
        current_buffer: list[str] = []

        for line in lines:
            match = header_pattern.match(line)
            if match:
                # Se temos conteudo acumulado, processamos
                if current_buffer:
                    section_text = "\n".join(current_buffer).strip()
                    if section_text:
                        chunks.extend(
                            self._create_chunks(
                                section_text, source_name, current_section
                            )
                        )
                    current_buffer = []

                # Atualiza secao atual
                # match.group(2) é o titulo do header
                current_section = match.group(2).strip()
            else:
                current_buffer.append(line)

        # Processa o ultimo buffer
        if current_buffer:
            section_text = "\n".join(current_buffer).strip()
            if section_text:
                chunks.extend(
                    self._create_chunks(section_text, source_name, current_section)
                )

        return chunks

    def _create_chunks(self, text: str, source: str, section: str) -> list[Chunk]:
        """Divide texto longo em chunks menores com overlap."""
        if len(text) <= self.chunk_size:
            return [Chunk(content=text, source_file=source, section=section)]

        chunks: list[Chunk] = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + self.chunk_size

            # Tenta nao cortar palavras no meio
            if end < text_len:
                # Procura ultimo espaco ou quebra de linha antes do limite
                last_space = text.rfind(" ", start, end)
                if last_space != -1 and last_space > start:
                    end = last_space

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    Chunk(content=chunk_text, source_file=source, section=section)
                )

            # Avança considerando o overlap
            start = end - self.overlap

            # Evita loop infinito se overlap >= chunk_size (nao deve acontecer com config padrao)
            if start >= end:
                start = end

        return chunks

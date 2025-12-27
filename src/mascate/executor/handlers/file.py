"""Handler de operacoes de arquivo para o Mascate.

Gerencia operacoes seguras de arquivo como abrir, listar, copiar, mover.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

from mascate.executor.handlers.base import BaseHandler
from mascate.executor.models import ActionType, Command

logger = logging.getLogger(__name__)


class FileHandler(BaseHandler):
    """Executa operacoes de arquivo de forma segura."""

    @property
    def supported_actions(self) -> list[ActionType]:
        """Retorna as acoes suportadas por este handler."""
        return [ActionType.FILE_OP]

    def execute(self, command: Command) -> bool:
        """Executa a operacao de arquivo.

        Args:
            command: Comando com target sendo o path e params contendo a operacao.

        Returns:
            True se executado com sucesso.
        """
        operation = command.params.get("operation", "open")
        target_path = Path(command.target).expanduser()

        logger.info("FileHandler executando '%s' em: %s", operation, target_path)

        try:
            if operation == "open":
                return self._open_file(target_path)
            elif operation == "list":
                return self._list_directory(target_path)
            elif operation == "copy":
                destination = command.params.get("destination")
                if not destination:
                    logger.error("Operacao 'copy' requer param 'destination'")
                    return False
                return self._copy_file(target_path, Path(destination).expanduser())
            elif operation == "move":
                destination = command.params.get("destination")
                if not destination:
                    logger.error("Operacao 'move' requer param 'destination'")
                    return False
                return self._move_file(target_path, Path(destination).expanduser())
            elif operation == "delete":
                return self._delete_file(target_path)
            elif operation == "mkdir":
                return self._make_directory(target_path)
            else:
                logger.warning("Operacao de arquivo desconhecida: %s", operation)
                return False
        except Exception as e:
            logger.error("Erro na operacao de arquivo '%s': %s", operation, e)
            return False

    def _open_file(self, path: Path) -> bool:
        """Abre um arquivo com o aplicativo padrao.

        Args:
            path: Caminho do arquivo.

        Returns:
            True se o arquivo foi aberto.
        """
        if not path.exists():
            logger.error("Arquivo nao encontrado: %s", path)
            return False

        try:
            subprocess.Popen(
                ["xdg-open", str(path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info("Arquivo aberto: %s", path)
            return True
        except Exception as e:
            logger.error("Falha ao abrir arquivo: %s", e)
            return False

    def _list_directory(self, path: Path) -> bool:
        """Lista o conteudo de um diretorio.

        Args:
            path: Caminho do diretorio.

        Returns:
            True se listado com sucesso.
        """
        if not path.is_dir():
            logger.error("Caminho nao e um diretorio: %s", path)
            return False

        try:
            contents = list(path.iterdir())
            logger.info("Conteudo de %s:", path)
            for item in contents:
                item_type = "DIR" if item.is_dir() else "FILE"
                logger.info("  [%s] %s", item_type, item.name)
            return True
        except PermissionError:
            logger.error("Permissao negada para listar: %s", path)
            return False

    def _copy_file(self, source: Path, destination: Path) -> bool:
        """Copia um arquivo ou diretorio.

        Args:
            source: Caminho de origem.
            destination: Caminho de destino.

        Returns:
            True se copiado com sucesso.
        """
        if not source.exists():
            logger.error("Origem nao encontrada: %s", source)
            return False

        try:
            if source.is_dir():
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
            logger.info("Copiado: %s -> %s", source, destination)
            return True
        except Exception as e:
            logger.error("Falha ao copiar: %s", e)
            return False

    def _move_file(self, source: Path, destination: Path) -> bool:
        """Move um arquivo ou diretorio.

        Args:
            source: Caminho de origem.
            destination: Caminho de destino.

        Returns:
            True se movido com sucesso.
        """
        if not source.exists():
            logger.error("Origem nao encontrada: %s", source)
            return False

        try:
            shutil.move(str(source), str(destination))
            logger.info("Movido: %s -> %s", source, destination)
            return True
        except Exception as e:
            logger.error("Falha ao mover: %s", e)
            return False

    def _delete_file(self, path: Path) -> bool:
        """Deleta um arquivo ou diretorio (REQUER CONFIRMACAO).

        Args:
            path: Caminho a deletar.

        Returns:
            True se deletado com sucesso.
        """
        if not path.exists():
            logger.error("Caminho nao encontrado: %s", path)
            return False

        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            logger.info("Deletado: %s", path)
            return True
        except Exception as e:
            logger.error("Falha ao deletar: %s", e)
            return False

    def _make_directory(self, path: Path) -> bool:
        """Cria um diretorio.

        Args:
            path: Caminho do diretorio a criar.

        Returns:
            True se criado com sucesso.
        """
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.info("Diretorio criado: %s", path)
            return True
        except Exception as e:
            logger.error("Falha ao criar diretorio: %s", e)
            return False

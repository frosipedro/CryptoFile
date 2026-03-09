"""
Classe base abstrata para todos os handlers de criptografia.
"""
from abc import ABC, abstractmethod
from pathlib import Path


class CryptoHandler(ABC):

    MAGIC: bytes = b''  # identificador no cabeçalho do arquivo cifrado

    @property
    @abstractmethod
    def name(self) -> str:
        """Nome do algoritmo."""

    @property
    @abstractmethod
    def kind(self) -> str:
        """'simetrico' ou 'assimetrico'."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Descrição curta do algoritmo."""

    @property
    @abstractmethod
    def key_info(self) -> str:
        """Informação sobre o tipo de chave usada."""

    @abstractmethod
    def encrypt_file(self, src: Path, dst: Path, **kwargs) -> dict:
        """
        Criptografa `src` e salva em `dst`.
        Retorna dict com metadados (ex.: chave gerada, caminho de chave etc.)
        """

    @abstractmethod
    def decrypt_file(self, src: Path, dst: Path, **kwargs) -> None:
        """Descriptografa `src` e salva em `dst`."""

    # ── helpers utilitários ──────────────────────────────────────

    @staticmethod
    def _read(path: Path) -> bytes:
        with open(path, 'rb') as f:
            return f.read()

    @staticmethod
    def _write(path: Path, data: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)
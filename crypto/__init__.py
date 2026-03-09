from .aes_handler import AESHandler
from .des_handler import DESHandler
from .rsa_handler import RSAHandler

# Registro central: chave → instância do handler
REGISTRY: dict = {
    '1': AESHandler(),
    '2': DESHandler(),
    '3': RSAHandler(),
}

__all__ = ['REGISTRY', 'AESHandler', 'DESHandler', 'RSAHandler']
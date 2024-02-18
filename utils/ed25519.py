from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ed25519


class Ed25519:
    @staticmethod
    def generate() -> ed25519.Ed25519PrivateKey:
        return ed25519.Ed25519PrivateKey.generate()

    @staticmethod
    def encode_private_key(private_key: ed25519.Ed25519PrivateKey) -> str:
        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

    @staticmethod
    def encode_public_key(public_key: ed25519.Ed25519PublicKey) -> str:
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

    @staticmethod
    def decode_private_key(encoded_private_key: str) -> ed25519.Ed25519PrivateKey:
        return serialization.load_pem_private_key(
            encoded_private_key.encode('utf-8'),
            password=None,
            backend=default_backend()
        )

    @staticmethod
    def decode_public_key(encoded_public_key: str) -> ed25519.Ed25519PublicKey:
        return serialization.load_pem_public_key(
            encoded_public_key.encode('utf-8'),
            backend=default_backend()
        )

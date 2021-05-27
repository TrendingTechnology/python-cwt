from typing import Any, Dict, List, Optional, Union

from cbor2 import CBORTag

from .cbor_processor import CBORProcessor
from .cose import COSE
from .cose_key import COSEKey
from .key_builder import KeyBuilder


class EncryptedCOSEKey(CBORProcessor):
    """
    An encrypted COSE key.
    """

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """
        Constructor.

        At the current implementation, any ``options`` will be ignored.
        """
        self._options = options
        self._cose = COSE()
        self._key_builder = KeyBuilder()
        return

    def decode(self, key: List[Any], encryption_key: COSEKey) -> COSEKey:
        """
        Returns an decrypted COSE key.

        Args:
            key: COSEKey: A key formatted to COSE_Encrypt0 structure to be decrypted.
            encryption_key: COSEKey: An encryption key to decrypt the target COSE key.
        Returns:
            COSEKey: A COSEKey decrypted.
        Raises:
            ValueError: Invalid arguments.
            DecodeError: Failed to decode the COSE key.
            VerifyError: Failed to verify the COSE key.
        """
        res = self._loads(self._cose.decode(CBORTag(16, key), encryption_key))
        return self._key_builder.from_dict(res)

    def encode(
        self,
        key: COSEKey,
        encryption_key: COSEKey,
        nonce: bytes = b"",
        tagged: bool = False,
    ) -> Union[List[Any], bytes]:
        """
        Returns an encrypted COSE key formatted to COSE_Encrypt0 structure.

        Args:
            key: COSEKey: A key to be encrypted.
            encryption_key: COSEKey: An encryption key to encrypt the target COSE key.
            nonce (bytes): A nonce for encryption.
        Returns:
            List[Any]: A COSE_Encrypt0 structure of the target COSE key.
        Raises:
            ValueError: Invalid arguments.
            EncodeError: Failed to encrypt the COSE key.
        """
        protected: Dict[int, Any] = {1: encryption_key.alg}
        unprotected: Dict[int, Any] = (
            {4: encryption_key.kid} if encryption_key.kid else {}
        )
        if not nonce:
            try:
                nonce = encryption_key.generate_nonce()
            except NotImplementedError:
                raise ValueError(
                    "Nonce generation is not supported for the key. Set a nonce explicitly."
                )
        unprotected[5] = nonce
        b_payload = self._dumps(key.to_dict())
        res: CBORTag = self._cose.encode_and_encrypt(
            b_payload,
            encryption_key,
            protected,
            unprotected,
            nonce=nonce,
            out="cbor2/CBORTag",
        )
        return res.value


# export
encrypted_cose_key = EncryptedCOSEKey()
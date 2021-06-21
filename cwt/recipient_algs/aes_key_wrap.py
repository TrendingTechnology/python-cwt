from typing import Any, Dict, List, Optional, Union

from cryptography.hazmat.primitives.keywrap import aes_key_unwrap, aes_key_wrap

from ..const import COSE_KEY_OPERATION_VALUES
from ..cose_key import COSEKey
from ..cose_key_interface import COSEKeyInterface
from ..exceptions import DecodeError, EncodeError
from ..recipient_interface import RecipientInterface


class AESKeyWrap(RecipientInterface):
    _ACCEPTABLE_KEY_OPS = [
        COSE_KEY_OPERATION_VALUES["wrapKey"],
        COSE_KEY_OPERATION_VALUES["unwrapKey"],
    ]

    def __init__(
        self,
        protected: Dict[int, Any],
        unprotected: Dict[int, Any],
        ciphertext: bytes = b"",
        recipients: List[Any] = [],
        key_ops: List[int] = [],
        key: bytes = b"",
    ):
        super().__init__(protected, unprotected, ciphertext, recipients, key_ops, key)

        if self._alg == -3:  # A128KW
            if self._key and len(self._key) != 16:
                raise ValueError(f"Invalid key length: {len(self._key)}.")
        elif self._alg == -4:  # A192KW
            if self._key and len(self._key) != 24:
                raise ValueError(f"Invalid key length: {len(self._key)}.")
        elif self._alg == -5:  # A256KW
            if self._key and len(self._key) != 32:
                raise ValueError(f"Invalid key length: {len(self._key)}.")
        else:
            raise ValueError(f"Unknown alg(3) for AES key wrap: {self._alg}.")

    def encode_key(
        self,
        key: Optional[COSEKeyInterface] = None,
        recipient_key: Optional[COSEKeyInterface] = None,
        alg: Optional[int] = None,
        context: Optional[Union[List[Any], Dict[str, Any]]] = None,
    ) -> COSEKeyInterface:
        if not key:
            raise ValueError("key should be set.")
        try:
            self._ciphertext = aes_key_wrap(self._key, key.key)
        except Exception as err:
            raise EncodeError("Failed to wrap key.") from err
        return key

    def decode_key(
        self,
        key: COSEKeyInterface,
        alg: Optional[int] = None,
        context: Optional[Union[List[Any], Dict[str, Any]]] = None,
    ) -> COSEKeyInterface:
        if not alg:
            raise ValueError("alg should be set.")
        try:
            unwrapped = aes_key_unwrap(key.key, self._ciphertext)
            return COSEKey.from_symmetric_key(unwrapped, alg=alg, kid=self._kid)
        except Exception as err:
            raise DecodeError("Failed to decode key.") from err

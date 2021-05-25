import hashlib
import hmac
from secrets import token_bytes
from typing import Any, Dict, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESCCM, AESGCM, ChaCha20Poly1305

from ..const import COSE_KEY_OPERATION_VALUES
from ..cose_key import COSEKey
from ..exceptions import DecodeError, EncodeError, VerifyError

_CWT_DEFAULT_HMAC_KEY_SIZE = 32  # bytes
_CWT_DEFAULT_AESGCM_NONCE_SIZE = 12  # bytes
_CWT_CHACHA20_POLY1305_NONCE_SIZE = 12  # bytes


class SymmetricKey(COSEKey):
    def __init__(self, cose_key: Dict[int, Any]):
        super().__init__(cose_key)

        self._key: bytes = b""

        # Validate kty.
        if cose_key[1] != 4:
            raise ValueError("kty(1) should be Symmetric(4).")

        # Validate k.
        if -1 in cose_key:
            if not isinstance(cose_key[-1], bytes):
                raise ValueError("k(-1) should be bytes(bstr).")
            self._key = cose_key[-1]

        if 3 not in cose_key:
            raise ValueError("alg(3) not found.")
        self._alg = cose_key[3]

    @property
    def key(self) -> bytes:
        return self._key

    def to_dict(self) -> Dict[int, Any]:
        res = super().to_dict()
        res[-1] = self._key
        return res


class MACAuthenticationKey(SymmetricKey):
    _ACCEPTABLE_KEY_OPS = [
        COSE_KEY_OPERATION_VALUES["MAC create"],
        COSE_KEY_OPERATION_VALUES["MAC verify"],
    ]

    def __init__(self, cose_key: Dict[int, Any]):
        super().__init__(cose_key)

        # Validate key_opt.
        if not self._key_ops:
            self._key_ops = MACAuthenticationKey._ACCEPTABLE_KEY_OPS
            return
        not_acceptable = [
            ops
            for ops in self._key_ops
            if ops not in MACAuthenticationKey._ACCEPTABLE_KEY_OPS
        ]
        if not_acceptable:
            raise ValueError(
                f"Unknown or not permissible key_ops(4) for MACAuthenticationKey: {not_acceptable[0]}."
            )


class ContentEncryptionKey(SymmetricKey):
    _ACCEPTABLE_KEY_OPS = [
        COSE_KEY_OPERATION_VALUES["encrypt"],
        COSE_KEY_OPERATION_VALUES["decrypt"],
        COSE_KEY_OPERATION_VALUES["wrap key"],
        COSE_KEY_OPERATION_VALUES["unwrap key"],
    ]

    def __init__(self, cose_key: Dict[int, Any]):
        super().__init__(cose_key)

        # Validate key_opt.
        if not self._key_ops:
            self._key_ops = ContentEncryptionKey._ACCEPTABLE_KEY_OPS
            return
        not_acceptable = [
            ops
            for ops in self._key_ops
            if ops not in ContentEncryptionKey._ACCEPTABLE_KEY_OPS
        ]
        if not_acceptable:
            raise ValueError(
                f"Unknown or not permissible key_ops(4) for ContentEncryptionKey: {not_acceptable[0]}."
            )


class HMACKey(MACAuthenticationKey):
    """ """

    def __init__(self, cose_key: Dict[int, Any]):
        """ """
        super().__init__(cose_key)

        self._hash_alg = None
        self._trunc = 0
        if not self._key:
            self._key = token_bytes(_CWT_DEFAULT_HMAC_KEY_SIZE)

        # Validate alg.
        if self._alg == 4:  # HMAC 256/64
            self._hash_alg = hashlib.sha256
            self._trunc = 8
        elif self._alg == 5:  # HMAC 256/256
            self._hash_alg = hashlib.sha256
            self._trunc = 32
        elif self._alg == 6:  # HMAC 384/384
            self._hash_alg = hashlib.sha384
            self._trunc = 48
        elif self._alg == 7:  # HMAC 512/512
            self._hash_alg = hashlib.sha512
            self._trunc = 64
        else:
            raise ValueError(f"Unsupported or unknown alg({self._alg}) for HMAC.")

    def sign(self, msg: bytes) -> bytes:
        """ """
        try:
            return hmac.new(self._key, msg, self._hash_alg).digest()[0 : self._trunc]
        except Exception as err:
            raise EncodeError("Failed to sign.") from err

    def verify(self, msg: bytes, sig: bytes):
        """ """
        if hmac.compare_digest(sig, self.sign(msg)):
            return
        raise VerifyError("Failed to compare digest.")


class AESCCMKey(ContentEncryptionKey):
    """ """

    def __init__(self, cose_key: Dict[int, Any]):
        """ """
        super().__init__(cose_key)

        self._cipher: AESCCM
        self._nonce_len = 0

        # Validate alg.
        if self._alg == 10:  # AES-CCM-16-64-128
            if not self._key:
                self._key = AESCCM.generate_key(bit_length=128)
            if len(self._key) != 16:
                raise ValueError(
                    "The length of AES-CCM-16-64-128 key should be 16 bytes."
                )
            self._cipher = AESCCM(self._key, tag_length=8)
            self._nonce_len = 13
        elif self._alg == 11:  # AES-CCM-16-64-256
            if not self._key:
                self._key = AESCCM.generate_key(bit_length=256)
            if len(self._key) != 32:
                raise ValueError(
                    "The length of AES-CCM-16-64-256 key should be 32 bytes."
                )
            self._cipher = AESCCM(self._key, tag_length=8)
            self._nonce_len = 13
        elif self._alg == 12:  # AES-CCM-64-64-128
            if not self._key:
                self._key = AESCCM.generate_key(bit_length=128)
            if len(self._key) != 16:
                raise ValueError(
                    "The length of AES-CCM-64-64-128 key should be 16 bytes."
                )
            self._cipher = AESCCM(self._key, tag_length=8)
            self._nonce_len = 7
        elif self._alg == 13:  # AES-CCM-64-64-256
            if not self._key:
                self._key = AESCCM.generate_key(bit_length=256)
            if len(self._key) != 32:
                raise ValueError(
                    "The length of AES-CCM-64-64-256 key should be 32 bytes."
                )
            self._cipher = AESCCM(self._key, tag_length=8)
            self._nonce_len = 7
        elif self._alg == 30:  # AES-CCM-16-128-128
            if not self._key:
                self._key = AESCCM.generate_key(bit_length=128)
            if len(self._key) != 16:
                raise ValueError(
                    "The length of AES-CCM-16-128-128 key should be 16 bytes."
                )
            self._cipher = AESCCM(self._key)
            self._nonce_len = 13
        elif self._alg == 31:  # AES-CCM-16-128-256
            if not self._key:
                self._key = AESCCM.generate_key(bit_length=256)
            if len(self._key) != 32:
                raise ValueError(
                    "The length of AES-CCM-16-128-256 key should be 32 bytes."
                )
            self._cipher = AESCCM(self._key)
            self._nonce_len = 13
        elif self._alg == 32:  # AES-CCM-64-128-128
            if not self._key:
                self._key = AESCCM.generate_key(bit_length=128)
            if len(self._key) != 16:
                raise ValueError(
                    "The length of AES-CCM-64-128-128 key should be 16 bytes."
                )
            self._cipher = AESCCM(self._key)
            self._nonce_len = 7
        elif self._alg == 33:  # AES-CCM-64-128-256
            if not self._key:
                self._key = AESCCM.generate_key(bit_length=256)
            if len(self._key) != 32:
                raise ValueError(
                    "The length of AES-CCM-64-128-256 key should be 32 bytes."
                )
            self._cipher = AESCCM(self._key)
            self._nonce_len = 7
        else:
            raise ValueError(f"Unsupported or unknown alg({self._alg}) for AES CCM.")

    def generate_nonce(self):
        return token_bytes(self._nonce_len)

    def encrypt(self, msg: bytes, nonce: bytes, aad: Optional[bytes] = None) -> bytes:
        """ """
        if len(nonce) != self._nonce_len:
            raise ValueError(
                "The length of nonce should be %d bytes." % self._nonce_len
            )
        try:
            return self._cipher.encrypt(nonce, msg, aad)
        except Exception as err:
            raise EncodeError("Failed to encrypt.") from err

    def decrypt(self, msg: bytes, nonce: bytes, aad: Optional[bytes] = None) -> bytes:
        """ """
        if len(nonce) != self._nonce_len:
            raise ValueError(
                "The length of nonce should be %d bytes." % self._nonce_len
            )
        try:
            return self._cipher.decrypt(nonce, msg, aad)
        except Exception as err:
            raise DecodeError("Failed to decrypt.") from err


class AESGCMKey(ContentEncryptionKey):
    """ """

    def __init__(self, cose_key: Dict[int, Any]):
        """ """
        super().__init__(cose_key)

        self._cipher: AESGCM

        # Validate alg.
        if self._alg == 1:  # A128GCM
            if not self._key:
                self._key = AESGCM.generate_key(bit_length=128)
            if len(self._key) != 16:
                raise ValueError("The length of A128GCM key should be 16 bytes.")
        elif self._alg == 2:  # A192GCM
            if not self._key:
                self._key = AESGCM.generate_key(bit_length=192)
            if len(self._key) != 24:
                raise ValueError("The length of A192GCM key should be 24 bytes.")
        elif self._alg == 3:  # A256GCM
            if not self._key:
                self._key = AESGCM.generate_key(bit_length=256)
            if len(self._key) != 32:
                raise ValueError("The length of A256GCM key should be 32 bytes.")
        else:
            raise ValueError(f"Unsupported or unknown alg(3) for AES GCM: {self._alg}.")

        self._cipher = AESGCM(self._key)
        return

    def generate_nonce(self):
        return token_bytes(_CWT_DEFAULT_AESGCM_NONCE_SIZE)

    def encrypt(self, msg: bytes, nonce: bytes, aad: Optional[bytes] = None) -> bytes:
        """ """
        try:
            return self._cipher.encrypt(nonce, msg, aad)
        except Exception as err:
            raise EncodeError("Failed to encrypt.") from err

    def decrypt(self, msg: bytes, nonce: bytes, aad: Optional[bytes] = None) -> bytes:
        """ """
        try:
            return self._cipher.decrypt(nonce, msg, aad)
        except Exception as err:
            raise DecodeError("Failed to decrypt.") from err


class ChaCha20Key(ContentEncryptionKey):
    def __init__(self, cose_key: Dict[int, Any]):
        super().__init__(cose_key)

        # Validate alg.
        if self._alg != 24:  # ChaCha20/Poly1305
            raise ValueError(
                f"Unsupported or unknown alg(3) for ChaCha20: {self._alg}."
            )

        if not self._key:
            self._key = ChaCha20Poly1305.generate_key()
        if len(self._key) != 32:
            raise ValueError("The length of ChaCha20/Poly1305 key should be 32 bytes.")
        self._cipher = ChaCha20Poly1305(self._key)
        return

    def generate_nonce(self):
        return token_bytes(_CWT_CHACHA20_POLY1305_NONCE_SIZE)

    def encrypt(self, msg: bytes, nonce: bytes, aad: Optional[bytes] = None) -> bytes:
        try:
            return self._cipher.encrypt(nonce, msg, aad)
        except Exception as err:
            raise EncodeError("Failed to encrypt.") from err

    def decrypt(self, msg: bytes, nonce: bytes, aad: Optional[bytes] = None) -> bytes:
        try:
            return self._cipher.decrypt(nonce, msg, aad)
        except Exception as err:
            raise DecodeError("Failed to decrypt.") from err
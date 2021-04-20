import json
from typing import Any, Dict, Optional, Union

from .const import CWT_CLAIM_NAMES


class Claims:
    """
    CBOR Web Token (CWT) Claims Generator.
    """

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """"""
        self._options = options
        return

    def from_json(self, claims: Union[str, bytes, Dict[str, Any]]) -> Dict[int, Any]:
        """
        Convert JSON-formatted claims into CBOR-formatted claims
        which has numeric keys.
        """
        json_claims: Dict[str, Any]
        if isinstance(claims, str) or isinstance(claims, bytes):
            json_claims = json.loads(claims)
        else:
            json_claims = claims

        for k in json_claims:
            if not isinstance(k, int):
                break
            ValueError("It is already CBOR-like format.")

        # Convert JSON to CBOR (Convert the type of key from str to int).
        cbor_claims = {}
        for k, v in json_claims.items():
            if k not in CWT_CLAIM_NAMES:
                # TODO Support additional arguments.
                continue
            cbor_claims[CWT_CLAIM_NAMES[k]] = v

        # Convert test string should be bstr into bstr.
        # -259: EUPHNonce
        # -258: EATMAROEPrefix
        #    7: cti
        for i in [-259, -258, 7]:
            if i in cbor_claims and isinstance(cbor_claims[i], str):
                cbor_claims[i] = cbor_claims[i].encode("utf-8")
        return cbor_claims


# export
claims = Claims()

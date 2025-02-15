# Python CWT

[![PyPI version](https://badge.fury.io/py/cwt.svg)](https://badge.fury.io/py/cwt)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cwt)
[![Documentation Status](https://readthedocs.org/projects/python-cwt/badge/?version=latest)](https://python-cwt.readthedocs.io/en/latest/?badge=latest)
![Github CI](https://github.com/dajiaji/python-cwt/actions/workflows/python-package.yml/badge.svg)
[![codecov](https://codecov.io/gh/dajiaji/python-cwt/branch/main/graph/badge.svg?token=QN8GXEYEP3)](https://codecov.io/gh/dajiaji/python-cwt)


Python CWT is a CBOR Web Token (CWT) and CBOR Object Signing and Encryption (COSE)
implementation compliant with:
- [RFC8392: CWT (CBOR Web Token)](https://tools.ietf.org/html/rfc8392)
- [RFC8152: COSE (CBOR Object Signing and Encryption)](https://tools.ietf.org/html/rfc8152)
- and related various specifications. See [Referenced Specifications](#referenced-specifications).

It is designed to make users who already know about [JWS](https://tools.ietf.org/html/rfc7515)/[JWE](https://tools.ietf.org/html/rfc7516)/[JWT](https://tools.ietf.org/html/rfc7519)
be able to use it in ease. Little knowledge of [CBOR](https://tools.ietf.org/html/rfc7049)/[COSE](https://tools.ietf.org/html/rfc8152)/[CWT](https://tools.ietf.org/html/rfc8392)
is required to use it.

You can install Python CWT with pip:


```sh
$ pip install cwt
```

And then, you can use it as follows:

```py
>>> import cwt
>>> from cwt import COSEKey
>>> key = COSEKey.from_symmetric_key(alg="HS256", kid="01")
>>> token = cwt.encode({"iss": "coaps://as.example", "sub": "dajiaji", "cti": "123"}, key)
>>> token.hex()
'd18443a10105a05835a60172636f6170733a2f2f61732e657861'...
>>> cwt.decode(token, key)
{1: 'coaps://as.example', 2: 'dajiaji', 7: b'123', 4: 1620088759, 5: 1620085159, 6: 1620085159}
```

See [Document](https://python-cwt.readthedocs.io/en/stable/) for details.

## Index

- [Installing](#installing)
- [CWT Usage Examples](#cwt-usage-examples)
    - [MACed CWT](#maced-cwt)
    - [Signed CWT](#signed-cwt)
    - [Encrypted CWT](#encrypted-cwt)
    - [Nested CWT](#nested-cwt)
    - [CWT with User Settings (e.g., expires\_in)](#cwt-with-user-settings)
    - [CWT with User-Defined Claims](#cwt-with-user-defined-claims)
    - [CWT with PoP Key](#cwt-with-pop-key)
    - [CWT for EUDCC (EU Digital COVID Certificate)](#cwt-for-eudcc-eu-digital-covid-certificate)
- [COSE Usage Examples](#cose-usage-examples)
    - [COSE MAC0](#cose-mac0)
    - [COSE MAC](#cose-mac)
        - [Direct Key Distribution](#direct-key-distribution-for-mac)
        - [Direct Key with KDF](#direct-key-with-kdf-for-mac)
        - [AES Key Wrap](#aes-key-wrap-for-mac)
        - [Direct key Agreement](#direct-key-agreement-for-mac)
        - [Key Agreement with Key Wrap](#key-agreement-with-key-wrap-for-mac)
    - [COSE Encrypt0](#cose-encrypt0)
    - [COSE Encrypt](#cose-encrypt)
        - [Direct Key Distribution](#direct-key-distribution-for-encryption)
        - [Direct Key with KDF](#direct-key-with-kdf-for-encryption)
        - [AES Key Wrap](#aes-key-wrap-for-encryption)
        - [Direct key Agreement](#direct-key-agreement-for-encryption)
        - [Key Agreement with Key Wrap](#key-agreement-with-key-wrap-for-encryption)
    - [COSE Signature1](#cose-signature1)
    - [COSE Signature](#cose-signature)
- [API Reference](#api-reference)
- [Supported CWT Claims](#supported-cwt-claims)
- [Supported COSE Algorithms](#supported-cose-algorithms)
- [Referenced Specifications](#referenced-specifications)
- [Tests](#tests)

## Installing

Install with pip:

```
pip install cwt
```

## CWT Usage Examples

Followings are typical and basic examples which create various types of CWTs, verify and decode them.

[CWT API](https://python-cwt.readthedocs.io/en/stable/api.html) in the examples are built
on top of [COSE API](https://python-cwt.readthedocs.io/en/stable/api.html#cwt.COSE).

See [API Reference](https://python-cwt.readthedocs.io/en/stable/api.html) and
[CWT Usage Examples on document](https://python-cwt.readthedocs.io/en/stable/cwt_usage.html)
for more details.

### MACed CWT

Create a MACed CWT with `HS256`, verify and decode it as follows:

```py
import cwt
from cwt import Claims, COSEKey

try:
    key = COSEKey.from_symmetric_key(alg="HS256", kid="01")
    token = cwt.encode({"iss": "coaps://as.example", "sub": "dajiaji", "cti": "123"}, key)
    decoded = cwt.decode(token, key)

    # If you want to treat the result like a JWT;
    readable = Claims.new(decoded)
    assert readable.iss == 'coaps://as.example'
    assert readable.sub == 'dajiaji'
    assert readable.cti == '123'
    # readable.exp == 1620088759
    # readable.nbf == 1620085159
    # readable.iat == 1620085159

except Exception as err:
    # All the other examples in this document omit error handling but this CWT library
    # can throw following errors:
    #   ValueError: Invalid arguments.
    #   EncodeError: Failed to encode.
    #   VerifyError: Failed to verify.
    #   DecodeError: Failed to decode.
    print(err)
```

A raw CWT structure (Dict[int, Any]) can also be used as follows:

```py
import cwt
from cwt import COSEKey

key = COSEKey.from_symmetric_key(alg="HS256", kid="01")
token = cwt.encode({1: "coaps://as.example", 2: "dajiaji", 7: b"123"}, key)
decoded = cwt.decode(token, key)
```

MAC algorithms other than `HS256` are listed in
[Supported COSE Algorithms](https://python-cwt.readthedocs.io/en/stable/algorithms.html).

### Signed CWT

Create an `Ed25519` key pair:

```sh
$ openssl genpkey -algorithm ed25519 -out private_key.pem
$ openssl pkey -in private_key.pem -pubout -out public_key.pem
```

Create a Signed CWT with `Ed25519`, verify and decode it with the key pair as follows:

```py
import cwt
from cwt import COSEKey

# The sender side:
with open("./private_key.pem") as key_file:
    private_key = COSEKey.from_pem(key_file.read(), kid="01")
token = cwt.encode(
    {"iss": "coaps://as.example", "sub": "dajiaji", "cti": "123"}, private_key
)

# The recipient side:
with open("./public_key.pem") as key_file:
    public_key = COSEKey.from_pem(key_file.read(), kid="01")
decoded = cwt.decode(token, public_key)
```

JWKs can also be used instead of the PEM-formatted keys as follows:

```py
import cwt
from cwt import COSEKey

# The sender side:
private_key = COSEKey.from_jwk({
    "kid": "01",
    "kty": "OKP",
    "key_ops": ["sign"],
    "alg": "EdDSA",
    "crv": "Ed25519",
    "x": "2E6dX83gqD_D0eAmqnaHe1TC1xuld6iAKXfw2OVATr0",
    "d": "L8JS08VsFZoZxGa9JvzYmCWOwg7zaKcei3KZmYsj7dc",
})
token = cwt.encode(
    {"iss": "coaps://as.example", "sub": "dajiaji", "cti": "123"}, private_key
)

# The recipient side:
public_key = COSEKey.from_jwk({
    "kid": "01",
    "kty": "OKP",
    "key_ops": ["verify"],
    "crv": "Ed25519",
    "x": "2E6dX83gqD_D0eAmqnaHe1TC1xuld6iAKXfw2OVATr0",
})
decoded = cwt.decode(token, public_key)
```

Signing algorithms other than `Ed25519` are listed in
[Supported COSE Algorithms](https://python-cwt.readthedocs.io/en/stable/algorithms.html).

### Encrypted CWT

Create an encrypted CWT with `ChaCha20/Poly1305` and decrypt it as follows:

```py
import cwt
from cwt import COSEKey

enc_key = COSEKey.from_symmetric_key(alg="ChaCha20/Poly1305", kid="01")
token = cwt.encode({"iss": "coaps://as.example", "sub": "dajiaji", "cti": "123"}, enc_key)
decoded = cwt.decode(token, enc_key)
```

Encryption algorithms other than `ChaCha20/Poly1305` are listed in
[Supported COSE Algorithms](https://python-cwt.readthedocs.io/en/stable/algorithms.html).

### Nested CWT

Create a signed CWT and encrypt it, and then decrypt and verify the nested CWT as follows.

```py
import cwt
from cwt import COSEKey

# A shared encryption key.
enc_key = COSEKey.from_symmetric_key(alg="ChaCha20/Poly1305", kid="enc-01")

# Creates a CWT with ES256 signing.
with open("./private_key.pem") as key_file:
    private_key = COSEKey.from_pem(key_file.read(), kid="sig-01")
token = cwt.encode(
    {"iss": "coaps://as.example", "sub": "dajiaji", "cti": "123"}, private_key
)

# Encrypts the signed CWT.
nested = cwt.encode(token, enc_key)

# Decrypts and verifies the nested CWT.
with open("./public_key.pem") as key_file:
    public_key = COSEKey.from_pem(key_file.read(), kid="sig-01")
decoded = cwt.decode(nested, [enc_key, public_key])
```

### CWT with User Settings

The `cwt` in `cwt.encode()` and `cwt.decode()` above is a global `CWT` class instance created
with default settings in advance. The default settings are as follows:
- `expires_in`: `3600` seconds. This is the default lifetime in seconds of CWTs.
- `leeway`: `60` seconds. This is the default leeway in seconds for validating `exp` and `nbf`.

If you want to change the settings, you can create your own `CWT` class instance as follows:

```py
from cwt import COSEKey, CWT

key = COSEKey.from_symmetric_key(alg="HS256", kid="01")
mycwt = CWT.new(expires_in=3600*24, leeway=10)
token = mycwt.encode({"iss": "coaps://as.example", "sub": "dajiaji", "cti": "123"}, key)
decoded = mycwt.decode(token, key)
```

### CWT with User-Defined Claims

You can use your own claims as follows:

Note that such user-defined claim's key should be less than -65536.

```py
import cwt
from cwt import COSEKey

# The sender side:
with open("./private_key.pem") as key_file:
    private_key = COSEKey.from_pem(key_file.read(), kid="01")
token = cwt.encode(
    {
        1: "coaps://as.example",  # iss
        2: "dajiaji",  # sub
        7: b"123",  # cti
        -70001: "foo",
        -70002: ["bar"],
        -70003: {"baz": "qux"},
        -70004: 123,
    },
    private_key,
)

# The recipient side:
with open("./public_key.pem") as key_file:
    public_key = COSEKey.from_pem(key_file.read(), kid="01")
raw = cwt.decode(token, public_key)
assert raw[-70001] == "foo"
assert raw[-70002][0] == "bar"
assert raw[-70003]["baz"] == "qux"
assert raw[-70004] == 123

readable = Claims.new(raw)
assert readable.get(-70001) == "foo"
assert readable.get(-70002)[0] == "bar"
assert readable.get(-70003)["baz"] == "qux"
assert readable.get(-70004) == 123
```

User-defined claims can also be used with JSON-based claims as follows:

```py
import cwt
from cwt import Claims, COSEKey

with open("./private_key.pem") as key_file:
    private_key = COSEKey.from_pem(key_file.read(), kid="01")

my_claim_names = {
    "ext_1": -70001,
    "ext_2": -70002,
    "ext_3": -70003,
    "ext_4": -70004,
}

cwt.set_private_claim_names(my_claim_names)
token = cwt.encode(
    {
        "iss": "coaps://as.example",
        "sub": "dajiaji",
        "cti": b"123",
        "ext_1": "foo",
        "ext_2": ["bar"],
        "ext_3": {"baz": "qux"},
        "ext_4": 123,
    },
    private_key,
)

with open("./public_key.pem") as key_file:
    public_key = COSEKey.from_pem(key_file.read(), kid="01")

raw = cwt.decode(token, public_key)
readable = Claims.new(
    raw,
    private_claims_names=my_claim_names,
)
assert readable.get("ext_1") == "foo"
assert readable.get("ext_2")[0] == "bar"
assert readable.get("ext_3")["baz"] == "qux"
assert readable.get("ext_4") == 123
```


### CWT with PoP Key

Python CWT supports [Proof-of-Possession Key Semantics for CBOR Web Tokens (CWTs)](https://tools.ietf.org/html/rfc8747).
A CWT can include a PoP key as follows:

On the issuer side:

```py
import cwt
from cwt import COSEKey

# Prepares a signing key for CWT in advance.
with open("./private_key_of_issuer.pem") as key_file:
    private_key = COSEKey.from_pem(key_file.read(), kid="issuer-01")

# Sets the PoP key to a CWT for the presenter.
token = cwt.encode(
    {
        "iss": "coaps://as.example",
        "sub": "dajiaji",
        "cti": "123",
        "cnf": {
            "jwk": {  # Provided by the CWT presenter.
                "kty": "OKP",
                "use": "sig",
                "crv": "Ed25519",
                "kid": "presenter-01",
                "x": "2E6dX83gqD_D0eAmqnaHe1TC1xuld6iAKXfw2OVATr0",
                "alg": "EdDSA",
            },
        },
    },
    private_key,
)

# Issues the token to the presenter.
```

On the CWT presenter side:

```py
import cwt
from cwt import COSEKey

# Prepares a private PoP key in advance.
with open("./private_pop_key.pem") as key_file:
    pop_key_private = COSEKey.from_pem(key_file.read(), kid="presenter-01")

# Receives a message (e.g., nonce)  from the recipient.
msg = b"could-you-sign-this-message?"  # Provided by recipient.

# Signs the message with the private PoP key.
sig = pop_key_private.sign(msg)

# Sends the msg and the sig with the CWT to the recipient.
```

On the CWT recipient side:

```py
import cwt
from cwt import Claims, COSEKey

# Prepares the public key of the issuer in advance.
with open("./public_key_of_issuer.pem") as key_file:
    public_key = COSEKey.from_pem(key_file.read(), kid="issuer-01")

# Verifies and decodes the CWT received from the presenter.
raw = cwt.decode(token, public_key)
decoded = Claims.new(raw)

# Extracts the PoP key from the CWT.
extracted_pop_key = COSEKey.new(decoded.cnf)  # = raw[8][1]

# Then, verifies the message sent by the presenter
# with the signature which is also sent by the presenter as follows:
extracted_pop_key.verify(msg, sig)
```

[Usage Examples](https://python-cwt.readthedocs.io/en/stable/cwt_usage.html#cwt-with-pop-key)
shows other examples which use other confirmation methods for PoP keys.

### CWT for EUDCC (EU Digital COVID Certificate)

Python CWT supports [Electronic Health Certificate Specification](https://github.com/ehn-dcc-development/hcert-spec/blob/main/hcert_spec.md)
and [EUDCC (EU Digital COVID Certificate)](https://ec.europa.eu/info/live-work-travel-eu/coronavirus-response/safe-covid-19-vaccines-europeans/eu-digital-covid-certificate_en) compliant with [Technical Specifications for Digital Green Certificates Volume 1](https://ec.europa.eu/health/sites/default/files/ehealth/docs/digital-green-certificates_v1_en.pdf)

A following example shows how to verify an EUDCC:

```py
import cwt
from cwt import load_pem_hcert_dsc

# A DSC(Document Signing Certificate) issued by a CSCA
# (Certificate Signing Certificate Authority) quoted from:
# https://github.com/eu-digital-green-certificates/dgc-testdata/blob/main/AT/2DCode/raw/1.json
dsc = "-----BEGIN CERTIFICATE-----\nMIIBvTCCAWOgAwIBAgIKAXk8i88OleLsuTAKBggqhkjOPQQDAjA2MRYwFAYDVQQDDA1BVCBER0MgQ1NDQSAxMQswCQYDVQQGEwJBVDEPMA0GA1UECgwGQk1TR1BLMB4XDTIxMDUwNTEyNDEwNloXDTIzMDUwNTEyNDEwNlowPTERMA8GA1UEAwwIQVQgRFNDIDExCzAJBgNVBAYTAkFUMQ8wDQYDVQQKDAZCTVNHUEsxCjAIBgNVBAUTATEwWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAASt1Vz1rRuW1HqObUE9MDe7RzIk1gq4XW5GTyHuHTj5cFEn2Rge37+hINfCZZcozpwQKdyaporPUP1TE7UWl0F3o1IwUDAOBgNVHQ8BAf8EBAMCB4AwHQYDVR0OBBYEFO49y1ISb6cvXshLcp8UUp9VoGLQMB8GA1UdIwQYMBaAFP7JKEOflGEvef2iMdtopsetwGGeMAoGCCqGSM49BAMCA0gAMEUCIQDG2opotWG8tJXN84ZZqT6wUBz9KF8D+z9NukYvnUEQ3QIgdBLFSTSiDt0UJaDF6St2bkUQuVHW6fQbONd731/M4nc=\n-----END CERTIFICATE-----"

# An EUDCC (EU Digital COVID Certificate) quoted from:
# https://github.com/eu-digital-green-certificates/dgc-testdata/blob/main/AT/2DCode/raw/1.json
eudcc = bytes.fromhex(
    "d2844da20448d919375fc1e7b6b20126a0590133a4041a61817ca0061a60942ea001624154390103a101a4617681aa62646e01626d616d4f52472d3130303033303231356276706a313131393334393030376264746a323032312d30322d313862636f624154626369783155524e3a555643493a30313a41543a31303830373834334639344145453045453530393346424332353442443831332342626d706c45552f312f32302f31353238626973781b4d696e6973747279206f66204865616c74682c20417573747269616273640262746769383430353339303036636e616da463666e74754d5553544552465241553c474f455353494e47455262666e754d7573746572667261752d47c3b6c39f696e67657263676e74684741425249454c4562676e684761627269656c656376657265312e302e3063646f626a313939382d30322d323658405812fce67cb84c3911d78e3f61f890d0c80eb9675806aebed66aa2d0d0c91d1fc98d7bcb80bf00e181806a9502e11b071325901bd0d2c1b6438747b8cc50f521"
)

public_key = load_pem_hcert_dsc(dsc)
decoded = cwt.decode(eudcc, keys=[public_key])
claims = Claims.new(decoded)
# claims.hcert[1] ==
# {
#     'v': [
#         {
#             'dn': 1,
#             'ma': 'ORG-100030215',
#             'vp': '1119349007',
#             'dt': '2021-02-18',
#             'co': 'AT',
#             'ci': 'URN:UVCI:01:AT:10807843F94AEE0EE5093FBC254BD813#B',
#             'mp': 'EU/1/20/1528',
#             'is': 'Ministry of Health, Austria',
#             'sd': 2,
#             'tg': '840539006',
#         }
#     ],
#     'nam': {
#         'fnt': 'MUSTERFRAU<GOESSINGER',
#         'fn': 'Musterfrau-Gößinger',
#         'gnt': 'GABRIELE',
#         'gn': 'Gabriele',
#     },
#     'ver': '1.0.0',
#     'dob': '1998-02-26',
# }
```

## COSE Usage Examples

Followings are typical and basic examples which create various types of COSE messages, verify and decode them.

See [API Reference](https://python-cwt.readthedocs.io/en/stable/api.html#cwt.COSE) and
[COSE Usage Examples on document](https://python-cwt.readthedocs.io/en/stable/cose_usage.html) for more details.

### COSE MAC0

Create a COSE MAC0 message, verify and decode it as follows:

```py
from cwt import COSE, COSEKey

mac_key = COSEKey.from_symmetric_key(alg="HS256", kid="01")
ctx = COSE.new(alg_auto_inclusion=True, kid_auto_inclusion=True)
encoded = ctx.encode_and_mac(b"Hello world!", mac_key)
assert b"Hello world!" == ctx.decode(encoded, mac_key)
```

Following two samples are other ways of writing the above example:

```py
from cwt import COSE, COSEKey

mac_key = COSEKey.from_symmetric_key(alg="HS256", kid="01")
ctx = COSE.new()
encoded = ctx.encode_and_mac(
    b"Hello world!",
    mac_key,
    protected={"alg": "HS256"},
    unprotected={"kid": "01"},
)
assert b"Hello world!" == ctx.decode(encoded, mac_key)
```

```py
from cwt import COSE, COSEKey

mac_key = COSEKey.from_symmetric_key(alg="HS256", kid="01")
ctx = COSE.new()
encoded = ctx.encode_and_mac(
    b"Hello world!",
    mac_key,
    protected={1: 5},
    unprotected={4: b"01"},
)
assert b"Hello world!" == ctx.decode(encoded, mac_key)
```

### COSE MAC

#### Direct Key Distribution for MAC

The direct key distribution shares a MAC key between the sender and the recipient that is used directly.
The follwing example shows the simplest way to make a COSE MAC message, verify and decode it with the direct
key distribution method.

```py
from cwt import COSE, COSEKey, Recipient

# The sender makes a COSE MAC message as follows:
mac_key = COSEKey.from_symmetric_key(alg="HS512", kid="01")
r = Recipient.from_jwk({"alg": "direct"})
r.apply(mac_key)
ctx = COSE.new()
encoded = ctx.encode_and_mac(b"Hello world!", mac_key, recipients=[r])

# The recipient has the same MAC key and can verify and decode it:
assert b"Hello world!" == ctx.decode(encoded, mac_key)
```

#### Direct Key with KDF for MAC


```py
from secrets import token_bytes
from cwt import COSE, COSEKey, Recipient

shared_material = token_bytes(32)
shared_key = COSEKey.from_symmetric_key(shared_material, kid="01")

# The sender side:
r = Recipient.from_jwk(
    {
        "kty": "oct",
        "alg": "direct+HKDF-SHA-256",
    },
)
mac_key = r.apply(shared_key, context={"alg": "HS256"})
ctx = COSE.new(alg_auto_inclusion=True)
encoded = ctx.encode_and_mac(
    b"Hello world!",
    key=mac_key,
    recipients=[r],
)

# The recipient side:
assert b"Hello world!" == ctx.decode(encoded, shared_key, context={"alg": "HS256"})
```

#### AES Key Wrap for MAC

The AES key wrap algorithm can be used to wrap a MAC key as follows:

```py
from cwt import COSE, COSEKey, Recipient

# The sender side:
mac_key = COSEKey.from_symmetric_key(alg="HS512")
r = Recipient.from_jwk(
    {
        "kid": "01",
        "alg": "A128KW",
        "k": "hJtXIZ2uSN5kbQfbtTNWbg",  # A shared wrapping key
    },
)
r.apply(mac_key)
ctx = COSE.new(alg_auto_inclusion=True)
encoded = ctx.encode_and_mac(b"Hello world!", key=mac_key, recipients=[r])

# The recipient side:
shared_key = COSEKey.from_jwk(
    {
        "kid": "01",
        "kty": "oct",
        "alg": "A128KW",
        "k": "hJtXIZ2uSN5kbQfbtTNWbg",
    },
)
assert b"Hello world!" == ctx.decode(encoded, shared_key)
```

#### Direct Key Agreement for MAC

The direct key agreement methods can be used to create a shared secret. A KDF (Key Distribution Function) is then
applied to the shared secret to derive a key to be used to protect the data.
The follwing example shows a simple way to make a COSE Encrypt message, verify and decode it with the direct key
agreement methods (``ECDH-ES+HKDF-256`` with various curves).

```py
from cwt import COSE, COSEKey, Recipient

# The sender side:
r = Recipient.from_jwk(
    {
        "kty": "EC",
        "alg": "ECDH-ES+HKDF-256",
        "crv": "P-256",
    },
)
# The following key is provided by the recipient in advance.
pub_key = COSEKey.from_jwk(
    {
        "kid": "01",
        "kty": "EC",
        "alg": "ECDH-ES+HKDF-256",
        "crv": "P-256",
        "x": "Ze2loSV3wrroKUN_4zhwGhCqo3Xhu1td4QjeQ5wIVR0",
        "y": "HlLtdXARY_f55A3fnzQbPcm6hgr34Mp8p-nuzQCE0Zw",
    }
)
mac_key = r.apply(recipient_key=pub_key, context={"alg": "HS256"})
ctx = COSE.new(alg_auto_inclusion=True)
encoded = ctx.encode_and_mac(
    b"Hello world!",
    key=mac_key,
    recipients=[r],
)

# The recipient side:
# The following key is the private key of the above pub_key.
priv_key = COSEKey.from_jwk(
    {
        "kid": "01",
        "kty": "EC",
        "alg": "ECDH-ES+HKDF-256",
        "crv": "P-256",
        "x": "Ze2loSV3wrroKUN_4zhwGhCqo3Xhu1td4QjeQ5wIVR0",
        "y": "HlLtdXARY_f55A3fnzQbPcm6hgr34Mp8p-nuzQCE0Zw",
        "d": "r_kHyZ-a06rmxM3yESK84r1otSg-aQcVStkRhA-iCM8",
    }
)
# The enc_key will be derived in decode() with priv_key and
# the sender's public key which is conveyed as the recipient
# information structure in the COSE Encrypt message (encoded).
assert b"Hello world!" == ctx.decode(encoded, priv_key, context={"alg": "HS256"})
```

#### Key Agreement with Key Wrap for MAC


```py
from cwt import COSE, COSEKey, Recipient

# The sender side:
mac_key = COSEKey.from_symmetric_key(alg="HS256")
r = Recipient.from_jwk(
    {
        "kty": "EC",
        "alg": "ECDH-SS+A128KW",
        "crv": "P-256",
        "x": "7cvYCcdU22WCwW1tZXR8iuzJLWGcd46xfxO1XJs-SPU",
        "y": "DzhJXgz9RI6TseNmwEfLoNVns8UmvONsPzQDop2dKoo",
        "d": "Uqr4fay_qYQykwcNCB2efj_NFaQRRQ-6fHZm763jt5w",
    }
)
pub_key = COSEKey.from_jwk(
    {
        "kid": "meriadoc.brandybuck@buckland.example",
        "kty": "EC",
        "crv": "P-256",
        "x": "Ze2loSV3wrroKUN_4zhwGhCqo3Xhu1td4QjeQ5wIVR0",
        "y": "HlLtdXARY_f55A3fnzQbPcm6hgr34Mp8p-nuzQCE0Zw",
    }
)
r.apply(mac_key, recipient_key=pub_key, context={"alg": "HS256"})
ctx = COSE.new(alg_auto_inclusion=True)
encoded = ctx.encode_and_mac(
    b"Hello world!",
    key=mac_key,
    recipients=[r],
)

# The recipient side:
priv_key = COSEKey.from_jwk(
    {
        "kid": "meriadoc.brandybuck@buckland.example",
        "kty": "EC",
        "crv": "P-256",
        "alg": "ECDH-SS+A128KW",
        "x": "Ze2loSV3wrroKUN_4zhwGhCqo3Xhu1td4QjeQ5wIVR0",
        "y": "HlLtdXARY_f55A3fnzQbPcm6hgr34Mp8p-nuzQCE0Zw",
        "d": "r_kHyZ-a06rmxM3yESK84r1otSg-aQcVStkRhA-iCM8",
    }
)
assert b"Hello world!" == ctx.decode(encoded, priv_key, context={"alg": "HS256"})
```


### COSE Encrypt0

Create a COSE Encrypt0 message, verify and decode it as follows:

```py
from cwt import COSE, COSEKey

enc_key = COSEKey.from_symmetric_key(alg="ChaCha20/Poly1305", kid="01")
ctx = COSE.new(alg_auto_inclusion=True, kid_auto_inclusion=True)
encoded = ctx.encode_and_encrypt(b"Hello world!", enc_key)
decoded = ctx.decode(encoded, enc_key)
```

### COSE Encrypt

#### Direct Key Distribution for encryption

The direct key distribution shares a MAC key between the sender and the recipient that is used directly.
The follwing example shows the simplest way to make a COSE MAC message, verify and decode it with the direct
key distribution method.

```py
from cwt import COSE, COSEKey, Recipient

enc_key = COSEKey.from_symmetric_key(alg="ChaCha20/Poly1305", kid="01")

# The sender side:
nonce = enc_key.generate_nonce()
r = Recipient.from_jwk({"alg": "direct"})
r.apply(enc_key)
ctx = COSE.new()
encoded = ctx.encode_and_encrypt(
    b"Hello world!",
    enc_key,
    nonce=nonce,
    recipients=[r],
)

# The recipient side:
assert b"Hello world!" == ctx.decode(encoded, enc_key)
```

#### Direct Key with KDF for encryption


```py
from cwt import COSE, COSEKey, Recipient

shared_material = token_bytes(32)
shared_key = COSEKey.from_symmetric_key(shared_material, kid="01")

# The sender side:
r = Recipient.from_jwk(
    {
        "kty": "oct",
        "alg": "direct+HKDF-SHA-256",
    },
)
enc_key = r.apply(shared_key, context={"alg": "A256GCM"})
ctx = COSE.new(alg_auto_inclusion=True)
encoded = ctx.encode_and_encrypt(
    b"Hello world!",
    key=enc_key,
    recipients=[r],
)
# The recipient side:
assert b"Hello world!" == ctx.decode(encoded, shared_key, context={"alg": "A256GCM"})
```

#### AES Key Wrap for encryption

The AES key wrap algorithm can be used to wrap a MAC key as follows:

```py
from cwt import COSE, COSEKey, Recipient

# The sender side:
r = Recipient.from_jwk(
    {
        "kid": "01",
        "kty": "oct",
        "alg": "A128KW",
        "k": "hJtXIZ2uSN5kbQfbtTNWbg",  # A shared wrapping key
    },
)
enc_key = COSEKey.from_symmetric_key(alg="ChaCha20/Poly1305")
r.apply(enc_key)
ctx = COSE.new(alg_auto_inclusion=True)
encoded = ctx.encode_and_encrypt(b"Hello world!", key=enc_key, recipients=[r])

# The recipient side:
shared_key = COSEKey.from_jwk(
    {
        "kid": "01",
        "kty": "oct",
        "alg": "A128KW",
        "k": "hJtXIZ2uSN5kbQfbtTNWbg",
    },
)
assert b"Hello world!" == ctx.decode(encoded, shared_key)
```

#### Direct Key Agreement for encryption

The direct key agreement methods can be used to create a shared secret. A KDF (Key Distribution Function) is then
applied to the shared secret to derive a key to be used to protect the data.
The follwing example shows a simple way to make a COSE Encrypt message, verify and decode it with the direct key
agreement methods (``ECDH-ES+HKDF-256`` with various curves).

```py
from cwt import COSE, COSEKey, Recipient

# The sender side:
r = Recipient.from_jwk(
    {
        "kty": "OKP",
        "alg": "ECDH-ES+HKDF-256",
        "crv": "X25519",
    },
)
pub_key = COSEKey.from_jwk(
    {
        "kid": "01",
        "kty": "OKP",
        "alg": "ECDH-ES+HKDF-256",
        "crv": "X25519",
        "x": "y3wJq3uXPHeoCO4FubvTc7VcBuqpvUrSvU6ZMbHDTCI",
    }
)
enc_key = r.apply(recipient_key=pub_key, context={"alg": "A128GCM"})
ctx = COSE.new(alg_auto_inclusion=True)
encoded = ctx.encode_and_encrypt(
    b"Hello world!",
    key=enc_key,
    recipients=[r],
)

# The recipient side:
priv_key = COSEKey.from_jwk(
    {
        "kid": "01",
        "kty": "OKP",
        "alg": "ECDH-ES+HKDF-256",
        "crv": "X25519",
        "x": "y3wJq3uXPHeoCO4FubvTc7VcBuqpvUrSvU6ZMbHDTCI",
        "d": "vsJ1oX5NNi0IGdwGldiac75r-Utmq3Jq4LGv48Q_Qc4",
    }
)
assert b"Hello world!" == ctx.decode(encoded, priv_key, context={"alg": "A128GCM"})
```

#### Key Agreement with Key Wrap for encryption

```py
from cwt import COSE, COSEKey, Recipient

# The sender side:
enc_key = COSEKey.from_symmetric_key(alg="A128GCM")
nonce = enc_key.generate_nonce()
r = Recipient.from_jwk(
    {
        "kty": "EC",
        "alg": "ECDH-SS+A128KW",
        "crv": "P-256",
        "x": "7cvYCcdU22WCwW1tZXR8iuzJLWGcd46xfxO1XJs-SPU",
        "y": "DzhJXgz9RI6TseNmwEfLoNVns8UmvONsPzQDop2dKoo",
        "d": "Uqr4fay_qYQykwcNCB2efj_NFaQRRQ-6fHZm763jt5w",
    }
)
pub_key = COSEKey.from_jwk(
    {
        "kid": "meriadoc.brandybuck@buckland.example",
        "kty": "EC",
        "crv": "P-256",
        "x": "Ze2loSV3wrroKUN_4zhwGhCqo3Xhu1td4QjeQ5wIVR0",
        "y": "HlLtdXARY_f55A3fnzQbPcm6hgr34Mp8p-nuzQCE0Zw",
    }
)
r.apply(enc_key, recipient_key=pub_key, context={"alg": "A128GCM"})
ctx = COSE.new(alg_auto_inclusion=True)
encoded = ctx.encode_and_encrypt(
    b"Hello world!",
    key=enc_key,
    nonce=nonce,
    recipients=[r],
)

# The recipient side:
priv_key = COSEKey.from_jwk(
    {
        "kid": "meriadoc.brandybuck@buckland.example",
        "kty": "EC",
        "alg": "ECDH-SS+A128KW",
        "crv": "P-256",
        "x": "Ze2loSV3wrroKUN_4zhwGhCqo3Xhu1td4QjeQ5wIVR0",
        "y": "HlLtdXARY_f55A3fnzQbPcm6hgr34Mp8p-nuzQCE0Zw",
        "d": "r_kHyZ-a06rmxM3yESK84r1otSg-aQcVStkRhA-iCM8",
    }
)
assert b"Hello world!" == ctx.decode(encoded, priv_key, context={"alg": "A128GCM"})
```

### COSE Signature1

Create a COSE Signature1 message, verify and decode it as follows:

```py
from cwt import COSE, COSEKey, Signer

# The sender side:
signer = Signer.new(
    cose_key=COSEKey.from_jwk(
        {
            "kid": "01",
            "kty": "EC",
            "crv": "P-256",
            "x": "usWxHK2PmfnHKwXPS54m0kTcGJ90UiglWiGahtagnv8",
            "y": "IBOL-C3BttVivg-lSreASjpkttcsz-1rb7btKLv8EX4",
            "d": "V8kgd2ZBRuh2dgyVINBUqpPDr7BOMGcF22CQMIUHtNM",
        }
    ),
    protected={"alg": "ES256"},
    unprotected={"kid": "01"},
)
ctx = COSE.new()
encoded = ctx.encode_and_sign(b"Hello world!", signers=[signer])

# The recipient side:
pub_key = COSEKey.from_jwk(
    {
        "kid": "01",
        "kty": "EC",
        "crv": "P-256",
        "x": "usWxHK2PmfnHKwXPS54m0kTcGJ90UiglWiGahtagnv8",
        "y": "IBOL-C3BttVivg-lSreASjpkttcsz-1rb7btKLv8EX4",
    }
)
assert b"Hello world!" == ctx.decode(encoded, pub_key)
```

### COSE Signature

Create a COSE Signature message, verify and decode it as follows:

```py
from cwt import COSE, COSEKey, Signer

# The sender side:
signer = Signer.new(
    cose_key=COSEKey.from_jwk(
        {
            "kid": "01",
            "kty": "EC",
            "crv": "P-256",
            "x": "usWxHK2PmfnHKwXPS54m0kTcGJ90UiglWiGahtagnv8",
            "y": "IBOL-C3BttVivg-lSreASjpkttcsz-1rb7btKLv8EX4",
            "d": "V8kgd2ZBRuh2dgyVINBUqpPDr7BOMGcF22CQMIUHtNM",
        }
    ),
    protected={1: -7},
    unprotected={4: b"01"},
)
ctx = COSE.new()
encoded = ctx.encode_and_sign(b"Hello world!", signers=[signer])

# The recipient side:
pub_key = COSEKey.from_jwk(
    {
        "kid": "01",
        "kty": "EC",
        "crv": "P-256",
        "x": "usWxHK2PmfnHKwXPS54m0kTcGJ90UiglWiGahtagnv8",
        "y": "IBOL-C3BttVivg-lSreASjpkttcsz-1rb7btKLv8EX4",
    }
)
assert b"Hello world!" == ctx.decode(encoded, pub_key)
```
## API Reference

See [Document](https://python-cwt.readthedocs.io/en/stable/api.html).

## Supported CWT Claims

See [Document](https://python-cwt.readthedocs.io/en/stable/claims.html).

## Supported COSE Algorithms

See [Document](https://python-cwt.readthedocs.io/en/stable/algorithms.html).

## Referenced Specifications

Python CWT is (partially) compliant with following specifications:

- [RFC8152: CBOR Object Signing and Encryption (COSE)](https://tools.ietf.org/html/rfc8152)
- [RFC8230: Using RSA Algorithms with COSE Messages](https://tools.ietf.org/html/rfc8230)
- [RFC8392: CBOR Web Token (CWT)](https://tools.ietf.org/html/rfc8392)
- [RFC8747: Proof-of-Possession Key Semantics for CBOR Web Tokens (CWTs)](https://tools.ietf.org/html/rfc8747)
- [RFC8812: COSE and JOSE Registrations for Web Authentication (WebAuthn) Algorithms](https://tools.ietf.org/html/rfc8812)
- [Electronic Health Certificate Specification](https://github.com/ehn-dcc-development/hcert-spec/blob/main/hcert_spec.md)
- [Technical Specifications for Digital Green Certificates Volume 1](https://ec.europa.eu/health/sites/default/files/ehealth/docs/digital-green-certificates_v1_en.pdf)

## Tests

You can run tests from the project root after cloning with:

```sh
$ tox
```

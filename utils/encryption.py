import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# This function will hash the master key
def hashPassword(password):
    # salt for hashing
    salt = b'\x9a\x10\xa4\x8b\xc3y\xa0\xdcy\xd2\xe1\x8a?pu\x81\xab\xce\xf7\x8e\xc7A\xb8\\fC\x06=\x97\xa5(P'
    key = PBKDF2HMAC(algorithm=hashes.SHA1(), salt=salt,
                     iterations=100000, backend=default_backend(), length=32)
    return base64.urlsafe_b64encode(key.derive(password.encode()))

import functools
import logging

# from app.moneykit_client import MoneyKitClient, get_moneykit_client

logger = logging.getLogger(__name__)


class MoneyKitWebHookVerificationError(Exception):
    pass


class MoneyKitWebHookVerifier:
    pass
    # def __init__(self, client: MoneyKitClient) -> None:
    #     # It is recommended that your application caches the public key for a given key ID, but for no more than 24
    #     # hours. This reduces the likelihood of using an expired key to validate incoming webhooks.
    #     # MoneyKit rotates webhook sig keys regularly
    #     self._key_cache = TTLCache[str, dict](maxsize=20, ttl=timedelta(hours=12).total_seconds())
    #     self._client = client

    # def verify_moneykit_webhook(self, verification_token: str | None, request_data: bytes) -> None:
    #     expected_request_data_hash = self.verify_moneykit_webhook_token(verification_token)
    #     hasher = hashlib.sha256()
    #     hasher.update(request_data)
    #     request_data_hash = hasher.hexdigest()

    #     if not hmac.compare_digest(request_data_hash, expected_request_data_hash):
    #         raise MoneyKitWebHookVerificationError(
    #             f"Request content does not match expected hash. {expected_request_data_hash=} {request_data_hash=}"
    #         )

    # def verify_moneykit_webhook_token(self, verification_token: str | None) -> str:
    #     """
    #     Returns
    #         str: SHA256 of the expected request data.
    #     """
    #     if not verification_token:
    #         raise MoneyKitWebHookVerificationError("Invalid MoneyKit verification")

    #     header = jwt.get_unverified_header(verification_token)
    #     alg = header["alg"]
    #     if alg != "ES256":
    #         raise MoneyKitWebHookVerificationError("Only ES256 algorithm is supported")
    #     kid = header["kid"]
    #     key = self._get_key_for_id(kid)

    #     try:
    #         decoded_token = jwt.decode(
    #             verification_token,
    #             key,  # type: ignore
    #             algorithms=["ES256"],
    #             verify=True,
    #             leeway=timedelta(minutes=5),
    #             options={"verify_iat": True},
    #         )
    #         request_body_sha256 = decoded_token["request_body_sha256"]
    #         return request_body_sha256
    #     except jwt.ExpiredSignatureError:
    #         raise MoneyKitWebHookVerificationError("Token has expired.")
    #     except jwt.PyJWTError:
    #         raise MoneyKitWebHookVerificationError("Invalid token")

    # def _get_key_for_id(self, kid: str) -> jwt.algorithms.ECAlgorithm:
    #     if kid not in self._key_cache:
    #         logger.info(f"Refreshing JWKS. Missing {kid}.")
    #         jwks = self._client.get_well_known_jwks()
    #         for jwk in jwks.keys:
    #             self._key_cache[jwk["kid"]] = jwk
    #     else:
    #         logger.info(f"{kid} in cache")

    #     key = self._key_cache[kid]
    #     logger.info(f"Using JWK {kid}")
    #     return jwt.algorithms.ECAlgorithm.from_jwk(key)  # type: ignore


@functools.lru_cache()
def get_verifier(
    # moneykit_client: Annotated[MoneyKitClient, Depends(get_moneykit_client)],
) -> MoneyKitWebHookVerifier:
    return MoneyKitWebHookVerifier(moneykit_client)

import functools
import hashlib
import hmac
import logging
from datetime import datetime, timedelta
from typing import ClassVar

import jwt
import jwt.algorithms
import moneykit
import moneykit.models
from cachetools import TTLCache

from app.settings import get_settings

logger = logging.getLogger("example.mk_client")


@functools.lru_cache
def moneykit_client() -> moneykit.ApiClient:
    """Generates a Bearer token from your client id and secret to access MoneyKit.

    This bearer token will expire. This method does not show regenerating the token on/before expiry for simplicity.

    :returns: An authenticated client
    """
    settings = get_settings()

    # Generate a bearer access token that is valid for 60 minutes.
    # This client _should_ be cached to avoid regenerating a token on every request.
    # The bearer token should be regenerated before expiry or after a `api_error.auth.expired_access_token` error code
    # is returned by a request.

    config = moneykit.Configuration(host=settings.moneykit_url)
    api_client = moneykit.ApiClient(config)

    logger.debug(f"Authenticating to {settings.moneykit_url} as {settings.moneykit_client_id}")
    access_token_api = moneykit.AccessTokenApi(api_client)
    response = access_token_api.generate_access_token(
        client_id=settings.moneykit_client_id,
        client_secret=settings.moneykit_client_secret.get_secret_value(),
        grant_type="client_credentials",
    )

    logger.debug(f"Token will expire in {response.expires_in} seconds")
    api_client.configuration.access_token = response.access_token
    return api_client


class MoneyKitWebHookVerificationError(Exception):
    pass


class MoneyKitWebHookVerifier:
    # It is recommended that your application caches the public key for a given key ID, but for no more than 24
    # hours. This reduces the likelihood of using an expired key to validate incoming webhooks.
    # We rotate webhook sig keys regularly
    _key_cache: ClassVar[TTLCache[str, dict]] = TTLCache(maxsize=20, ttl=timedelta(hours=12).total_seconds())
    # To avoid malicious requests triggering cache invalidations there needs to be some kind of grace time or other
    # logic for determining the validity of the invalidation. This example only allows cache invalidations every 5
    # minutes.
    _cache_refreshed_at: datetime = datetime.min

    def __init__(self, client: moneykit.ApiClient) -> None:
        self._client = client

    def verify_moneykit_webhook_request(self, verification_token: str | None, request_body: bytes) -> None:
        """This verifies the authenticity of an incoming webhook request from moneykit.

        Moneykit supplies a verification token in the header which can be compared with your own computed value using
        the raw request body.

        Args:
            verification_token (str | None): Value from incoming webhook's `MoneyKit-Signature` HTTP header.
            request_body (bytes): Raw incoming webhook request body.

        Raises:
            MoneyKitWebHookVerificationError: For invalid or expired tokens or when the hashes do not match.
        """
        expected_request_body_hash = self.verify_moneykit_webhook_token(verification_token)
        hasher = hashlib.sha256()
        hasher.update(request_body)
        actual_request_body_hash = hasher.hexdigest()

        if not hmac.compare_digest(actual_request_body_hash, expected_request_body_hash):
            raise MoneyKitWebHookVerificationError(
                "Request content does not match expected hash. "
                f"{expected_request_body_hash=} {actual_request_body_hash=}"
            )

    def verify_moneykit_webhook_token(self, verification_token: str | None) -> str:
        """Fetches MoneyKit Json Web Key Set to discover the correct signing key for the verification token via `kid`
        (Key Id) in the JWT header.

        It then uses this key to decode and verfiy the `verification_token`. This token contains the expected SHA256 of
        the request body.

        Returns
            str: SHA256 of the expected request data.
        """
        if not verification_token:
            raise MoneyKitWebHookVerificationError("Invalid MoneyKit verification")

        header = jwt.get_unverified_header(verification_token)
        alg = header["alg"]
        if alg != "ES256":
            raise MoneyKitWebHookVerificationError("Only ES256 algorithm is supported")
        kid = header["kid"]
        key = self._get_key_for_id(kid)

        try:
            decoded_token = jwt.decode(
                verification_token,
                key,
                algorithms=["ES256"],
                verify=True,
                # issuer="https://api.moneykit.com",
                leeway=timedelta(minutes=5),
                options={"verify_iat": True},
            )
            request_body_sha256 = decoded_token["request_body_sha256"]
            return request_body_sha256
        except jwt.ExpiredSignatureError:
            raise MoneyKitWebHookVerificationError("Token has expired.")
        except jwt.PyJWTError:
            raise MoneyKitWebHookVerificationError("Invalid token")

    def _get_key_for_id(self, kid: str) -> jwt.algorithms.ECAlgorithm:
        if kid not in self._key_cache:
            if datetime.now() - timedelta(minutes=5) > self._cache_refreshed_at:
                logger.info(f"Invalidating JWK cache. {kid} not found from previous cache.")
                access_token_api = moneykit.AccessTokenApi(self._client)
                jwks = access_token_api.get_well_known_jwks()
                for jwk in jwks.keys:
                    self._key_cache[jwk["kid"]] = jwk
                self._cache_refreshed_at = datetime.now()
        else:
            logger.info(f"{kid} in cache")

        key = self._key_cache[kid]
        logger.info(f"Using JWK {kid}")
        return jwt.algorithms.ECAlgorithm.from_jwk(key)

# frozen_string_literal: true

require 'digest'
require 'openssl'
require 'active_support/security_utils'
require 'debug'
require 'jwt'
require 'moneykit'


def configure_moneykit_client
  # Generate a bearer access token that is valid for 60 minutes.
  # This client should be cached to avoid regenerating a token on every request.
  # The bearer token should be regenerated before expiry or after a `api_error.auth.expired_access_token` error code
  # is returned by a request.
  MoneyKit.configure do |config|
    # Configure Bearer authorization
    config.host = ENV['MONEYKIT_URL'] || 'https://api.moneykit.com'
  end

  access_token_api = MoneyKit::AccessTokenApi.new
  response =
    access_token_api.generate_access_token(
      {
        grant_type: 'client_credentials',
        client_id: ENV['MONEYKIT_CLIENT_ID'],
        client_secret: ENV['MONEYKIT_CLIENT_SECRET']
      }
    )

  MoneyKit.configure do |config|
    config.access_token = response.access_token
  end
end


class MoneyKitWebHookVerificationError < StandardError
end


class MoneyKitWebHookVerifier
  def verify_moneykit_webhook_request(verification_token, request_body)
    # This verifies the authenticity of an incoming webhook request from moneykit.
    #
    # Moneykit supplies a verification token in the header which can be compared with your own computed value using
    # the raw request body.
    #
    # :verification_token: Value from incoming webhook's `MoneyKit-Signature` HTTP header.
    # :request_body: Raw incoming webhook request body.
    expected_request_body_hash = self.verify_moneykit_webhook_token(verification_token)
    actual_request_body_hash = Digest::SHA256.hexdigest(request_body)
    raise MoneyKitWebHookVerificationError, "Request content does not match expected hash" unless ActiveSupport::SecurityUtils.secure_compare(actual_request_body_hash, expected_request_body_hash)
  end

  def verify_moneykit_webhook_token(verification_token)
    # Fetches MoneyKit Json Web Key Set to discover the correct signing key for the verification token via `kid`
    # (Key Id) in the JWT header.
    #
    # It then uses this key to decode and verfiy the `verification_token`. This token contains the expected SHA256 of
    # the request body.
    raise MoneyKitWebHookVerificationError, "Invalid MoneyKit verification" if verification_token.nil? || verification_token.empty?

    jwks_loader = ->(options) do
      # The jwk loader would fetch the set of JWKs from a trusted source.
      # To avoid malicious requests triggering cache invalidations there needs to be
      # some kind of grace time or other logic for determining the validity of the invalidation.
      # This example only allows cache invalidations every 5 minutes.
      if options[:kid_not_found] && @cache_last_update < Time.now.to_i - 300
        puts("Invalidating JWK cache. #{options[:kid]} not found from previous cache")
        @cached_keys = nil
      end
      @cached_keys ||= begin
        @cache_last_update = Time.now.to_i
        # Fetch moneykit jwks
        access_token_api = MoneyKit::AccessTokenApi.new
        response = access_token_api.get_well_known_jwks()
        jwks = JWT::JWK::Set.new(response.to_hash)
        jwks.select! { |key| key[:use] == 'sig' } # Signing Keys only
        jwks
      end
    end

    begin
      # Basic verification using loaded JWKs. You can choose to verify other properties such as issuer and issued at.
      decoded_token = JWT.decode(verification_token, nil, true, algorithms: ["ES256"], jwks: jwks_loader)
      payload = decoded_token[0]
      request_body_sha256 = payload['request_body_sha256']
      return request_body_sha256
    rescue JWT::DecodeError => e
      puts "Decode failed: #{e}"
      raise MoneyKitWebHookVerificationError, "Invalid MoneyKit verification"
    end
  end
end

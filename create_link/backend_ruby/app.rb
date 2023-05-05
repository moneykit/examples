require "sinatra"
require "moneykit"
require 'debug'

set :port, 8000
set :bind, '0.0.0.0'
set :default_content_type, 'application/json'

def create_moneykit_client
  # Generate a bearer access token that is valid for 60 minutes.
  # This client should be cached to avoid regenerating a token on every request.
  # The bearer token should be regenerated before expiry or after a `api_error.auth.expired_access_token` error code
  # is returned by a request.
  configuration = MoneyKit::Configuration.new
  configuration.server_index = nil
  configuration.host = ENV["MONEYKIT_URL"]
  unauthenticated_client = MoneyKit::ApiClient.new(configuration)

  access_token_client = MoneyKit::AccessTokenApi.new(unauthenticated_client)
  response =
    access_token_client.generate_access_token(
      {
        grant_type: "client_credentials",
        client_id: ENV["MONEYKIT_CLIENT_ID"],
        client_secret: ENV["MONEYKIT_CLIENT_SECRET"]
      }
    )

  configuration.access_token = response.access_token
  api_client = MoneyKit::ApiClient.new(configuration)
  api_client
end

def moneykit_client
  @mk_client ||= begin
    create_moneykit_client
  end
end

get "/health-check" do
  { project: "create_link/backend_ruby" }.to_json
end

post "/linking/session" do
  link_session_api = MoneyKit::LinkSessionApi.new(moneykit_client)
  response = link_session_api.create_link_session(
    MoneyKit::CreateLinkSessionRequest.new({
      customer_user: MoneyKit::CustomerUser.new({id: "examples-create_link-test-user"}),
      link_tags: ["examples:create_link"],
      settings: MoneyKit::LinkSessionSettingOverrides.new({
        link_permissions: MoneyKit::LinkPermissions.new({
          requested: [
            MoneyKit::RequestedLinkPermission.new({scope: "accounts", reason: "play with MoneyKit examples.", required: true}),
            MoneyKit::RequestedLinkPermission.new({scope: "account_numbers", reason: "play with MoneyKit examples.", required: true}),
            MoneyKit::RequestedLinkPermission.new({scope: "identity", reason: "play with MoneyKit examples.", required: true}),
            MoneyKit::RequestedLinkPermission.new({scope: "transactions", reason: "play with MoneyKit examples.", required: true}),

          ]
        }),
        products: MoneyKit::ProductsSettings.new({
          account_numbers: MoneyKit::AccountNumbersProductSettings.new({
            required: false,
            prefetch: true,
          })

        }),

      })
    })
  )

  status 201
  { link_session_token: response.link_session_token }.to_json
end

post "/linking/exchange-token" do
  request.body.rewind
  data = JSON.parse request.body.read
  exchangeable_token = data["exchangeable_token"]

  link_session_api = MoneyKit::LinkSessionApi.new(moneykit_client)
  response = link_session_api.exchange_token(
    MoneyKit::ExchangeTokenRequest.new({exchangeable_token: exchangeable_token})
  )

  status 202
  { moneykit_link_id: response.link_id, institution_name: response.link.institution_name }.to_json
end

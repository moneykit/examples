# frozen_string_literal: true

require 'sinatra'
require 'moneykit'
require 'debug'

set :port, 8000
set :bind, '0.0.0.0'
set :default_content_type, 'application/json'

def create_moneykit_client
  configuration = MoneyKit::PlaidCompatible::Configuration.new
  configuration.server_index =MoneyKit::PlaidCompatible::Configuration::Environment["sandbox"]
  unauthenticated_client = MoneyKit::ApiClient.new(configuration)

  configuration.api_key["PLAID-CLIENT-ID"] = ENV["MONEYKIT_CLIENT_ID"]
  configuration.api_key["PLAID-SECRET"] = ENV["MONEYKIT_CLIENT_SECRET"]
  configuration.api_key["Plaid-Version"] = "2020-09-14"

  api_client = MoneyKit::PlaidCompatible::ApiClient.new(configuration)
  client = MoneyKit::PlaidCompatible::PlaidApi.new(api_client)
  client
end

def moneykit_client
  @moneykit_client ||= create_moneykit_client
end

get '/health-check' do
  { project: 'create_link/backend_ruby_plaid' }.to_json
end

post '/linking/session' do
  link_session_api = MoneyKit::LinkSessionApi.new(moneykit_client)

  response = moneykit_client.link_token_create(
    MoneyKit::PlaidCompatible::LinkTokenCreateRequest.new(
      {
        user: {
          client_user_id: "examples-create_link-test-user"
        },
        client_name: "MoneyKit Create Link Example",
        products: ["transactions"],
        country_codes: ["US"],
        language: "en",
      }
    )
  )

  status 201
  { link_session_token: response.link_token }.to_json
end

post '/linking/exchange-token' do
  request.body.rewind
  data = JSON.parse request.body.read
  exchangeable_token = data['exchangeable_token']

  response = moneykit_client.item_public_token_exchange(
    MoneyKit::PlaidCompatible::ItemPublicTokenExchangeRequest.new({ public_token: exchangeable_token })
  )
  access_token = response.access_token
  puts("MoneyKit link id: #{response.item_id}, access token: #{response.access_token}")

  item_response = moneykit_client.item_get(
    MoneyKit::PlaidCompatible::ItemGetRequest.new({ access_token: access_token })
  )
  item = item_response.item
  institution_id = item.institution_id
  # TODO: Fetch institution name

  status 202
  { moneykit_link_id: response.access_token, institution_name: institution_id }.to_json
end

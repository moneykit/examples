# frozen_string_literal: true

require "bundler/setup"
require 'sinatra'
require 'sinatra/cors'
require 'moneykit'
require 'debug'

set :port, 8000
set :bind, '0.0.0.0'
set :default_content_type, 'application/json'

# CORS
set :allow_origin, "*"
set :allow_methods, "GET,HEAD,POST"
set :allow_headers, "content-type"

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
    access_token_api.create_access_token(
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

configure_moneykit_client()

get '/health-check' do
  { project: 'create_link/backend/ruby' }.to_json
end

post '/linking/session' do
  # Create a link session. This example shows overriding default settings and products.
  link_session_api = MoneyKit::LinkSessionApi.new
  response = link_session_api.create_link_session(
    MoneyKit::CreateLinkSessionRequest.new(
      {
        customer_user: { id: 'examples-create_link-test-user' },
        link_tags: ['examples:create_link'],
        redirect_uri: ENV['FRONTEND_OAUTH_REDIRECT_URI'] || 'http://localhost:3000',
        settings: {
          products: {
            transactions: {
              required: true,
            }
          }
        }
      }
    )
  )

  status 201
  { link_session_token: response.link_session_token }.to_json
end

post '/linking/exchange-token' do
  # Exchange the Connect SDK's response for a link_id

  request.body.rewind
  data = JSON.parse request.body.read
  exchangeable_token = data['exchangeable_token']

  link_session_api = MoneyKit::LinkSessionApi.new
  response = link_session_api.exchange_token(
    MoneyKit::ExchangeTokenRequest.new({ exchangeable_token: exchangeable_token })
  )

  status 202
  { moneykit_link_id: response.link_id, institution_name: response.link.institution_name }.to_json
end

delete '/links/:link_id' do
  # Delete a link.
  request.body.rewind
  data = JSON.parse request.body.read
  link_id = params['link_id']

  links_api = MoneyKit::LinksApi.new
  links_api.disconnect(link_id)

  status 200
  { }.to_json
end

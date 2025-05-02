# frozen_string_literal: true

require 'securerandom'
require 'json'
require 'sinatra'
require 'sinatra/cors'
require 'moneykit'
require 'debug'
require './lib/client'
require './lib/ngrok'

set :port, 8000
set :bind, '0.0.0.0'
set :default_content_type, 'application/json'

# CORS
set :allow_origin, "*"
set :allow_methods, "GET,HEAD,POST"
set :allow_headers, "content-type"

configure_moneykit_client()

get '/health-check' do
  { project: 'use_webhooks/backend/ruby' }.to_json
end

post '/linking/session' do
  # Create a new link session with a webhook url set to this locally running backend.
  # nrgrok is exposing this local service publically so that moneykit.com can send a webhook event.
  link_session_api = MoneyKit::LinkSessionApi.new

  # Hint: When deployed you would fetch the url from an environment variable.
  # Do not run ngrok in production-like environments
  backend_url = get_ngrok_tunnel_to_backend()
  webhook_url = "#{backend_url}/webhook-handler"
  puts("webhook_url=#{webhook_url}")
  puts('Navigate to http://localhost:4040/inspect/http to view incoming webhook traffic')

  response = link_session_api.create_link_session(
    MoneyKit::CreateLinkSessionRequest.new(
      {
        customer_user: { id: 'examples-use_webhooks-test-user' },
        link_tags: ['examples:use_webhooks'],
        redirect_uri: ENV['FRONTEND_OAUTH_REDIRECT_URI'] || 'http://localhost:3000',
        webhook: webhook_url,
      }
    )
  )

  status 201
  { link_session_token: response.link_session_token }.to_json
end

post '/linking/exchange-token' do
  # Exchange the Connect SDK's response for a link_id.

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
  links_api.delete_link(link_id)

  status 200
  { }.to_json
end

post '/links/:link_id/refresh/:product' do
  # Request a product refresh for a link.
  request.body.rewind
  data = JSON.parse request.body.read
  link_id = params['link_id']
  product = params['product']

  products_api = MoneyKit::ProductsApi.new
  products_api.refresh_products(link_id, { products => [product] })

  status 200
  { }.to_json
end

post '/links/:link_id/webhooks/test/state-changed' do
  # Trigger a test `link.state_changed` webhook event to be sent by moneykit.
  # NOTE: This only works for sandbox links
  request.body.rewind
  data = JSON.parse request.body.read
  link_id = params['link_id']

  # You should see this value in the incoming webhook handler
  idempotency_key = SecureRandom.uuid

  webhooks_api = MoneyKit::WebhooksApi.new
  webhooks_api.trigger_test_link_webhook_event(link_id, {
    webhook_event: 'link.state_changed',
    webhook_idempotency_key: idempotency_key
  })

  puts("Triggered test link.state_changed webhook idempotency_key=#{idempotency_key}")

  status 200
  { idempotency_key: idempotency_key }.to_json
end

post '/links/:link_id/webhooks/test/product-refresh' do
  # Trigger a test `link.product_refresh` webhook event for `accounts` product to be sent by moneykit.
  # NOTE: This only works for sandbox links
  request.body.rewind
  data = JSON.parse request.body.read
  link_id = params['link_id']

  # You should see this value in the incoming webhook handler
  idempotency_key = SecureRandom.uuid

  webhooks_api = MoneyKit::WebhooksApi.new
  webhooks_api.trigger_test_link_webhook_event(link_id, {
    webhook_event: 'link.product_refresh',
    webhook_idempotency_key: idempotency_key
  })

  puts("Triggered test link.product_refresh webhook idempotency_key=#{idempotency_key}")

  status 200
  { idempotency_key: idempotency_key }.to_json
end

post '/links/:link_id/webhooks/test/transactions-updates' do
  # Trigger a test `transactions.updates_available` webhook event for product to be sent by moneykit.
  # NOTE: This only works for sandbox links
  request.body.rewind
  data = JSON.parse request.body.read
  link_id = params['link_id']

  # You should see this value in the incoming webhook handler
  idempotency_key = SecureRandom.uuid

  webhooks_api = MoneyKit::WebhooksApi.new
  webhooks_api.trigger_test_link_webhook_event(link_id, {
    webhook_event: 'transactions.updates_available',
    webhook_idempotency_key: idempotency_key
  })

  puts("Triggered test transactions.updates_available webhook idempotency_key=#{idempotency_key}")

  status 200
  { idempotency_key: idempotency_key }.to_json
end

post '/webhook-handler' do
  # Verifies and handles incoming moneykit webhooks.
  #
  # This method should do the least amount of work possible and respond in a timely manner.
  # Here we pseudocode triggering sidekiq background jobs to do the work once the webhook has been verified and decoded.
  #
  # `moneykit_delivery_token` and `moneykit_delivery_attempt` can be used to help debug requests and are valuable to
  # include in your backend logs.

  moneykit_signature = request.env['HTTP_MONEYKIT_SIGNATURE']
  moneykit_delivery_token = request.env['HTTP_MONEYKIT_DELIVERY_TOKEN']
  moneykit_delivery_attempt = request.env['HTTP_MONEYKIT_DELIVERY_ATTEMPT']
  puts "Handling webhook moneykit_delivery_token=#{moneykit_delivery_token}(#{moneykit_delivery_attempt}) moneykit_signature#{moneykit_signature}"

  body_data = request.body.read

  begin
    verifier = MoneyKitWebHookVerifier.new
    verifier.verify_moneykit_webhook_request(moneykit_signature, body_data)
  rescue MoneyKitWebHookVerificationError => e
    puts e
    status 400
    return { handled: false }.to_json
  end

  body = JSON.parse(body_data)

  webhook_event = body['webhook_event']
  case webhook_event
  when 'link.state_changed'
    payload = MoneyKit::LinkStateChangedWebhook.new(body)
    puts payload
    # Next step: start a background job to update the saved link state
    # UpdateLinkState.perform_async(payload.link_id)
  when 'link.product_refresh'
    payload = MoneyKit::LinkProductRefreshWebhook.new(body)
    puts payload
    # Next step: start a background job that performs whatever you need after your product has updated
    # UpdateLinkState.perform_async(payload.link_id)
  when 'transactions.updates_available'
    payload = MoneyKit::TransactionUpdatesAvailableWebhook.new(body)
    puts payload
    # Next step: start a background job that syncs the latest transactions for this link
    # SyncTransactions.perform_async(payload.link_id)
  else
    puts "Unhandled webhook event #{webhook_event}"
  end
end


# class UpdateLinkState
#   include Sidekiq::Job

#   def perform(link_id)
#     # Pseudo code to fetch and store the latest link state in your database
#     link = db.get_link(link_id)
#     links_api = moneykit.LinksApi.new
#     response = links_api.get_link(link_id)
#     link.moneykit_state = response.state
#     link.moneykit_error = response.error_code
#     link.moneykit_error_message = response.error_message
#     db.commit()
#   end
# end


# class SyncTransactions
#   include Sidekiq::Job

#   def perform(link_id)
#     # Pseudo code background task to sync transactions to your database
#     link = db.get_link(link_id)
#     transactions_api = moneykit.TransactionsApi.new
#     response = transactions_api.get_transactions_sync(link_id, cursor=link.transaction_sync_cursor)
#     # See `cache_transactions/ruby` example for how this works
#   end
# end

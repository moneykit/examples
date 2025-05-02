# Use Webhooks Example

This is is a more complex example which shows how you can verify and handle incoming MoneyKit webhook events.

In order to use webhooks, when creating a Link Session you must include a `webhook` url that points to an endpoint on
your backend API.

The included frontend is the same as the `create_link` frontend and does not contain any specific webhook functionality.

The backend is responsible for generating a Link Session with a `webhook` url, refreshing products, triggering test
webhooks (sandbox links only) and handling the incoming webhooks from MoneyKit.

## Getting started

Choose the language for your backend:
- python: Uses MoneyKit's Python SDK
- ruby: Uses MoneyKit's Ruby SDK

The backend will run on `http://localhost:8000`.

### Set up ngrok an account

In order for webhooks to work, the url must be reachable my MoneyKit. We use [ngrok](https://ngrok.com/) to set up a
tunnel that exposes the backend docker container on a public url. As of writing ngrok does not require an `authtoken`
but they do have plans to make it mandatory so you may need to create an account.

*If you are not comfortable with this, you should host the example with a publically reachable domain name and remove the
ngrok setup.*

Please follow ngrok's instructions to generate an `authtoken`. You will need to add this value to your `.env` file.

### Set your environment variables

Copy `.env.sample` to `create_link/.env`.

Set your `MONEYKIT_CLIENT_ID`, `MONEYKIT_CLIENT_SECRET` and `NGROK_AUTHTOKEN` in the `.env` file.
MoneyKit recommends you use your sandbox keys to play around with test institutions.

If you already have ngrok setup locally you can find the location of your `ngrok.yml` by running
```sh
ngrok config check
```

This will print the location where you can copy the `authtoken` value.

### Create a Link with webhooks

Start any backend, here we'll use python but it doesn't matter.
```sh
make run backend=python
make run backend=ruby
```

Navigate to http://localhost:3000 and to launch the Connect SDK and connect to sandbox.
This will allow you to create a link that has webhooks configured.

Once complete, you should see your first webhook logged on the backend. This is for the `link.state_changed` event
which should show that the link is in a connected state.

### Triggering other webhook events

With a sandbox link you can use the our [`/webhooks/test/link/{link_id}`](https://docs.moneykit.com/webhooks/test-link-event)
API to generate a fake event for various products:
- `link.state_changed`
- `link.product_refreshed`
- `transactions.updates_available`

The backend exposes 3 APIs you can `curl` or use postman to trigger:
- `POST` `http://localhost:8000/links/LINK_ID/webhooks/test/state-changed`
- `POST` `http://localhost:8000/links/LINK_ID/webhooks/test/product-refresh`
- `POST` `http://localhost:8000/links/LINK_ID/webhooks/test/transactions-updates`

With each of these you should see new webhook events logged.

For non-sandbox links you can request real product refreshes to trigger webhook events. Be aware you may be charged for
on-demand product refreshes. You can also delete the link to trigger a state change, but this will make the link
unusable.

- `POST http://localhost:8000/links/LINK_ID/refresh/accounts`
- `POST http://localhost:8000/links/LINK_ID/refresh/account_numbers`
- `POST http://localhost:8000/links/LINK_ID/refresh/transactions`
- `POST http://localhost:8000/links/LINK_ID/refresh/identity`
- `DELETE http://localhost:8000/links/LINK_ID/`


## Handling Webhook Payloads

Due to the nature of exposing a public endpoint on your backend API, we provide a way of verifying that the request
did originate from MoneyKit.

Our webhook payloads do not contain any sensitive information.

### Payload format

All webhooks have a common set of keys:
- `webhook_event`: This is primary discriminator for the type of payload. E.g. `links.state_changed`
- `webhook_major_version`: This indicates the payload schema's major version number. Changes in this indicate a breaking
    change to the payload.
- `webhook_minor_version`: This indicates the payload schema's minor version number. Changes in this indicate a
    backwards compatible change to the payload (e.g. a new field added).
- `webhook_timestamp`: The server timestamp when this payload was generated. This value is not regenerated for retries.
- `webhook_idempotency_key`: An opaque value that can be used to deduplicate webhook events. See below for more details.

### Verifying webhook payloads

MoneyKit signs the webhook payloads and includes a JWT for you to verify the origin of the request.

We make the public key used to sign the JWT available as a Json Web Key Set [`/.well-known/jwks.json`](https://docs.moneykit.com/authentication/json-web-key-set).

The steps to verify a request are:
1. Grab the JWT from `MoneyKit-Signature` HTTP header.
2. Fetch and cache the JWKS from `/.well-known/jwks.json`
3. Extract the `kid` (key id) from JWT's header.
4. Look up the public key from the JWKS using `kid`.
5. Decode and verify the `MoneyKit-Signature` JWT using the key above.
6. Compute the SHA256 of the request body.
7. Compare `decoded_jwt['request_body_sha256'] == computed_request_body_sha256`
8. If the JWT fails verification with the key or the computed SHA256 does not match the value in the JWT the request
    must be ignored.

You should cache the JWKS response for at most 24 hours to avoid making too many requests. We regularly rotate the keys
used to sign the JWT and include the previous `kid` temporarily for backwards compatibility.

### Handling delayed / repeated webhook payloads
Webhooks can be delayed, retried or executed in a non-deterministic order which means you may see an old state.
MoneyKit retries webhooks that receive a non-`2XX` HTTP response status several times (with exponential back off).

There are several strategies to mitigate this:
- As a general practice you should take the incoming link_id and use it to fetch the latest data from our API and not
    rely on the state indicated in the payload.
- MoneyKit include a `webhook_idempotency_key` key in each payload body. This unique value is set when the payload is
    generated. The value **is not** regenerated when we retry requests. Therefore you can use this value to throw away
    payloads you have already seen if you keep track of previously seen `webhook_idempotency_key`.
    These values are opaque and only serve as one way to deduplicate webhook events.
- As a general practice you can ignore webhooks with a `webhook_timestamp` that falls outside of an acceptable time
    window. The value **is not** regenerated when we retry requests.

### Debugging

Included in each webhook request is a `MoneyKit-Delivery-Token` and `MoneyKit-Delivery-Attempt` HTTP header.
You should log this value out in your handler to help debug webhook issues.

You can provide MoneyKit support with a `MoneyKit-Delivery-Token` to aid our debugging process.

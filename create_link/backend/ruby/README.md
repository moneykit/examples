# Create Link Backend

This backend is a minimal example Sinatra app required to create a Link and obtain the `link_id` for later use in other
API calls or testing via Postman.

We expose 3 api endpoints for use by any of the frontend examples.

## Endpoints

### New Link Session

This endpoint returns a new Link Session token that is required to launch MoneyKit Connect on the frontend.
```sh
POST /linking/session {}  # empty body
```

Response:
```json
{
    "link_session_token": "sandbox_..."
}
```

### Exchange Token

```sh
POST /linking/exchange-token {
    "exchangeable_token": "..."
}
```
Response:
```json
{
    "moneykit_link_id": "mk_...",
    "institution_name": "Instant Bank"
}
```

### Disconnect Link

This endpoint disconnects a link which will disable all future access to the accounts and stop the data from being
refreshed.

```sh
DEL /links/{link_id}
```

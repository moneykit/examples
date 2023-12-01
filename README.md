# MoneyKit Examples

## Getting started

All the examples have a docker compose set up ready for use out of the box. This will include extra services such as postgres.

For all examples you will need to set up your local environment variables.

1. Copy `.env.sample` to `.env`

   ```sh
   cp .env.sample .env
   ```

2. Update `.env` with your MoneyKit client id and secret.

## Create Link

This example shows the bare minimum to create a link.

**[Create a Link](create_link/README.md)**

1. Create a link session via a backend API.
2. Launch MoneyKit Connect frontend to allow a user to connect a bank account.
   - Visit `http://localhost:3000` in your browser, and create a new link.
3. Exchange a temporary token to a long-lived link id on the backend.

### Get some account data!

Once you have created a Link you can fetch product data.

If you've followed the steps above, created a new link, and clicked Next all the way to the end, you should have been
rewarded with a panel that shows a new `link_id`:

   > **link_id**<br>
   > mk_AfZGwnseamMJQcAWXqk7iL

You can now use our [fetch_products example](fetch_products/README.md), Postman, curl, or any HTTP client to request
accounts, balances, and other data about that link using the MoneyKit API:  https://docs.moneykit.com.
   ```sh
   # create an access_token
   curl --request POST \
   --url 'https://production.moneykit.com/auth/token'
   --header 'accept: application/json'
   --header 'content-type: application/x-www-form-urlencoded'
   --data 'grant_type: client_credentials'
   --data 'client_id: your_client_id'
   --data 'client_secret: your_secret'

   # get accounts
   curl --request GET
   --url 'https://production.moneykit.com/links/YOUR_LINK_ID/accounts'
   --header 'accept: application/json'
   --header 'Authorization: Bearer YOUR_AUTH_TOKEN'
   ```

## Fetch Products

This example shows how to fetch product data for a link that has already been created.

**[Begin fetching product data](fetch_products/README.md)**

It is a CLI tool that can show you raw responses for products such as `accounts`, `account_numbers`, `identity` and
`transactions`.

1. Create a Link using the the above `Create Link` example.
2. Launch the CLI and pass in the `link_id` obtained from step 1 to show product data.


## Cache Transactions

This example shows the most efficient way of caching transactions in a database. This demonstrates use the use of
`/transactions/sync` instead of `/transactions` endpoint to obtain the difference between calls to sync. The response
 includes `created`, `updated` and `removed` entries for transactions that have occurred since the given `cursor`.

 **[Begin using transactions data](cache_transactions/README.md)**

1. Create a Link using the above `Create Link` example. Ensuring you have `transactions` set to `prefetch` for convenience.
2. Launch the CLI and pass in the `link_id` obtained from step 1 to show product data.

## Use Webhooks

This example shows how to configure webhooks when creating a Link and how to verify that a webhook was sent from MoneyKit.

TODO: Publish example

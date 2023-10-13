# MoneyKit Examples

## Getting started

All the examples have a docker compose set up ready for use out of the box. This will include extra services such as postgres or redis.

For all examples you will need to set up your local environment variables.

1. Copy `.env.sample` to `.env`

   ```sh
   cp .env.sample .env
   ```

2. Update `.env` with your MoneyKit client id and secret.

## Create Link

This example shows off the bare minimum to create a link.

1. Create a link session via a backend API.
2. Launch iOS MoneyLink SDK to allow a user to connect a bank account.
3. Exchange a temporary token to a long-lived link id on the backend.

This example has a backend using the `moneykit` Python sdk and another version that uses `httpx` to communicate with the MoneyKit api.

### Getting started

1. Copy the `.env` you created above to `create_link/.env`

   ```sh
   cp .env create_link/.env
   ```

2. Change directories into `create_link` and launch your preferred backend.

   ```sh
   cd create_link

   docker compose run --rm --service-ports backend-python
   # or
   docker compose run --rm --service-ports backend-python-httpx
   ```

3. At this point, the backend should be running on port 8000 (in docker) and you should see "Uvicorn running on **http://0.0.0.0:8000**".

4. Now launch your preferred frontend:

**iOS:**

1. Open the iOS frontend Xcode project: `create_link/frontend_ios/Create Link.xcodeproj`
2. Build and run the project in the Simulator.
3. Create a new link with the Simulator.

https://user-images.githubusercontent.com/7124846/235194069-e2d65111-1440-4f85-aed0-906c796d314a.mp4

**Web:**

1. In a separate shell, change directories to the frontend web project:

   ```sh
   cd create_link/frontend_web
   ```

2. Install dependencies and start the server.
   ```sh
   npm install
   npm run dev
   ```

3. At this point, the frontend should be running on port 3000 and you should see "Local:  **http://localhost:3000**".

4. Visit `http://localhost:3000` in your browser, and create a new link.

## Get some account data!

If you've followed the steps above, created a new link, and clicked Next all the way to the end, you should have been rewarded with a panel that shows a new `link_id`:

   > **link_id**<br>
   > mk_AfZGwnseamMJQcAWXqk7iL

You can now use Postman, curl, or any HTTP client to request accounts, balances, and other data about that link
using the MoneyKit API:  https://docs.moneykit.com.

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

A tiny demo app is also included which will take your link ID and request your accounts for you (requires Python and Poetry to be installed on your machine).  That app is in the root of the repo.  Install and run it like this:

   ```sh
   poetry install
   # ...installs requirements

   poetry run python show_accounts.py mk_AfZGwnseamMJQcAWXqk7iL
   # prints accounts...
   ```

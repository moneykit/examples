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

1. Copy or symlink your `.env` to `create_link/.env`
    ```sh
    ln -s .env create_link/.env
    ```

2. Launch your preferred backend.
    ```sh
    dcr --rm --service-ports backend-python
    # or
    dcr --rm --service-ports backend-python-httpx
    ```

3. Open the iOS frontend Xcode project: `create_link/frontend_ios/Create Link.xcodeproj`
4. Build and run the project in the Simulator.
5. Create a new link with the Simulator.

https://user-images.githubusercontent.com/7124846/235194069-e2d65111-1440-4f85-aed0-906c796d314a.mp4



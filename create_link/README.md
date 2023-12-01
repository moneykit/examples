# Create Link Example

This is the most basic example that shows how you can create a MoneyKit link with a minimal backend and frontend.

The frontend uses the backend to generate a Link Session, launches MoneyKit Connect with this token and then passes
the response back to the backend.

The backend is responsible for generating a Link Session which is used to initialize the frontend MoneyKit Connect SDK.
It is also responsible for exchanging the Connect SDK response for a `link_id`. With this `link_id` the backend is able
to fetch data such as accounts and disconnect the link.

## Getting started

Choose the language for your backend:
- python: Uses MoneyKit's Python SDK
- python_without_sdk: If you choose to write your own MoneyKit API client, this example shows the requests being made by
    Python's `httpx` HTTP client
- ruby: Uses MoneyKit's Ruby SDK

Chose the language for your frontend:
- iOS: Uses MoneyKit's native iOS Connect SDK
- web: Uses MoneyKit's react Connect SDK
- react_native: Uses MoneyKit's react native Connect SDK

The backend will run on `http://localhost:8000`.

### Set your environment variables

Copy `.env.sample` to `create_link/.env`.

Set your `MONEYKIT_CLIENT_ID` and `MONEYKIT_CLIENT_SECRET` in the `.env` file.
We recommend you use your sandbox keys to play around with test institutions.

### Web Example

Start any backend, here we'll use python but it doesn't matter.
```sh
make run frontend=web
# Options:
# make run backend=python_without_sdk frontend=web
# make run backend=ruby frontend=web
```

Start up the react frontend

```sh
TODO: make run backend=python frontend=web
```

Navigate to http://localhost:TODO and to launch the Connect SDK and connect to sandbox.

### iOS Example

Start any backend, here we'll use python but it doesn't matter.
```sh
make run frontend=ios
# Options:
# make run backend=python_without_sdk frontend=ios
# make run backend=ruby frontend=ios
```

Run the iOS example in the simulator.

1. Open the iOS frontend Xcode project: `create_link/frontend/ios/Create Link.xcodeproj`
2. Build and run the project in the Simulator.
3. Create a new link with the Simulator.

[![iOS Example Video](https://user-images.githubusercontent.com/7124846/235194069-e2d65111-1440-4f85-aed0-906c796d314a.mp4)](https://user-images.githubusercontent.com/7124846/235194069-e2d65111-1440-4f85-aed0-906c796d314a.mp4)


### Android Example

Start any backend, here we'll use python but it doesn't matter.
```sh
make run frontend=android
# Options:
# make run backend=python_without_sdk frontend=android
# make run backend=ruby frontend=android
```

Run the Android example in the emulator.

TODO: Screenshots and instructions

### React Native Example

Start any backend, here we'll use python but it doesn't matter.
```sh
make run frontend=react_native
# Options:
# make run backend=python_without_sdk frontend=react_native
# make run backend=ruby frontend=react_native
```

TODO: Screenshots and instructions


TODO

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


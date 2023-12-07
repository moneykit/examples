# This is only required for demo purposes.
# Here we fetch the opened ngrok tunnel by via `http://ngrok:4040/api/tunnels`
# In a deployed environment the webhook url would be known ahead of time and configured via environment variable.

import functools

import httpx


@functools.cache
def get_ngrok_tunnel_to_backend() -> str:
    # ngrok domain is the name of the service defined in docker-compose.yml
    response = httpx.get("http://ngrok:4040/api/tunnels")
    response.raise_for_status()
    tunnels = response.json()["tunnels"]
    for tunnel in tunnels:
        # find the one tunneling to backend_python:8000
        if tunnel["config"]["addr"] == "http://backend_python:8000":
            return tunnel["public_url"]
    assert False, "No tunnel for http://backend_python:8000 found"

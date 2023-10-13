import os
import httpx
import json
import typer
from dotenv import load_dotenv

load_dotenv()

cli = typer.Typer()


class Client:
    access_token: str = ""
    host = os.environ['MONEYKIT_URL']
    client_id = os.environ['MONEYKIT_CLIENT_ID']
    client_secret = os.environ['MONEYKIT_CLIENT_SECRET']

    def get_access_token(self) -> None:
        resp = self.access_token = httpx.post(
            f"{self.host}/auth/token",
            data=dict(
                client_id=self.client_id,
                client_secret=self.client_secret,
                grant_type="client_credentials"
            )
        )
        return resp.json()["access_token"]

    def get_accounts(self, link_id: str) -> dict:
        if not self.access_token:
            self.get_access_token()
        return httpx.post(
            f"{self.host}/links/{link_id}/accounts",
            headers=dict(
                Authorization=f"Bearer {self.access_token}"
            )
        ).json()


@cli.command()
def show_accounts(link_id: str) -> None:
    accounts = Client().get_accounts(link_id)
    print(json.dumps(accounts, indent=2))


if __name__ == "__main__":
    cli().run()

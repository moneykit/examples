import ky from "ky";
import moneykit from "@moneykit/moneykit";
import type { LinkedInstitution } from "@moneykit/moneykit";

import moneykitLogo from "./assets/moneykit-logo.svg";
import { useState } from "react";

type MoneyKitLinkSessionResponse = {
  link_session_token: string;
};

type MoneyKitExchangeTokenResponse = {
  moneykit_link_id: string;
  institution_name: string;
};

function createLinkSession() {
  return ky
    .post("http://localhost:8000/linking/session")
    .json<MoneyKitLinkSessionResponse>();
}

async function startLink(
  onSuccess: (exchangeableToken: string, institution: LinkedInstitution) => void
) {
  const { link_session_token } = await createLinkSession();
  const mk = new moneykit();
  mk.link(link_session_token, onSuccess);
}

function exchangeToken(token: string) {
  return ky
    .post("http://localhost:8000/linking/exchange-token", {
      json: { exchangeable_token: token },
    })
    .json<MoneyKitExchangeTokenResponse>();
}

function App() {
  const [isLinking, setIsLinking] = useState(false);
  const [moneykitLinkID, setMoneykitLinkID] = useState("");

  const onClickStart = async () => {
    setIsLinking(true);
    startLink(async (exchangeableToken, institution) => {
      const { moneykit_link_id } = await exchangeToken(exchangeableToken);
      setMoneykitLinkID(moneykit_link_id);
      setIsLinking(false);
    });
  };

  return (
    <main className="w-full h-screen flex items-center justify-center bg-gray-200">
      <div className="flex flex-col h-[600px] w-96 border px-4 py-8 shadow bg-white justify-between">
        <img src={moneykitLogo} className="h-12 mb-16" alt="MoneyKit logo" />
        {moneykitLinkID && (
          <div className="font-mono text-white bg-gray-700 p-4 rounded-lg">
            <p className="font-semibold mb-1">link_id</p>
            <p>{moneykitLinkID}</p>
          </div>
        )}
        <button
          onClick={onClickStart}
          className="text-lg rounded-full bg-blue-500 text-white px-4 py-2"
        >
          {isLinking ? "Link In Progress..." : "Start Link"}
        </button>
      </div>
    </main>
  );
}

export default App;

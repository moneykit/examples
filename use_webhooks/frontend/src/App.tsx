import ky from "ky";
import moneykit from "@moneykit/connect";

import moneykitLogo from "./assets/moneykit-logo.svg";
import { useState } from "react";

const BACKEND_URL = 'http://localhost:8000';

type MoneyKitLinkSessionResponse = {
  link_session_token: string;
};

type MoneyKitExchangeTokenResponse = {
  moneykit_link_id: string;
  institution_name: string;
};

function createLinkSession() {
  return ky
    .post(`${BACKEND_URL}/linking/session`)
    .json<MoneyKitLinkSessionResponse>();
}

async function startLink(
  onSuccess: (exchangeableToken: string, institution: object) => void
) {
  const { link_session_token } = await createLinkSession();
  const mk = new moneykit();
  mk.link(link_session_token, onSuccess);
}

function exchangeToken(token: string) {
  return ky
    .post(`${BACKEND_URL}/linking/exchange-token`, {
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
    <main className="flex items-center justify-center w-full h-screen bg-gray-200">
      <div className="flex flex-col h-[600px] w-96 border px-4 py-8 shadow bg-white justify-between">
        <img src={moneykitLogo} className="h-12 mb-16" alt="MoneyKit logo" />
        {moneykitLinkID && (
          <div className="p-4 font-mono text-white bg-gray-700 rounded-lg">
            <p className="mb-1 font-semibold">link_id</p>
            <p>{moneykitLinkID}</p>
          </div>
        )}
        <button
          onClick={onClickStart}
          className="px-4 py-2 text-lg text-white bg-blue-500 rounded-full"
        >
          {isLinking ? "Link In Progress..." : "Start Link"}
        </button>
      </div>
    </main>
  );
}

export default App;

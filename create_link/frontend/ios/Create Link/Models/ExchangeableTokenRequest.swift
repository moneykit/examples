import Foundation

struct ExchangeableTokenRequest: ApiResource {
    let exchangeableToken: String
}

struct ExchangeableTokenResponse: ApiResource {
    let moneykitLinkId: String
}

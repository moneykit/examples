import Foundation

final class DemoViewModel {

    // MARK: - Private properties

    private let apiClient: ApiClientType

    // MARK: - Lifecycle

    init(apiClient: ApiClientType = LinkApiClient(environment: .local)) {
        self.apiClient = apiClient
    }

    // MARK: - Internal functions

    func requestLinkSession(completion: @escaping ((Result<String, ApiClientError>) -> Void)) {
        let request = LinkSessionRequest()

        apiClient.post(
            request,
            endpoint: LinkSession.Endpoint.create,
            headers: [:]
        ) { (result: Result<LinkSessionResponse, ApiClientError>) in
            switch result {
            case let .success(response):
                completion(.success(response.linkSessionToken))
            case let .failure(error):
                completion(.failure(error))
            }
        }
    }

    func exchange(token: String, completion: @escaping ((Result<String, ApiClientError>) -> Void)) {
        let request = ExchangeableTokenRequest(exchangeableToken: token)

        apiClient.post(
            request,
            endpoint: LinkSession.Endpoint.exchange,
            headers: [:]
        ) { (result: Result<ExchangeableTokenResponse, ApiClientError>) in
            switch result {
            case let .success(response):
                completion(.success(response.moneykitLinkId))
            case let .failure(error):
                completion(.failure(error))
            }
        }
    }
}

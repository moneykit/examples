import Foundation

final class LinkApiClient: ApiClientType {

    // MARK: - Internal types

    enum HTTPMethod: String {
        case get = "GET"
        case post = "POST"
        case patch = "PATCH"
        case put = "PUT"
        case delete = "DELETE"
    }

    // MARK: - Private properties

    private let rootURL: URL
    private let sessionConfiguration: URLSessionConfiguration
    private let urlSession: URLSession
    private let environment: Environment

    // MARK: - Lifecycle

    init(
        environment: Environment,
        sessionConfiguration: URLSessionConfiguration = .ephemeral,
        sessionDelegate: URLSessionDelegate? = nil
    ) {
        self.environment = environment
        self.rootURL = environment.apiBaseURL
        self.sessionConfiguration = sessionConfiguration

        sessionConfiguration.httpAdditionalHeaders = [
            "Accept": "application/json",
            "Content-Type": "application/json"
        ]

        self.urlSession = URLSession(
            configuration: sessionConfiguration,
            delegate: sessionDelegate,
            delegateQueue: nil
        )
    }

    // MARK: - ApiClient functions

    @discardableResult
    func post<IT: ApiResource, OT: ApiResource>(
        _ resource: IT,
        endpoint: ApiEndpoint,
        headers: [String: String],
        completion: @escaping (Result<OT, ApiClientError>) -> Void
    ) -> ApiRequest? {
        let requestUrl = rootURL.appendingPathComponent(endpoint.rootPath, isDirectory: false)
        var urlComponents = URLComponents(url: requestUrl, resolvingAgainstBaseURL: false)!
        urlComponents.queryItems = endpoint.queryItems
        let url = urlComponents.url!

        do {
            let encoder = JSONEncoder()
            encoder.dateEncodingStrategy = .iso8601
            encoder.keyEncodingStrategy = .convertToSnakeCase
            encoder.outputFormatting = .sortedKeys
            let data = try encoder.encode(resource)

            var urlRequest = URLRequest(url: url)
            urlRequest.httpMethod = HTTPMethod.post.rawValue
            urlRequest.httpBody = data

            headers.forEach {
                urlRequest.addValue($0.value, forHTTPHeaderField: $0.key)
            }

            let request = urlSession.dataTask(for: urlRequest) { data, response, error in
                if let error = error {
                    completion(.failure(ApiClientError.serverError(error)))
                    return
                }

                guard let data = data, !data.isEmpty else {
                    completion(.failure(ApiClientError.noData))
                    return
                }

                do {
                    let decoder = JSONDecoder()
                    decoder.keyDecodingStrategy = .convertFromSnakeCase
                    let resource = try decoder.decode(OT.self, from: data)

                    completion(.success(resource))
                    return
                } catch let parseError {
                    completion(.failure(ApiClientError.decodingError(parseError)))
                    return
                }
            }
            request.resume()

            return request
        } catch let encodingError {
            completion(.failure(ApiClientError.encodingError(encodingError)))
        }

        return nil
    }
}

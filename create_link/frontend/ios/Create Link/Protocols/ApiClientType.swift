import Foundation

protocol ApiClientType {

    @discardableResult
    func post<T: ApiResource>(
        _ resource: T,
        endpoint: ApiEndpoint,
        headers: [String: String],
        completion: @escaping (Result<T, ApiClientError>) -> Void
    ) -> ApiRequest?

    @discardableResult
    func post<IT: ApiResource, OT: ApiResource>(
        _ resource: IT,
        endpoint: ApiEndpoint,
        headers: [String: String],
        completion: @escaping (Result<OT, ApiClientError>) -> Void
    ) -> ApiRequest?
}

extension ApiClientType {
    @discardableResult
    func post<T: ApiResource>(
        _ resource: T,
        endpoint: ApiEndpoint,
        headers: [String: String] = [:],
        completion: @escaping (Result<T, ApiClientError>) -> Void
    ) -> ApiRequest? {
        post(
            resource,
            endpoint: endpoint,
            headers: headers,
            completion: completion
        )
    }

    @discardableResult
    func post<IT: ApiResource, OT: ApiResource>(
        _ resource: IT,
        endpoint: ApiEndpoint,
        headers: [String: String] = [:],
        completion: @escaping (Result<OT, ApiClientError>) -> Void
    ) -> ApiRequest? {
        post(
            resource,
            endpoint: endpoint,
            headers: headers,
            completion: completion
        )
    }
}

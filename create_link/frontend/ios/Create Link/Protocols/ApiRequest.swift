import Foundation

protocol ApiRequest {
    var currentRequest: URLRequest? { get }
    var originalRequest: URLRequest? { get }
    var response: URLResponse? { get }
    func cancel()
    func resume()
}

extension URLSessionDataTask: ApiRequest {}

protocol URLSessionProtocol {
    func dataTask(for url: URL, completionHandler: @escaping (Data?, URLResponse?, Error?) -> Void) -> ApiRequest
    func dataTask(for request: URLRequest, completionHandler: @escaping (Data?, URLResponse?, Error?) -> Void) -> ApiRequest
}

extension URLSession: URLSessionProtocol {
    func dataTask(for url: URL, completionHandler: @escaping (Data?, URLResponse?, Error?) -> Void) -> ApiRequest {
        dataTask(with: url, completionHandler: completionHandler) as ApiRequest
    }

    func dataTask(for request: URLRequest, completionHandler: @escaping (Data?, URLResponse?, Error?) -> Void) -> ApiRequest {
        dataTask(with: request, completionHandler: completionHandler) as ApiRequest
    }
}

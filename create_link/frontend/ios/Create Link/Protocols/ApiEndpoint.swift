import Foundation

protocol ApiEndpoint: CustomStringConvertible {
    var rootPath: String { get }
    var arguments: [String: CustomStringConvertible]? { get }
    var description: String { get }
    var url: URL? { get }
}

extension ApiEndpoint {
    var arguments: [String: CustomStringConvertible]? {
        nil
    }

    var queryItems: [URLQueryItem]? {
        arguments?
            .sorted(by: { $0.key < $1.key })
            .compactMap { URLQueryItem(name: $0.key, value: $0.value.description) }
    }

    var description: String {
        var path = rootPath
        let compactedArgs = arguments?
            .sorted(by: { $0.key < $1.key })
            .compactMap { "\($0.key)=\($0.value)" }.joined(separator: "&")
        if let compactedArgs = compactedArgs {
            path += "?\(compactedArgs)"
        }
        return path
    }

    var url: URL? {
        URL(string: description)
    }
}

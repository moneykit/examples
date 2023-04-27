import Foundation

struct LinkSession {
    enum Endpoint: ApiEndpoint {
        case create
        case exchange

        var rootPath: String {
            switch self {
            case .create:
                return "linking/session"
            case .exchange:
                return "linking/exchange-token"
            }
        }
    }
}

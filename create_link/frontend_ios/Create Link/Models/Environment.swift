import Foundation

enum Environment: String {
    case local
}

extension Environment {
    var apiBaseURL: URL {
        switch self {
        case .local:
            return URL(string: "http://localhost:8000/")!
        }
    }
}

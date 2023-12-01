import Foundation

enum ApiClientError: Error {
    case noData
    case serverError(Error)
    case decodingError(Error)
    case encodingError(Error)
    case unknownApiError(Int)
}

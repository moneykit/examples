import MoneyKit
import UIKit

final class DemoViewController: UIViewController {

    // MARK: - Private properties

    private let viewModel: DemoViewModel

    private var linkHandler: MKLinkHandler?

    private let startLinkButton = ActivityButton()
    private let logoImageView = UIImageView()
    private let connectedView = UIView()

    private let linkValueLabel = CopyableLabel()

    // MARK: - Lifecycle

    init(viewModel: DemoViewModel) {
        self.viewModel = viewModel

        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    // MARK: - UIViewController overrides

    override func viewDidLoad() {
        super.viewDidLoad()

        view.backgroundColor = UIColor.systemBackground

        logoImageView.image = UIImage(named: "MoneyKitLogo")
        logoImageView.tintColor = UIColor.label
        logoImageView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(logoImageView)
        logoImageView.centerYAnchor.activeConstraint(equalTo: view.centerYAnchor)
        logoImageView.centerXAnchor.activeConstraint(equalTo: view.centerXAnchor)

        connectedView.alpha = 0
        connectedView.layer.cornerRadius = 10
        connectedView.layer.borderWidth = 1
        connectedView.layer.borderColor = UIColor.secondarySystemFill.cgColor
        connectedView.backgroundColor = UIColor(white: 0, alpha: 0.8)
        connectedView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(connectedView)
        connectedView.topAnchor.activeConstraint(greaterThanOrEqualTo: view.safeAreaLayoutGuide.topAnchor)
        connectedView.bottomAnchor.activeConstraint(lessThanOrEqualTo: view.safeAreaLayoutGuide.bottomAnchor)
        connectedView.centerYAnchor.activeConstraint(equalTo: view.centerYAnchor)
        connectedView.leadingAnchor.activeConstraint(equalTo: view.leadingAnchor, constant: 24)
        connectedView.trailingAnchor.activeConstraint(equalTo: view.trailingAnchor, constant: -24)

        let linkTitleLabel = UILabel()
        linkTitleLabel.text = "link_id"
        linkTitleLabel.textColor = UIColor.white
        linkTitleLabel.adjustsFontSizeToFitWidth = true
        linkTitleLabel.numberOfLines = 1
        linkTitleLabel.lineBreakMode = .byTruncatingTail
        linkTitleLabel.font = UIFont.monospacedSystemFont(ofSize: 17, weight: .bold)
        linkTitleLabel.translatesAutoresizingMaskIntoConstraints = false
        connectedView.addSubview(linkTitleLabel)
        linkTitleLabel.topAnchor.activeConstraint(equalTo: connectedView.topAnchor, constant: 16)
        linkTitleLabel.leadingAnchor.activeConstraint(equalTo: connectedView.leadingAnchor, constant: 16)
        linkTitleLabel.trailingAnchor.activeConstraint(equalTo: connectedView.trailingAnchor, constant: -16)

        linkValueLabel.textColor = UIColor.white
        linkValueLabel.numberOfLines = 0
        linkValueLabel.lineBreakMode = .byCharWrapping
        linkValueLabel.font = UIFont.monospacedSystemFont(ofSize: 16, weight: .medium)
        linkValueLabel.translatesAutoresizingMaskIntoConstraints = false
        connectedView.addSubview(linkValueLabel)
        linkValueLabel.topAnchor.activeConstraint(equalTo: linkTitleLabel.bottomAnchor, constant: 6)
        linkValueLabel.leadingAnchor.activeConstraint(equalTo: connectedView.leadingAnchor, constant: 16)
        linkValueLabel.trailingAnchor.activeConstraint(equalTo: connectedView.trailingAnchor, constant: -16)
        linkValueLabel.bottomAnchor.activeConstraint(equalTo: connectedView.bottomAnchor, constant: -16)

        startLinkButton.setTitle("Start Link", for: .normal)
        startLinkButton.titleLabel?.font = UIFont.boldSystemFont(ofSize: 18)
        startLinkButton.setTitleColor(UIColor.label, for: .normal)
        startLinkButton.updateColors(backgroundColor: UIColor.systemBlue, foregroundColor: UIColor.white)
        startLinkButton.layer.cornerRadius = 24
        startLinkButton.layer.cornerCurve = .continuous
        startLinkButton.addTarget(self, action: #selector(startLinkTapped(_:)), for: .touchUpInside)
        startLinkButton.clipsToBounds = true
        startLinkButton.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(startLinkButton)
        startLinkButton.leadingAnchor.activeConstraint(equalTo: view.leadingAnchor, constant: 24)
        startLinkButton.trailingAnchor.activeConstraint(equalTo: view.trailingAnchor, constant: -24)
        startLinkButton.heightAnchor.activeConstraint(equalToConstant: 48)
        startLinkButton.bottomAnchor.activeConstraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor)
    }

    // MARK: - Private functions

    private func requestLinkSessionToken() {
        hideConnectedView()

        startLinkButton.startActivityIndicator()

        viewModel.requestLinkSession { [weak self] result in
            guard let self = self else { return }

            DispatchQueue.main.async {
                switch result {
                case let .success(linkSession):
                    self.presentMoneyLink(with: linkSession)
                case .failure:
                    self.presentLinkSessionErrorAlert()
                }

                self.startLinkButton.stopActivityIndicator()
            }
        }
    }

    private func exchnageToken(for linkedInstitution: MKLinkedInstitution) {
        viewModel.exchange(token: linkedInstitution.token.value) { [weak self] result in
            guard let self = self else { return }

            DispatchQueue.main.async {
                switch result {
                case let .success(linkId):
                    self.showConnectedView(with: linkId)
                case .failure:
                    self.presentExchangeErrorAlert(linkedInstitution: linkedInstitution)
                }

                self.startLinkButton.stopActivityIndicator()
            }
        }
    }

    private func showConnectedView(with linkId: String) {
        linkValueLabel.text = linkId

        UIView.animate(withDuration: 0.35) {
            self.logoImageView.alpha = 0
            self.connectedView.alpha = 1
        }
    }

    private func hideConnectedView() {
        UIView.animate(withDuration: 0.35) {
            self.connectedView.alpha = 0
            self.logoImageView.alpha = 1
        }
    }

    private func presentLinkSessionErrorAlert() {
        let message = "Unable to create a link session token."

        let alertController = UIAlertController(title: "Error", message: message, preferredStyle: .alert)
        let action = UIAlertAction(title: "OK", style: .default)

        alertController.addAction(action)

        present(alertController, animated: true)
    }

    private func presentExchangeErrorAlert(linkedInstitution: MKLinkedInstitution) {
        let message = "Couldn't exchange token for \(linkedInstitution.institution.name)."

        let alertController = UIAlertController(title: "Error", message: message, preferredStyle: .alert)
        let action = UIAlertAction(title: "OK", style: .default)

        alertController.addAction(action)

        present(alertController, animated: true)
    }

    private func presentMoneyLink(with linkSessionToken: String) {
        do {
            let configuration = try MKConfiguration(
                sessionToken: linkSessionToken,
                onSuccess: onMoneyLinkSuccess(successType:),
                onExit: onMoneyLinkExit,
                onEvent: onMoneyLinkEvent(event:),
                onError: onMoneyLinkError(error:)
            )

            linkHandler = MKLinkHandler(configuration: configuration)

            let presentationMethod = MKPresentationMethod.modal(presentingViewController: self)
            linkHandler?.presentInstitutionSelectionFlow(using: presentationMethod)
        } catch let error {
            print("Configuration error - \(error.localizedDescription)")
        }
    }

    private func onMoneyLinkSuccess(successType: MKLinkSuccessType) {
        switch successType {
        case let .linked(linkedInstitution):
            exchnageToken(for: linkedInstitution)
        case .relinked:
            print("Relinked")
        @unknown default:
            print("Future MKLinkSuccessType")
        }
    }

    private func onMoneyLinkExit() {
        print("MoneyLink exit")
    }

    private func onMoneyLinkError(error: MKLinkError) {
        print("MoneyLink error: \(error.name)")
    }

    private func onMoneyLinkEvent(event: MKLinkEvent) {
        print("MoneyLink event - \(event.name)")
    }

    @objc private func startLinkTapped(_ sender: UIButton) {
        requestLinkSessionToken()
    }
}

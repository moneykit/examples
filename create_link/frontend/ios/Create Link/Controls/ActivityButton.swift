import Foundation
import UIKit

final class ActivityButton: UIButton {

    // MARK: - Internal types

    enum TapDirection {
        case down
        case up
    }

    // MARK: - Private Properties

    private var currentTapDirection: TapDirection = .up
    private let activityIndicator = UIActivityIndicatorView(style: .medium)

    private var currentTitleText: String?

    // MARK: - UIView overrides

    override init(frame: CGRect) {
        super.init(frame: frame)

        commonInit()
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        super.touchesBegan(touches, with: event)

        if self.isEnabled {
            self.update(tapDirection: .down)
        }
    }

    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        super.touchesMoved(touches, with: event)

        if self.isEnabled {
            if self.isTouchInside {
                self.update(tapDirection: .down)
            } else {
                self.update(tapDirection: .up)
            }
        }
    }

    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        super.touchesEnded(touches, with: event)

        self.update(tapDirection: .up)
    }

    override func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent?) {
        super.touchesCancelled(touches, with: event)

        self.update(tapDirection: .up)
    }

    // MARK: - Internal functions

    func setInsets(
        forContentPadding contentPadding: UIEdgeInsets,
        imageTitlePadding: CGFloat
    ) {
        self.contentEdgeInsets = UIEdgeInsets(
            top: contentPadding.top,
            left: contentPadding.left,
            bottom: contentPadding.bottom,
            right: contentPadding.right + imageTitlePadding
        )

        self.titleEdgeInsets = UIEdgeInsets(
            top: 0,
            left: imageTitlePadding,
            bottom: 0,
            right: -imageTitlePadding
        )
    }

    func updateColors(
        backgroundColor: UIColor,
        foregroundColor: UIColor,
        disabledBackgroundColor: UIColor? = nil,
        disabledForegroundColor: UIColor? = nil
    ) {
        self.backgroundColor = .clear
        self.activityIndicator.color = foregroundColor
        self.tintColor = foregroundColor

        let backgroundColorImage = generateImage(using: backgroundColor)
        setBackgroundImage(backgroundColorImage, for: .normal)

        if let disabledBackgroundColor = disabledBackgroundColor {
            let disabledColorImage = generateImage(using: disabledBackgroundColor)
            setBackgroundImage(disabledColorImage, for: .disabled)
        } else {
            setBackgroundImage(backgroundColorImage, for: .disabled)
        }

        if let attributedTitle = attributedTitle(for: .normal) {
            let mutableAttributedTitle = NSMutableAttributedString(attributedString: attributedTitle)
            mutableAttributedTitle.addAttributes([.foregroundColor: foregroundColor], range: NSMakeRange(0, attributedTitle.length))
            setAttributedTitle(mutableAttributedTitle, for: .normal)

        } else {
            setTitleColor(foregroundColor, for: .normal)
        }

        if let disabledAttributedTitle = attributedTitle(for: .disabled) {
            let mutableDisabledAttributedTitle = NSMutableAttributedString(attributedString: disabledAttributedTitle)
            mutableDisabledAttributedTitle.addAttributes([.foregroundColor: disabledForegroundColor ?? foregroundColor], range: NSMakeRange(0, disabledAttributedTitle.length))
            setAttributedTitle(mutableDisabledAttributedTitle, for: .disabled)

        } else {
            setTitleColor(disabledForegroundColor, for: .disabled)
        }
    }

    func startActivityIndicator() {
        activityIndicator.startAnimating()

        currentTitleText = titleLabel?.text

        setTitle(nil, for: .normal)

        UIView.animate(withDuration: 0.25) {
            self.activityIndicator.isHidden = false
        }
    }

    func stopActivityIndicator() {
        UIView.animate(withDuration: 0.25) {
            self.activityIndicator.stopAnimating()

            self.setTitle(self.currentTitleText, for: .normal)
        }
    }

    // MARK: - Private functions

    private func commonInit() {
        clipsToBounds = true
        adjustsImageWhenDisabled = false
        adjustsImageWhenHighlighted = false

        layer.rasterizationScale = UIScreen.main.scale
        layer.shouldRasterize = true

        activityIndicator.color = UIColor.white
        activityIndicator.tintColor = UIColor.white
        activityIndicator.isHidden = true
        activityIndicator.hidesWhenStopped = true
        activityIndicator.translatesAutoresizingMaskIntoConstraints = false
        addSubview(activityIndicator)
        activityIndicator.centerYAnchor.activeConstraint(equalTo: centerYAnchor)
        activityIndicator.centerXAnchor.activeConstraint(equalTo: centerXAnchor)

        update(tapDirection: .up)
    }

    private func update(tapDirection: TapDirection) {
        guard currentTapDirection != tapDirection else {
            return
        }

        currentTapDirection = tapDirection

        UIView.animate(withDuration: 0.2, delay: 0, usingSpringWithDamping: 1.0, initialSpringVelocity: 0.5, options: [.curveEaseOut]) {
            if tapDirection == .down {
                self.transform = CGAffineTransform(
                    scaleX: 0.96,
                    y: 0.96
                )
            } else {
                self.transform = CGAffineTransform(scaleX: 1, y: 1)
            }
        }
    }

    private func generateImage(using color: UIColor) -> UIImage {
        let format = UIGraphicsImageRendererFormat.preferred()
        format.preferredRange = .extended

        let renderer = UIGraphicsImageRenderer(size: CGSize(width: 1, height: 1), format: format)

        let img: UIImage = renderer.image { ctx in
            color.setFill()
            ctx.fill(CGRect(x: 0, y: 0, width: 1, height: 1))
        }

        return img
    }
}

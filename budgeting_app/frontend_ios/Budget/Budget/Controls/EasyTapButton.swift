import Foundation
import UIKit

class EasyTapButton: UIButton {

    // MARK: - Internal types

    enum TapDirection {
        case down
        case up
    }

    // MARK: - Internal properties

    var touchAreaInsets: UIEdgeInsets

    var onTapDown: ((UIButton) -> Void)?
    var onTapUp: ((UIButton) -> Void)?

    var currentTapDirection: TapDirection = .up

    // MARK: - Lifecycle

    init(touchAreaInsets: UIEdgeInsets = .zero) {
        self.touchAreaInsets = touchAreaInsets
        super.init(frame: .zero)
    }

    required init?(coder: NSCoder) {
        self.touchAreaInsets = .zero

        super.init(coder: coder)
    }

    // MARK: - UIView overrides

    override func point(inside point: CGPoint, with event: UIEvent?) -> Bool {
        return bounds.inset(by: touchAreaInsets).contains(point)
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

    // MARK: - Private functions

    private func update(tapDirection: TapDirection) {
        guard currentTapDirection != tapDirection else {
            return
        }

        currentTapDirection = tapDirection

        UIView.animate(withDuration: 0.2, delay: 0, usingSpringWithDamping: 1.0, initialSpringVelocity: 0.5, options: [.curveEaseOut]) {
            if tapDirection == .down {
                self.onTapDown?(self)
            } else {
                self.onTapUp?(self)
            }
        }
    }
}

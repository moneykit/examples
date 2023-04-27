import Foundation
import UIKit

class CopyableLabel: UILabel {

    // MARK: - Public variables

    override public var canBecomeFirstResponder: Bool {
        get {
            return true
        }
    }

    // MARK: - Lifecyle

    override init(frame: CGRect) {
        super.init(frame: frame)
        commonInit()
    }

    required init?(coder aDecoder: NSCoder) {
        super.init(coder: aDecoder)
        commonInit()
    }

    // MARK: - UILabel overrides

    override func canPerformAction(_ action: Selector, withSender sender: Any?) -> Bool {
        return (action == #selector(copy(_:)))
    }

    override func copy(_ sender: Any?) {
        UIPasteboard.general.string = text
        UIMenuController.shared.showMenu(from: self, rect: self.bounds)
    }

    // MARK: - Private functions

    private func commonInit() {
        isUserInteractionEnabled = true
        addGestureRecognizer(UILongPressGestureRecognizer(
            target: self,
            action: #selector(showMenu(sender:))
        ))
    }

    @objc private func showMenu(sender: Any?) {
        becomeFirstResponder()

        let menu = UIMenuController.shared

        if !menu.isMenuVisible {
            menu.showMenu(from: self, rect: self.bounds)
        }
    }
}

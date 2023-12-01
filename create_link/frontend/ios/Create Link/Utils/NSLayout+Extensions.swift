import Foundation
import UIKit

extension UIView {
    @discardableResult func activeConstraintsForAnchoringTo(boundsOf view: UIView) -> [NSLayoutConstraint] {
        translatesAutoresizingMaskIntoConstraints = false

        return [
            topAnchor.activeConstraint(equalTo: view.topAnchor),
            leadingAnchor.activeConstraint(equalTo: view.leadingAnchor),
            bottomAnchor.activeConstraint(equalTo: view.bottomAnchor),
            trailingAnchor.activeConstraint(equalTo: view.trailingAnchor)
        ]
    }
}

extension NSLayoutConstraint {
    @discardableResult func usingPriority(_ priority: UILayoutPriority) -> NSLayoutConstraint {
        self.priority = priority
        return self
    }

    @discardableResult func usingMultiplier(_ multiplier: CGFloat) -> NSLayoutConstraint {
        guard let firstItem = self.firstItem else {
            fatalError("Can't apply multipler to constraint with nil firstItem")
        }

        let constraint = NSLayoutConstraint(
            item: firstItem,
            attribute: firstAttribute,
            relatedBy: relation,
            toItem: secondItem,
            attribute: secondAttribute,
            multiplier: multiplier,
            constant: constant
        )

        constraint.priority = priority

        NSLayoutConstraint.deactivate([self])
        NSLayoutConstraint.activate([constraint])

        return constraint
    }
}

extension NSLayoutAnchor {
    @objc @discardableResult func activeConstraint(equalTo anchor: NSLayoutAnchor<AnchorType>, constant: CGFloat = 0.0) -> NSLayoutConstraint {
        let constraint = self.constraint(equalTo: anchor, constant: constant)
        constraint.isActive = true
        return constraint
    }

    @objc @discardableResult func activeConstraint(greaterThanOrEqualTo anchor: NSLayoutAnchor<AnchorType>, constant: CGFloat = 0.0) -> NSLayoutConstraint {
        let constraint = self.constraint(greaterThanOrEqualTo: anchor, constant: constant)
        constraint.isActive = true
        return constraint
    }

    @objc @discardableResult func activeConstraint(lessThanOrEqualTo anchor: NSLayoutAnchor<AnchorType>, constant: CGFloat = 0.0) -> NSLayoutConstraint {
        let constraint = self.constraint(lessThanOrEqualTo: anchor, constant: constant)
        constraint.isActive = true
        return constraint
    }
}

extension NSLayoutDimension {
    @objc @discardableResult func activeConstraint(equalToConstant constant: CGFloat = 0.0) -> NSLayoutConstraint {
        let constraint = self.constraint(equalToConstant: constant)
        constraint.isActive = true
        return constraint
    }

    @objc @discardableResult func activeConstraint(greaterThanOrEqualToConstant constant: CGFloat = 0.0) -> NSLayoutConstraint {
        let constraint = self.constraint(greaterThanOrEqualToConstant: constant)
        constraint.isActive = true
        return constraint
    }

    @objc @discardableResult func activeConstraint(lessThanOrEqualToConstant constant: CGFloat = 0.0) -> NSLayoutConstraint {
        let constraint = self.constraint(lessThanOrEqualToConstant: constant)
        constraint.isActive = true
        return constraint
    }
}

extension UILayoutPriority {
    static var almostRequired: UILayoutPriority {
        return UILayoutPriority(rawValue: 999)
    }

    static var high: UILayoutPriority {
        return UILayoutPriority(rawValue: 750)
    }

    static var medium: UILayoutPriority {
        return UILayoutPriority(rawValue: 500)
    }

    static var low: UILayoutPriority {
        return UILayoutPriority(rawValue: 250)
    }

    static var notRequired: UILayoutPriority {
        return UILayoutPriority(rawValue: 0)
    }
}

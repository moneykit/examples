import UIKit

class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    // MARK: - Internal properties

    var window: UIWindow?

    // MARK: - Private properties

    private var demoViewController: DemoViewController!

    // MARK: - UIWindowSceneDelegate functions

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        guard let windowScene = (scene as? UIWindowScene) else { return }

        let windowFromScene = UIWindow(windowScene: windowScene)

        let viewModel = DemoViewModel()
        demoViewController = DemoViewController(viewModel: viewModel)

        windowFromScene.rootViewController = demoViewController
        windowFromScene.backgroundColor = .black
        windowFromScene.makeKeyAndVisible()

        window = windowFromScene
    }

    func sceneDidDisconnect(_ scene: UIScene) { }

    func sceneDidBecomeActive(_ scene: UIScene) { }

    func sceneWillResignActive(_ scene: UIScene) { }

    func sceneWillEnterForeground(_ scene: UIScene) { }

    func sceneDidEnterBackground(_ scene: UIScene) { }
}


import SwiftUI

@main
struct CaisseApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .frame(minWidth: 1000, minHeight: 650)
                .background(Theme.bgMain)
        }
        .windowStyle(HiddenTitleBarWindowStyle())
    }
}

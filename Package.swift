// swift-tools-version: 6.1
import PackageDescription

let package = Package(
    name: "GoalzCore",
    platforms: [
        .iOS(.v17),
        .macOS(.v14),
    ],
    products: [
        .library(
            name: "GoalzCore",
            targets: ["GoalzCore"]
        ),
    ],
    targets: [
        .target(
            name: "GoalzCore",
            path: "Goalz/Shared"
        ),
        .testTarget(
            name: "GoalzCoreTests",
            dependencies: ["GoalzCore"],
            path: "GoalzCoreTests"
        ),
    ]
)

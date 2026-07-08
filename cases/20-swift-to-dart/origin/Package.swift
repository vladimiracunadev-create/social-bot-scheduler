// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "Publisher",
    targets: [
        .executableTarget(name: "Publisher", path: "Sources/Publisher")
    ]
)

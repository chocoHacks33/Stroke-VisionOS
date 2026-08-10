import Foundation
import RealityKit
import CryptoKit

struct EntityRecord: Codable {
    let path: String
    let childIndexPath: [Int]
    let name: String
    let hasModel: Bool
    let materialCount: Int
    let animationCount: Int
    let childCount: Int
}

struct AssetRecord: Codable {
    let assetID: String
    let packageRelativePath: String
    let packageBytes: Int
    let packageSHA256: String
    let entityCount: Int
    let modelCount: Int
    let materialCount: Int
    let animationCount: Int
    let entities: [EntityRecord]
}

struct FailedAsset: Codable {
    let packageRelativePath: String
    let error: String
}

struct EntityMap: Codable {
    let schemaVersion: String
    let generatedWith: String
    let catalogRelativeRoot: String
    let assets: [AssetRecord]
    let failures: [FailedAsset]
}

func sanitizedPathComponent(_ value: String, fallback: String) -> String {
    let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
    return trimmed.isEmpty ? fallback : trimmed.replacingOccurrences(of: "/", with: "_")
}

func relativePath(for file: URL, root: URL) -> String {
    let rootPath = root.standardizedFileURL.path
    let filePath = file.standardizedFileURL.path
    guard filePath.hasPrefix(rootPath + "/") else {
        return file.lastPathComponent
    }
    return String(filePath.dropFirst(rootPath.count + 1))
}

func collectEntities(from root: Entity) -> [EntityRecord] {
    var records: [EntityRecord] = []

    func visit(_ entity: Entity, parentPath: String, childIndexPath: [Int], siblingIndex: Int) {
        let component = sanitizedPathComponent(entity.name, fallback: "unnamed_\(siblingIndex)")
        let path = parentPath.isEmpty ? "/\(component)" : "\(parentPath)/\(component)"
        let model = entity.components[ModelComponent.self]
        records.append(
            EntityRecord(
                path: path,
                childIndexPath: childIndexPath,
                name: entity.name,
                hasModel: model != nil,
                materialCount: model?.materials.count ?? 0,
                animationCount: entity.availableAnimations.count,
                childCount: entity.children.count
            )
        )
        for (index, child) in entity.children.enumerated() {
            visit(
                child,
                parentPath: path,
                childIndexPath: childIndexPath + [index],
                siblingIndex: index
            )
        }
    }

    visit(root, parentPath: "", childIndexPath: [], siblingIndex: 0)
    return records
}

guard CommandLine.arguments.count == 3 else {
    fputs("usage: ExtractRealityKitEntityMap <catalog-root> <output-json>\n", stderr)
    exit(64)
}

let catalogRoot = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true).standardizedFileURL
let outputURL = URL(fileURLWithPath: CommandLine.arguments[2]).standardizedFileURL
let fileManager = FileManager.default

guard let enumerator = fileManager.enumerator(
    at: catalogRoot,
    includingPropertiesForKeys: [.isRegularFileKey, .fileSizeKey],
    options: [.skipsHiddenFiles]
) else {
    fputs("could not enumerate catalog root\n", stderr)
    exit(66)
}

let files = enumerator.compactMap { $0 as? URL }
    .filter { $0.pathExtension.lowercased() == "usdz" }
    .sorted { relativePath(for: $0, root: catalogRoot) < relativePath(for: $1, root: catalogRoot) }

var assets: [AssetRecord] = []
var failures: [FailedAsset] = []

for file in files {
    let packagePath = relativePath(for: file, root: catalogRoot)
    do {
        let root = try Entity.load(contentsOf: file)
        let entities = collectEntities(from: root)
        let bytes = try file.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0
        let digest = SHA256.hash(data: try Data(contentsOf: file, options: .mappedIfSafe))
            .map { String(format: "%02x", $0) }
            .joined()
        let asset = AssetRecord(
            assetID: file.deletingPathExtension().lastPathComponent,
            packageRelativePath: packagePath,
            packageBytes: bytes,
            packageSHA256: digest,
            entityCount: entities.count,
            modelCount: entities.filter(\.hasModel).count,
            materialCount: entities.reduce(0) { $0 + $1.materialCount },
            animationCount: entities.reduce(0) { $0 + $1.animationCount },
            entities: entities
        )
        assets.append(asset)
        fputs("mapped \(asset.assetID): \(asset.entityCount) entities, \(asset.modelCount) models\n", stderr)
    } catch {
        failures.append(FailedAsset(packageRelativePath: packagePath, error: String(describing: error)))
        fputs("failed \(packagePath)\n", stderr)
    }
}

let document = EntityMap(
    schemaVersion: "1.0",
    generatedWith: "RealityKit Entity.load(contentsOf:)",
    catalogRelativeRoot: "RealityKitContent/Assets",
    assets: assets,
    failures: failures
)
let encoder = JSONEncoder()
encoder.outputFormatting = [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes]
let data = try encoder.encode(document)
try fileManager.createDirectory(at: outputURL.deletingLastPathComponent(), withIntermediateDirectories: true)
try data.write(to: outputURL, options: .atomic)

exit(failures.isEmpty ? 0 : 1)

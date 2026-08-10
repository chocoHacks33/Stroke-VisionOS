import RealityKit

/// Applies reversible, geometry-preserving presentation changes to already-loaded
/// entities. Source USDZ files and authored transforms are never mutated.
@MainActor
enum RealityPresentationSidecars {
    private static let emphasisMarkerName = "__StrokeActionEmphasisMarker"

    static func setActionEmphasis(on assetRoot: Entity, enabled: Bool) {
        if let marker = assetRoot.findEntity(named: emphasisMarkerName) {
            marker.isEnabled = enabled
            return
        }
        guard enabled else { return }

        let bounds = assetRoot.visualBounds(recursive: true, relativeTo: assetRoot)
        let extent = max(bounds.extents.x, bounds.extents.y, bounds.extents.z)
        let radius = max(0.002, min(0.02, extent * 0.045))
        let marker = ModelEntity(
            mesh: .generateSphere(radius: radius),
            materials: [UnlitMaterial(color: .init(red: 0.45, green: 0.96, blue: 0.82, alpha: 1))]
        )
        marker.name = emphasisMarkerName
        marker.position = bounds.center + SIMD3<Float>(0, bounds.extents.y * 0.62 + radius, 0)
        assetRoot.addChild(marker)
    }

}

#if canImport(ExperienceCore)
import ExperienceCore
#endif
import SwiftUI

struct AssetLibraryShellView: View {
    @EnvironmentObject private var model: ExperienceShellModel
    @State private var selectedCategory: ExperienceAssetCategory?
    @State private var pageIndex = 0
    @State private var pendingDetachedAsset: ExperienceAssetRecord?
    @State private var lockedAsset: ExperienceAssetRecord?

    private let pageSize = 8

    var body: some View {
        VStack(spacing: 16) {
            header
            categoryStrip

            if let error = model.catalogLoadError {
                ContentUnavailableView(
                    "Asset catalog unavailable",
                    systemImage: "exclamationmark.triangle",
                    description: Text(error)
                )
                .frame(maxHeight: .infinity)
            } else {
                assetGrid
                pagination
            }

            HStack {
                SafetyBadge(compact: true)
                Spacer()
                Text("The library indexes all 150 models. A scene loads only its active teaching set.")
                    .font(.caption)
                    .foregroundStyle(ExperienceTheme.quietText)
            }
            .padding(.horizontal, 28)
            .padding(.bottom, 18)
        }
        .onChange(of: selectedCategory) { pageIndex = 0 }
        .onChange(of: model.assetSearchText) { pageIndex = 0 }
        .confirmationDialog(
            "Open a detached conceptual asset?",
            isPresented: Binding(
                get: { pendingDetachedAsset != nil },
                set: { if !$0 { pendingDetachedAsset = nil } }
            ),
            titleVisibility: .visible
        ) {
            Button("Open developer-preview asset") {
                if let pendingDetachedAsset {
                    model.inspectAsset(id: pendingDetachedAsset.assetID)
                }
                pendingDetachedAsset = nil
            }
            Button("Cancel", role: .cancel) { pendingDetachedAsset = nil }
        } message: {
            Text("This micro-scale view is detached, conceptual, magnified, not to anatomical scale, and not patient-specific.")
        }
        .alert("Asset locked in the default preview", isPresented: Binding(
            get: { lockedAsset != nil },
            set: { if !$0 { lockedAsset = nil } }
        )) {
            Button("OK", role: .cancel) { lockedAsset = nil }
        } message: {
            Text("Open-cranial geometry requires the separately enabled developer flag, an explicit pathway confirmation, and a valid in-session developer authorization.")
        }
    }

    private var header: some View {
        HStack(spacing: 16) {
            Button {
                model.screen = model.selectedCaseID.isEmpty ? .landing : .explore
            } label: {
                Label("Back", systemImage: "chevron.left")
            }

            VStack(alignment: .leading, spacing: 3) {
                Text("Spatial asset library")
                    .font(.largeTitle.bold())
                Text("\(model.catalogAssets.count) release assets · 450 reversible presentation bindings")
                    .font(.callout)
                    .foregroundStyle(ExperienceTheme.quietText)
            }

            Spacer()

            TextField("Search asset IDs", text: $model.assetSearchText)
                .textFieldStyle(.roundedBorder)
                .frame(width: 300)
                .accessibilityHint("Filters metadata only; it does not load the model")

            Button {
                model.assetSearchText = ""
                selectedCategory = nil
            } label: {
                Label("Clear", systemImage: "xmark.circle")
            }

            InteractionFeedbackSettingsButton()
        }
        .padding(.horizontal, 28)
        .padding(.top, 24)
    }

    private var categoryStrip: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 9) {
                categoryButton(title: "All records", category: nil, count: model.accessibleCatalogAssets.count)
                ForEach(ExperienceAssetCategory.allCases, id: \.self) { category in
                    let count = model.accessibleCatalogAssets.lazy.filter { $0.primaryCategory == category }.count
                    if count > 0 {
                        categoryButton(title: shortTitle(for: category), category: category, count: count)
                    }
                }
            }
            .padding(.horizontal, 28)
            .padding(.vertical, 4)
        }
    }

    private var assetGrid: some View {
        LazyVGrid(
            columns: Array(repeating: GridItem(.flexible(), spacing: 12), count: 4),
            spacing: 12
        ) {
            ForEach(currentPage) { asset in
                assetCard(asset)
            }
        }
        .padding(.horizontal, 28)
        .frame(maxHeight: .infinity, alignment: .top)
    }

    private var pagination: some View {
        HStack(spacing: 14) {
            Button {
                pageIndex = max(0, pageIndex - 1)
            } label: {
                Label("Previous", systemImage: "chevron.left")
            }
            .disabled(pageIndex == 0)

            Text("Page \(pageIndex + 1) of \(pageCount) · showing up to \(pageSize) records")
                .font(.caption.monospacedDigit())
                .foregroundStyle(ExperienceTheme.quietText)

            Button {
                pageIndex = min(pageCount - 1, pageIndex + 1)
            } label: {
                Label("Next", systemImage: "chevron.right")
            }
            .disabled(pageIndex >= pageCount - 1)
        }
    }

    private var filteredAssets: [ExperienceAssetRecord] {
        let categoryFiltered = selectedCategory.map { selected in
            model.accessibleCatalogAssets.filter { $0.primaryCategory == selected }
        } ?? model.accessibleCatalogAssets
        let query = model.assetSearchText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !query.isEmpty else { return categoryFiltered }
        return categoryFiltered.filter {
            $0.assetID.localizedCaseInsensitiveContains(query)
                || $0.primaryCategory.rawValue.localizedCaseInsensitiveContains(query)
        }
    }

    private var currentPage: [ExperienceAssetRecord] {
        let offset = pageIndex * pageSize
        return Array(filteredAssets.dropFirst(offset).prefix(pageSize))
    }

    private var pageCount: Int {
        max(1, Int(ceil(Double(filteredAssets.count) / Double(pageSize))))
    }

    private func categoryButton(
        title: String,
        category: ExperienceAssetCategory?,
        count: Int
    ) -> some View {
        Button {
            selectedCategory = category
        } label: {
            HStack(spacing: 7) {
                Text(title)
                Text("\(count)")
                    .font(.caption2.monospacedDigit())
                    .foregroundStyle(selectedCategory == category ? .black.opacity(0.65) : ExperienceTheme.quietText)
            }
        }
        .buttonStyle(.bordered)
        .tint(selectedCategory == category ? ExperienceTheme.mint : .white.opacity(0.28))
        .accessibilityAddTraits(selectedCategory == category ? .isSelected : [])
    }

    private func assetCard(_ asset: ExperienceAssetRecord) -> some View {
        Button {
            if model.isCatalogAssetLocked(asset) {
                lockedAsset = asset
            } else if asset.primaryCategory == .microConceptual {
                pendingDetachedAsset = asset
            } else {
                model.inspectAsset(id: asset.assetID)
            }
        } label: {
            HStack(alignment: .top, spacing: 12) {
                Image(systemName: icon(for: asset.primaryCategory))
                    .font(.title2)
                    .foregroundStyle(ExperienceTheme.mint)
                    .frame(width: 46, height: 46)
                    .background(ExperienceTheme.mint.opacity(0.09), in: RoundedRectangle(cornerRadius: 13))

                VStack(alignment: .leading, spacing: 6) {
                    Text(asset.assetID.replacingOccurrences(of: "_", with: " ").capitalized)
                        .font(.callout.weight(.semibold))
                        .foregroundStyle(.white)
                        .lineLimit(2)
                    Text(shortTitle(for: asset.primaryCategory))
                        .font(.caption2.weight(.bold))
                        .foregroundStyle(ExperienceTheme.mint)
                        .lineLimit(1)
                    HStack(spacing: 7) {
                        Text(asset.compositionKind == .assembly ? "Assembly" : "Component")
                        Text("·")
                        Text(ByteCountFormatter.string(fromByteCount: Int64(asset.sourceUSDZBytes), countStyle: .file))
                    }
                    .font(.caption2)
                    .foregroundStyle(ExperienceTheme.quietText)
                }
                Spacer(minLength: 0)
                if model.isCatalogAssetLocked(asset) {
                    Image(systemName: "lock.fill")
                        .foregroundStyle(ExperienceTheme.amber)
                        .accessibilityLabel("Locked")
                }
            }
            .padding(14)
            .frame(maxWidth: .infinity, minHeight: 116, alignment: .topLeading)
            .experienceGlassPanel(cornerRadius: 20)
        }
        .buttonStyle(.plain)
        .accessibilityLabel("\(asset.assetID), \(shortTitle(for: asset.primaryCategory))")
        .accessibilityHint(
            model.isCatalogAssetLocked(asset)
                ? "Locked until the separate open-cranial developer gate is active"
                : "Selects this model and returns to the teaching stage"
        )
    }

    private func shortTitle(for category: ExperienceAssetCategory) -> String {
        switch category {
        case .adaptivePresentation: "Adaptive presentation"
        case .anatomyCNSMacro: "Brain anatomy"
        case .anatomyHeadNeckSupport: "Head & neck"
        case .anatomyVascular: "Vascular anatomy"
        case .bloodFlowTeaching: "Flow teaching"
        case .clinicalContext: "Clinical context"
        case .compositeAssembly: "Assemblies"
        case .guidance: "Guidance"
        case .microConceptual: "Micro concepts"
        case .openCranialAnatomyState: "Open-state anatomy"
        case .pathologyMacro: "Pathology concepts"
        case .spatialEnvironment: "Environment"
        case .toolsEndovascular: "Endovascular tools"
        case .toolsOpenCranial: "Open-cranial tools"
        }
    }

    private func icon(for category: ExperienceAssetCategory) -> String {
        switch category {
        case .anatomyCNSMacro, .anatomyHeadNeckSupport: "brain.head.profile"
        case .anatomyVascular, .bloodFlowTeaching: "waveform.path.ecg"
        case .toolsEndovascular, .toolsOpenCranial: "cross.case.fill"
        case .clinicalContext, .spatialEnvironment: "building.2.fill"
        case .pathologyMacro: "exclamationmark.circle.fill"
        case .microConceptual: "scope"
        case .guidance, .adaptivePresentation: "slider.horizontal.3"
        case .compositeAssembly, .openCranialAnatomyState: "square.3.layers.3d"
        }
    }
}

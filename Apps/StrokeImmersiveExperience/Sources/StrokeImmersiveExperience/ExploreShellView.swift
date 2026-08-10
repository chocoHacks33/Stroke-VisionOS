import SwiftUI

struct ExploreShellView: View {
    @EnvironmentObject private var model: ExperienceShellModel
    @Environment(\.openImmersiveSpace) private var openImmersiveSpace
    @Environment(\.dismissImmersiveSpace) private var dismissImmersiveSpace
    @State private var immersiveError: String?

    var body: some View {
        VStack(spacing: 14) {
            header
            if !model.isInspectingAsset {
                StepTimelineView(compact: false)
                    .padding(.horizontal, 26)
            }

            HStack(alignment: .top, spacing: 14) {
                TeachingNotesPanel()
                    .frame(width: 258)

                WindowModelStage()
                    .frame(maxWidth: .infinity, maxHeight: .infinity)

                TopicRail()
                    .frame(width: 230)
            }
            .padding(.horizontal, 22)

            controlStrip
                .padding(.horizontal, 22)
                .padding(.bottom, 18)
        }
        .alert("Unable to open the immersive space", isPresented: Binding(
            get: { immersiveError != nil },
            set: { if !$0 { immersiveError = nil } }
        )) {
            Button("OK", role: .cancel) { immersiveError = nil }
        } message: {
            Text(immersiveError ?? "Please try again.")
        }
        .confirmationDialog(
            model.pendingTransitionTitle ?? "Confirm transition",
            isPresented: Binding(
                get: { model.pendingTransitionTitle != nil },
                set: { if !$0 { model.cancelPendingTransition() } }
            ),
            titleVisibility: .visible
        ) {
            Button("Continue to catalogued developer-preview state") {
                model.confirmPendingTransition()
            }
            Button("Stay here", role: .cancel) {
                model.cancelPendingTransition()
            }
        } message: {
            Text("This is a scripted, non-graphic educational state. It is not a surgical simulation, clinical instruction, or patient-specific plan.")
        }
        .alert("Developer preview could not continue", isPresented: Binding(
            get: { model.runtimeError != nil },
            set: { if !$0 { model.clearRuntimeError() } }
        )) {
            Button("OK", role: .cancel) { model.clearRuntimeError() }
        } message: {
            Text(model.runtimeError ?? "Unknown developer-preview error")
        }
    }

    private var header: some View {
        HStack(spacing: 14) {
            Button {
                model.screen = .cases
            } label: {
                Label("Scenarios", systemImage: "chevron.left")
            }

            VStack(alignment: .leading, spacing: 2) {
                Text(model.isInspectingAsset ? "Single-asset inspection" : model.currentStepTitle)
                    .font(.title2.bold())
                Text(model.isInspectingAsset
                     ? "Catalogued developer-preview asset · lesson actions paused"
                     : "\(model.selectedCase.displayLabel) · \(model.procedureState.selectedPathway.rawValue)")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(ExperienceTheme.mint)
            }

            Spacer()

            if model.isInspectingAsset {
                Button {
                    model.exitInspectionMode()
                } label: {
                    Label("Return to lesson", systemImage: "arrow.uturn.backward.circle.fill")
                }
                .buttonStyle(.borderedProminent)
                .tint(ExperienceTheme.mint.opacity(0.72))
            } else {
                ProcedureTransportControls()
            }

            Picker("Explanation style", selection: $model.explanationMode) {
                ForEach(ExplanationMode.allCases) { mode in
                    Text(mode.rawValue).tag(mode)
                }
            }
            .pickerStyle(.segmented)
            .frame(width: 330)

            Button {
                model.screen = .library
            } label: {
                Label("Library", systemImage: "square.grid.3x3")
            }
        }
        .padding(.horizontal, 26)
        .padding(.top, 20)
    }

    private var controlStrip: some View {
        HStack(spacing: 18) {
            SafetyBadge(compact: true)

            Divider().frame(height: 34)

            VStack(alignment: .leading, spacing: 3) {
                Text("Comfort & visual detail")
                    .font(.caption.weight(.semibold))
                Text(model.detailTierTitle)
                    .font(.caption2)
                    .foregroundStyle(ExperienceTheme.mint)
            }

            Slider(value: $model.detailSliderValue, in: 0 ... 1) {
                Text("Visual detail")
            } minimumValueLabel: {
                Image(systemName: "circle")
                    .accessibilityLabel("Calmest visual")
            } maximumValueLabel: {
                Image(systemName: "circle.hexagongrid.fill")
                    .accessibilityLabel("Full detail")
            }
            .tint(ExperienceTheme.mint)
            .frame(maxWidth: 300)
            .accessibilityValue(model.detailTierTitle)
            .accessibilityHint("Explicitly changes the presentation tier. The app never infers anxiety.")

            Text("Selected by you · never inferred")
                .font(.caption2)
                .foregroundStyle(ExperienceTheme.quietText)

            Spacer()

            Button {
                model.isNotesVisible.toggle()
            } label: {
                Label(model.isNotesVisible ? "Hide notes" : "Show notes", systemImage: "note.text")
            }
            .buttonStyle(.bordered)

            Button {
                Task { await toggleImmersiveSpace() }
            } label: {
                Label(
                    model.isImmersiveSpaceOpen ? "Exit immersive view" : "Enter immersive view",
                    systemImage: model.isImmersiveSpaceOpen ? "arrow.down.right.and.arrow.up.left" : "visionpro"
                )
                .font(.headline)
            }
            .buttonStyle(.borderedProminent)
            .tint(model.isImmersiveSpaceOpen ? ExperienceTheme.amber.opacity(0.75) : ExperienceTheme.mint.opacity(0.72))
        }
        .padding(12)
        .experienceGlassPanel(cornerRadius: 22)
    }

    private func toggleImmersiveSpace() async {
        if model.isImmersiveSpaceOpen {
            await dismissImmersiveSpace()
            model.isImmersiveSpaceOpen = false
            return
        }

        switch await openImmersiveSpace(id: ExperienceSpaceID.immersiveStage) {
        case .opened:
            model.isImmersiveSpaceOpen = true
        case .userCancelled:
            break
        case .error:
            immersiveError = "The simulator or device did not open the full space."
        @unknown default:
            immersiveError = "The full space returned an unknown state."
        }
    }
}

private struct TeachingNotesPanel: View {
    @EnvironmentObject private var model: ExperienceShellModel

    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            HStack {
                Label(
                    model.isInspectingAsset ? "Inspection metadata" : "Detached placeholder notes",
                    systemImage: model.isInspectingAsset ? "cube.transparent" : "text.bubble.fill"
                )
                    .font(.headline)
                Spacer()
                Text(model.explanationMode.rawValue)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(ExperienceTheme.mint)
            }

            Text(model.isInspectingAsset
                 ? "Neutral catalog inspection. Procedure steps, actions, and anatomy-pinned claims are disabled."
                 : model.explanationSummary)
                .font(.callout)
                .foregroundStyle(ExperienceTheme.quietText)
                .fixedSize(horizontal: false, vertical: true)

            Divider()

            if model.isInspectingAsset {
                noteRow(number: 1, title: "Neutral asset metadata", text: primaryNote)
            } else {
                ForEach(Array(model.visiblePlaceholderNotes.enumerated()), id: \.element.id) { index, note in
                    noteRow(
                        number: index + 1,
                        title: note.displayCopy.title,
                        text: note.displayCopy.body
                    )
                }
            }

            Spacer()

            Label("Notes change framing with your selected explanation and detail settings.", systemImage: "slider.horizontal.3")
                .font(.caption2)
                .foregroundStyle(ExperienceTheme.quietText)
        }
        .padding(18)
        .experienceGlassPanel(cornerRadius: 24)
        .opacity(model.isNotesVisible ? 1 : 0.28)
    }

    private var primaryNote: String {
        if model.isInspectingAsset {
            return "Asset ID: \(model.selectedAssetID). Generic developer-preview geometry; not patient-authorized or clinical guidance."
        }
        return switch model.explanationMode {
        case .calm:
            "This view shows where a clot can interrupt blood flow."
        case .guided:
            "Start with the whole head, then follow the highlighted generic artery toward the conceptual clot marker."
        case .scholar:
            "Orient to the registered generic head assembly before isolating the cerebral arterial layer and right-M1 teaching marker."
        }
    }

    private func noteRow(number: Int, title: String, text: String) -> some View {
        HStack(alignment: .top, spacing: 10) {
            Text("\(number)")
                .font(.caption.bold())
                .foregroundStyle(.black)
                .frame(width: 22, height: 22)
                .background(ExperienceTheme.mint, in: Circle())
            VStack(alignment: .leading, spacing: 3) {
                Text(title)
                    .font(.caption.weight(.semibold))
                Text(text)
                    .font(.caption2)
                    .foregroundStyle(.white.opacity(0.76))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }
}

private struct TopicRail: View {
    @EnvironmentObject private var model: ExperienceShellModel
    private let topics = [
        ("Anatomy", "brain.head.profile"),
        ("Pathophysiology", "waveform.path.ecg"),
        ("Imaging", "viewfinder"),
        ("Interventions", "cross.case.fill"),
        ("Medications", "pills.fill"),
        ("Outcomes", "figure.walk.motion"),
        ("Guidelines", "book.closed.fill")
    ]

    var body: some View {
        if model.isInspectingAsset {
            inspectionRail
        } else {
            lessonRail
        }
    }

    private var inspectionRail: some View {
        VStack(alignment: .leading, spacing: 14) {
            Label("Asset inspection", systemImage: "cube.transparent.fill")
                .font(.headline)
                .foregroundStyle(ExperienceTheme.mint)
            Text(model.selectedAssetID.replacingOccurrences(of: "_", with: " ").capitalized)
                .font(.callout.weight(.semibold))
                .fixedSize(horizontal: false, vertical: true)
            Text("This neutral view is separate from the lesson timeline. No procedure action targets this asset.")
                .font(.caption)
                .foregroundStyle(ExperienceTheme.quietText)
                .fixedSize(horizontal: false, vertical: true)
            Spacer()
            Button {
                model.exitInspectionMode()
            } label: {
                Label("Return to lesson", systemImage: "arrow.uturn.backward")
            }
            .buttonStyle(.borderedProminent)
            .tint(ExperienceTheme.mint.opacity(0.72))
        }
        .padding(18)
        .experienceGlassPanel(cornerRadius: 24)
    }

    private var lessonRail: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Explore")
                .font(.headline)
            ForEach(Array(topics.enumerated()), id: \.offset) { index, topic in
                Button {
                    model.currentNoteIndex = index
                } label: {
                    HStack(spacing: 10) {
                        Image(systemName: topic.1)
                            .frame(width: 24)
                        Text(topic.0)
                            .font(.callout.weight(.medium))
                        Spacer()
                    }
                    .foregroundStyle(model.currentNoteIndex == index ? ExperienceTheme.mint : .white.opacity(0.75))
                    .padding(.vertical, 8)
                    .padding(.horizontal, 10)
                    .background(
                        model.currentNoteIndex == index ? ExperienceTheme.mint.opacity(0.1) : .clear,
                        in: RoundedRectangle(cornerRadius: 12)
                    )
                }
                .buttonStyle(.plain)
            }

            Spacer()

            Divider()

            VStack(alignment: .leading, spacing: 6) {
                Text("Scene asset")
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(ExperienceTheme.quietText)
                Text(model.selectedAssetID.replacingOccurrences(of: "_", with: " ").capitalized)
                    .font(.caption.weight(.semibold))
                    .fixedSize(horizontal: false, vertical: true)
                Text("Only the active teaching set is loaded; the remaining assets stay indexed in the library.")
                    .font(.caption2)
                    .foregroundStyle(ExperienceTheme.quietText)
                    .fixedSize(horizontal: false, vertical: true)
            }

            if model.isDeveloperOpenBranchAvailable {
                Button {
                    model.beginDeveloperOpenCranialPreview()
                } label: {
                    Label("Gated open-path preview", systemImage: "lock.shield")
                        .font(.caption.weight(.semibold))
                }
                .buttonStyle(.bordered)
                .tint(ExperienceTheme.amber)
                .accessibilityHint("Requires an explicit second confirmation and is unavailable in normal family mode")
            }
        }
        .padding(18)
        .experienceGlassPanel(cornerRadius: 24)
    }
}

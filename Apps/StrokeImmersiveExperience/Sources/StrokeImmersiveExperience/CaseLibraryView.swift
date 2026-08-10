import SwiftUI

struct CaseLibraryView: View {
    @EnvironmentObject private var model: ExperienceShellModel
    @State private var pendingDetachedCase: FictionalCaseCard?

    var body: some View {
        VStack(spacing: 22) {
            header

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(alignment: .top, spacing: 18) {
                    ForEach(ExperienceShellModel.demoCases) { caseCard in
                        caseView(caseCard)
                            .frame(width: 282)
                    }
                }
                .padding(.horizontal, 42)
            }
            .frame(maxHeight: 520)
            .scrollClipDisabled()

            HStack {
                SafetyBadge()
                Spacer()
                Text("Cases select predetermined educational scenes. They do not diagnose or recommend treatment.")
                    .font(.caption)
                    .foregroundStyle(ExperienceTheme.quietText)
            }
            .padding(.horizontal, 46)
            .padding(.bottom, 28)
        }
        .confirmationDialog(
            "Open the detached vessel teaching scenario?",
            isPresented: Binding(
                get: { pendingDetachedCase != nil },
                set: { if !$0 { pendingDetachedCase = nil } }
            ),
            titleVisibility: .visible
        ) {
            Button("Open conceptual vignette") {
                if let pendingDetachedCase { model.select(pendingDetachedCase) }
                pendingDetachedCase = nil
            }
            Button("Cancel", role: .cancel) { pendingDetachedCase = nil }
        } message: {
            Text("This scenario opens a magnified, conceptual, not-to-scale vessel view. It is not an anatomical fly-through or patient-specific route.")
        }
    }

    private var header: some View {
        HStack(alignment: .center, spacing: 18) {
            Button {
                model.screen = .landing
            } label: {
                Label("Back", systemImage: "chevron.left")
            }

            VStack(alignment: .leading, spacing: 4) {
                Text("Choose a fictional learning scenario")
                    .font(.largeTitle.bold())
            Text("Each card opens a catalogued developer-preview starting view from the shared asset library.")
                    .foregroundStyle(ExperienceTheme.quietText)
            }
            Spacer()
            Button {
                model.screen = .library
            } label: {
                Label("Asset library", systemImage: "square.grid.3x3")
            }
        }
        .padding(.horizontal, 44)
        .padding(.top, 34)
    }

    private func caseView(_ caseCard: FictionalCaseCard) -> some View {
        Button {
            if caseCard.id == "fictional_case_04_vessel_vignette_v1" {
                pendingDetachedCase = caseCard
            } else {
                model.select(caseCard)
            }
        } label: {
            VStack(alignment: .leading, spacing: 20) {
                ZStack {
                    RoundedRectangle(cornerRadius: 22, style: .continuous)
                        .fill(
                            LinearGradient(
                                colors: [ExperienceTheme.mint.opacity(0.18), ExperienceTheme.amber.opacity(0.08)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                    Image(systemName: caseCard.systemImage)
                        .font(.system(size: 70, weight: .light))
                        .foregroundStyle(ExperienceTheme.mint)
                }
                .frame(height: 150)

                VStack(alignment: .leading, spacing: 7) {
                    Text(caseCard.displayLabel.uppercased())
                        .font(.caption2.weight(.bold))
                        .tracking(1.4)
                        .foregroundStyle(ExperienceTheme.mint)
                    Text(caseCard.subtitle)
                        .font(.title3.weight(.semibold))
                        .foregroundStyle(.white)
                        .fixedSize(horizontal: false, vertical: true)
                    Text(caseCard.focus)
                        .font(.callout)
                        .foregroundStyle(ExperienceTheme.quietText)
                        .fixedSize(horizontal: false, vertical: true)
                }

                Spacer(minLength: 8)

                HStack {
                    Label("Fictional", systemImage: "person.crop.circle.badge.questionmark")
                        .font(.caption)
                        .foregroundStyle(ExperienceTheme.quietText)
                    Spacer()
                    Image(systemName: "arrow.right.circle.fill")
                        .font(.title2)
                        .foregroundStyle(ExperienceTheme.mint)
                }

                HStack(spacing: 6) {
                    ForEach(0 ..< 3, id: \.self) { index in
                        Circle()
                            .fill(index == 0 ? ExperienceTheme.mint : .white.opacity(0.18))
                            .frame(width: 7, height: 7)
                        if index < 2 {
                            Capsule()
                                .fill(.white.opacity(0.15))
                                .frame(width: 20, height: 1)
                        }
                    }
                    Text("orientation · focus · return")
                        .font(.caption2)
                        .foregroundStyle(ExperienceTheme.quietText)
                }
            }
            .padding(18)
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
            .experienceGlassPanel(cornerRadius: 28)
        }
        .buttonStyle(.plain)
        .accessibilityLabel("\(caseCard.displayLabel), \(caseCard.subtitle)")
        .accessibilityHint("Opens the fictional educational scene")
    }
}

import RealityKit
import SwiftUI

struct LandingView: View {
    @EnvironmentObject private var model: ExperienceShellModel

    var body: some View {
        VStack(spacing: 0) {
            topBar

            HStack(spacing: 52) {
                VStack(alignment: .leading, spacing: 28) {
                    Text("When stroke is sudden,\nclarity matters.")
                        .font(.system(size: 54, weight: .semibold, design: .rounded))
                        .tracking(-1.2)
                        .foregroundStyle(.white)

                    Text("Explore generic anatomy and a scripted educational care journey at a pace you control.")
                        .font(.title3)
                        .foregroundStyle(ExperienceTheme.quietText)
                        .fixedSize(horizontal: false, vertical: true)
                        .frame(maxWidth: 540, alignment: .leading)

                    audiencePicker

                    HStack(spacing: 14) {
                        Button {
                            model.screen = .cases
                        } label: {
                            Label("Choose a scenario", systemImage: "arrow.right")
                                .font(.headline)
                                .frame(minWidth: 210)
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(ExperienceTheme.mint.opacity(0.72))

                        Button {
                            model.screen = .library
                        } label: {
                            Label("Browse 150 assets", systemImage: "square.grid.3x3.fill")
                        }
                        .buttonStyle(.bordered)
                    }

                    SafetyBadge()
                }
                .frame(maxWidth: 600, alignment: .leading)

                HeroBrainPreview(audienceMode: model.audienceMode)
                    .frame(width: 470, height: 520)
            }
            .padding(.horizontal, 58)
            .padding(.bottom, 44)
        }
    }

    private var topBar: some View {
        HStack(spacing: 13) {
            Image(systemName: "brain.head.profile.fill")
                .font(.title2)
                .foregroundStyle(ExperienceTheme.mint)
            VStack(alignment: .leading, spacing: 1) {
                Text("STROKE CARE")
                    .font(.headline.weight(.bold))
                    .tracking(3.2)
                Text("LEARN · UNDERSTAND · EXPLORE")
                    .font(.caption2.weight(.semibold))
                    .tracking(1.7)
                    .foregroundStyle(ExperienceTheme.quietText)
            }
            Spacer()
            Label("150 assets · 3 visual-detail tiers", systemImage: "cube.transparent.fill")
                .font(.callout.weight(.medium))
                .foregroundStyle(ExperienceTheme.quietText)
        }
        .padding(.horizontal, 48)
        .padding(.vertical, 26)
    }

    private var audiencePicker: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("I’m viewing as")
                .font(.caption.weight(.semibold))
                .foregroundStyle(ExperienceTheme.quietText)

            HStack(spacing: 12) {
                ForEach(AudienceMode.allCases) { mode in
                    Button {
                        model.audienceMode = mode
                    } label: {
                        Label(mode.rawValue, systemImage: mode.systemImage)
                            .frame(minWidth: 132)
                    }
                    .buttonStyle(.bordered)
                    .tint(model.audienceMode == mode ? ExperienceTheme.mint : .white.opacity(0.35))
                    .accessibilityAddTraits(model.audienceMode == mode ? .isSelected : [])
                }
            }

            Label(
                "Developer preview: this choice changes placeholder framing only. Patient-display authorization remains locked.",
                systemImage: "lock.shield.fill"
            )
            .font(.caption2)
            .foregroundStyle(ExperienceTheme.amber)
            .fixedSize(horizontal: false, vertical: true)
        }
    }
}

private struct HeroBrainPreview: View {
    let audienceMode: AudienceMode

    private var modelURL: URL? {
        Bundle.main.resourceURL?
            .appending(path: "RealityKitContent/Assets/vision_pro_stroke_kit_v2/exports/usdz/brain_orientation_calm_educational_v1.usdz")
    }

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 44, style: .continuous)
                .fill(Color.white.opacity(0.025))
                .overlay {
                    RoundedRectangle(cornerRadius: 44, style: .continuous)
                        .stroke(ExperienceTheme.mint.opacity(0.18), lineWidth: 1)
                }

            RadialGradient(
                colors: [ExperienceTheme.glow.opacity(0.23), .clear],
                center: .center,
                startRadius: 10,
                endRadius: 220
            )

            if audienceMode == .presenter,
               let modelURL,
               FileManager.default.fileExists(atPath: modelURL.path()) {
                Model3D(url: modelURL) { phase in
                    switch phase {
                    case .empty:
                        ProgressView("Preparing orientation model…")
                    case .success(let model):
                        model
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .padding(38)
                    case .failure:
                        fallback
                    @unknown default:
                        fallback
                    }
                }
            } else {
                fallback
            }

            VStack {
                Spacer()
                Label(
                    audienceMode == .family ? "Abstract, low-detail orientation" : "Generic orientation model",
                    systemImage: "viewfinder"
                )
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(ExperienceTheme.mint)
                    .padding(.horizontal, 13)
                    .padding(.vertical, 9)
                    .background(.black.opacity(0.5), in: Capsule())
                    .padding(20)
            }
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("Generic three-dimensional brain orientation preview")
    }

    private var fallback: some View {
        Image(systemName: "brain.head.profile.fill")
            .font(.system(size: 190, weight: .ultraLight))
            .foregroundStyle(ExperienceTheme.mint.opacity(0.72))
            .shadow(color: ExperienceTheme.glow.opacity(0.5), radius: 36)
    }
}

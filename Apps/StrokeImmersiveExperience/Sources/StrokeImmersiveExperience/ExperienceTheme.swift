import SwiftUI

enum ExperienceTheme {
    static let canvas = Color.black
    static let panel = Color(red: 0.055, green: 0.06, blue: 0.065)
    static let mint = Color(red: 0.45, green: 0.88, blue: 0.79)
    static let amber = Color(red: 0.96, green: 0.66, blue: 0.37)
    static let quietText = Color.white.opacity(0.66)
    static let hairline = Color.white.opacity(0.14)
    static let glow = Color(red: 0.36, green: 0.80, blue: 0.76)
}

struct GlassPanelModifier: ViewModifier {
    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency
    var cornerRadius: CGFloat = 24
    var tint: Color = .white.opacity(0.025)

    func body(content: Content) -> some View {
        if reduceTransparency {
            content
                .background(Color.black.opacity(0.96), in: RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))
                .overlay {
                    RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                        .stroke(Color.white.opacity(0.34), lineWidth: 1.5)
                }
        } else {
            content
                .background(tint)
                .glassBackgroundEffect(in: RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))
                .overlay {
                    RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                        .stroke(ExperienceTheme.hairline, lineWidth: 1)
                }
        }
    }
}

extension View {
    func experienceGlassPanel(cornerRadius: CGFloat = 24, tint: Color = .white.opacity(0.025)) -> some View {
        modifier(GlassPanelModifier(cornerRadius: cornerRadius, tint: tint))
    }
}

struct SafetyBadge: View {
    var compact = false

    var body: some View {
        Label(
            compact ? "Educational preview" : "Generic educational preview — not patient-specific or surgical guidance",
            systemImage: "exclamationmark.shield.fill"
        )
        .font(compact ? .caption2.weight(.semibold) : .caption.weight(.semibold))
        .foregroundStyle(ExperienceTheme.amber)
        .padding(.horizontal, compact ? 10 : 14)
        .padding(.vertical, compact ? 7 : 9)
        .background(ExperienceTheme.amber.opacity(0.09), in: Capsule())
        .overlay { Capsule().stroke(ExperienceTheme.amber.opacity(0.32), lineWidth: 1) }
        .accessibilityLabel("Educational preview. Generic anatomy. Not patient-specific and not surgical guidance.")
    }
}

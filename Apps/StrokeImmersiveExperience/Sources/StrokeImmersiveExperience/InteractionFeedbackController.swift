import AVFAudio
import Foundation
import SwiftUI

/// Owns the app's optional, non-clinical interaction earcons and ambience.
///
/// The Vision Pro headset does not provide general-purpose vibration. Standard
/// SwiftUI controls keep their system hover/press treatment, while this class
/// adds only sparse state-confirmation sounds. Optional accessory haptics stay
/// behind the capability-gated adapter defined by InteractionFeedbackRecipes.
@MainActor
final class InteractionFeedbackController: ObservableObject {
    @Published var uiFeedbackEnabled: Bool {
        didSet {
            preferences.set(uiFeedbackEnabled, forKey: PreferenceKey.uiFeedbackEnabled)
            if !uiFeedbackEnabled { stopEarcons() }
        }
    }

    @Published var uiFeedbackVolume: Double {
        didSet {
            uiFeedbackVolume = uiFeedbackVolume.clamped(to: 0 ... 1)
            preferences.set(uiFeedbackVolume, forKey: PreferenceKey.uiFeedbackVolume)
        }
    }

    @Published var natureAmbienceEnabled: Bool {
        didSet {
            preferences.set(natureAmbienceEnabled, forKey: PreferenceKey.natureAmbienceEnabled)
            synchronizeAmbiencePlayback()
        }
    }

    @Published var natureAmbienceVolume: Double {
        didSet {
            natureAmbienceVolume = natureAmbienceVolume.clamped(
                to: 0 ... Double(InteractionAmbienceRecipes.softWaterRain.maximumGain)
            )
            preferences.set(natureAmbienceVolume, forKey: PreferenceKey.natureAmbienceVolume)
            ambiencePlayer?.volume = natureAmbienceEnabled && !systemRequestsSecondaryAudioSilence
                ? Float(natureAmbienceVolume)
                : 0
        }
    }

    @Published var externalAccessoryHapticsEnabled = false {
        didSet {
            if !externalAccessoryHapticsAvailable {
                externalAccessoryHapticsEnabled = false
            }
        }
    }

    @Published private(set) var externalAccessoryHapticsAvailable = false
    @Published private(set) var systemRequestsSecondaryAudioSilence = false
    @Published private(set) var lastFeedbackEvent: InteractionFeedbackEvent?
    @Published private(set) var resourceError: String?

    private enum PreferenceKey {
        static let uiFeedbackEnabled = "stroke.feedback.ui.enabled"
        static let uiFeedbackVolume = "stroke.feedback.ui.volume"
        static let natureAmbienceEnabled = "stroke.feedback.ambience.enabled"
        static let natureAmbienceVolume = "stroke.feedback.ambience.volume"
    }

    private let preferences: UserDefaults
    private let resourceRoot: URL?
    private var earconPlayers: [InteractionFeedbackEvent: AVAudioPlayer] = [:]
    private var lastEmissionUptime: [InteractionFeedbackEvent: TimeInterval] = [:]
    private var ambiencePlayer: AVAudioPlayer?
    private var ambienceFadeTask: Task<Void, Never>?
    private var ambienceDuckTask: Task<Void, Never>?
    private var secondarySilenceObserver: NSObjectProtocol?
    private var externalHapticAdapter: (any ExternalHapticFeedbackAdapter)?

    init(bundle: Bundle = .main, preferences: UserDefaults = .standard) {
        self.preferences = preferences
        resourceRoot = bundle.resourceURL?.appending(
            path: "InteractionFeedback",
            directoryHint: .isDirectory
        )

        uiFeedbackEnabled = preferences.object(forKey: PreferenceKey.uiFeedbackEnabled) as? Bool ?? true
        uiFeedbackVolume = (preferences.object(forKey: PreferenceKey.uiFeedbackVolume) as? Double
            ?? Double(InteractionFeedbackRecipes.defaultMasterGain)).clamped(to: 0 ... 1)
        // Ambience is intentionally opt-in. Evidence supports offering nature
        // sound as a choice, not assuming it is calming for every person.
        natureAmbienceEnabled = preferences.object(forKey: PreferenceKey.natureAmbienceEnabled) as? Bool ?? false
        natureAmbienceVolume = (preferences.object(forKey: PreferenceKey.natureAmbienceVolume) as? Double
            ?? Double(InteractionAmbienceRecipes.softWaterRain.defaultGain)).clamped(
                to: 0 ... Double(InteractionAmbienceRecipes.softWaterRain.maximumGain)
            )

        systemRequestsSecondaryAudioSilence = AVAudioSession.sharedInstance().secondaryAudioShouldBeSilencedHint
        secondarySilenceObserver = NotificationCenter.default.addObserver(
            forName: AVAudioSession.silenceSecondaryAudioHintNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            Task { @MainActor [weak self] in
                guard let self else { return }
                self.systemRequestsSecondaryAudioSilence = AVAudioSession.sharedInstance()
                    .secondaryAudioShouldBeSilencedHint
                self.synchronizeAmbiencePlayback()
            }
        }
        // Re-read after observer registration to close the small race between
        // sampling the hint and listening for subsequent changes. Resources
        // are prepared only after this fail-closed state is established.
        systemRequestsSecondaryAudioSilence = AVAudioSession.sharedInstance().secondaryAudioShouldBeSilencedHint
        preloadResources()
    }

    func installExternalHapticAdapter(_ adapter: any ExternalHapticFeedbackAdapter) {
        externalHapticAdapter = adapter
        Task { [weak self] in
            guard let self else { return }
            let available = await adapter.isAvailable
            await MainActor.run {
                self.externalAccessoryHapticsAvailable = available
                if !available { self.externalAccessoryHapticsEnabled = false }
            }
        }
    }

    /// Emits one causal feedback event after an action commits. Callers must not
    /// invoke this from raw gaze, head-pose, or continuous hand-tracking updates.
    @discardableResult
    func emit(_ event: InteractionFeedbackEvent, bypassCooldown: Bool = false) -> Bool {
        let recipe = InteractionFeedbackRecipes.recipe(for: event)
        guard uiFeedbackEnabled, recipe.defaultEnabled else { return false }

        let now = ProcessInfo.processInfo.systemUptime
        let cooldown = recipe.cooldown.timeInterval
        if !bypassCooldown,
           let previous = lastEmissionUptime[event],
           now - previous < cooldown {
            return false
        }

        guard let player = earconPlayers[event] else {
            resourceError = "The \(recipe.resourceName) feedback sound is unavailable. Visual feedback remains active."
            return false
        }

        activateAmbientAudioSessionIfPossible()
        enforceVoiceLimit(for: recipe)
        player.currentTime = 0
        player.volume = Float(uiFeedbackVolume) * decibelGain(recipe.gainTrimDecibels)
        player.prepareToPlay()
        let started = player.play()
        guard started else {
            resourceError = "The system declined feedback playback. Visual feedback remains active."
            return false
        }
        lastEmissionUptime[event] = now
        lastFeedbackEvent = event
        if event == .actionRequiresAttention { duckAmbienceForWarning() }
        emitExternalHapticIfAvailable(recipe.optionalExternalHapticIntent)
        return true
    }

    func previewFeedback() {
        emit(.confirmedStateChange, bypassCooldown: true)
    }

    var runtimeResourceSummary: (earcons: Int, ambienceReady: Bool) {
        (earconPlayers.count, ambiencePlayer != nil)
    }

    func stopAll() {
        ambienceFadeTask?.cancel()
        ambienceDuckTask?.cancel()
        stopEarcons()
        ambiencePlayer?.stop()
        ambiencePlayer?.currentTime = 0
    }

    func applicationDidBecomeActive() {
        synchronizeAmbiencePlayback()
    }

    func applicationWillResignActive() {
        stopAll()
    }

    private func preloadResources() {
        guard let resourceRoot else {
            resourceError = "The interaction-feedback resource folder is missing. Visual feedback remains active."
            return
        }

        var errors: [String] = []
        for recipe in InteractionFeedbackRecipes.all {
            let url = resourceRoot
                .appending(path: "Audio", directoryHint: .isDirectory)
                .appending(path: recipe.resourceName)
                .appendingPathExtension(recipe.resourceExtension)
            do {
                let player = try AVAudioPlayer(contentsOf: url)
                player.numberOfLoops = 0
                player.prepareToPlay()
                earconPlayers[recipe.event] = player
            } catch {
                errors.append(recipe.resourceName)
            }
        }

        let ambienceRecipe = InteractionAmbienceRecipes.softWaterRain
        let ambienceURL = resourceRoot
            .appending(path: "Audio", directoryHint: .isDirectory)
            .appending(path: ambienceRecipe.resourceName)
            .appendingPathExtension(ambienceRecipe.resourceExtension)
        if FileManager.default.fileExists(atPath: ambienceURL.path) {
            do {
                ambiencePlayer = try AVAudioPlayer(contentsOf: ambienceURL)
                ambiencePlayer?.numberOfLoops = -1
                ambiencePlayer?.volume = Float(natureAmbienceVolume)
                ambiencePlayer?.prepareToPlay()
            } catch {
                errors.append(ambienceRecipe.resourceName)
            }
        }

        resourceError = errors.isEmpty
            ? nil
            : "Some optional feedback resources could not be prepared: \(errors.joined(separator: ", "))."
        synchronizeAmbiencePlayback()
    }

    private func synchronizeAmbiencePlayback() {
        guard let ambiencePlayer else { return }
        ambienceFadeTask?.cancel()
        let recipe = InteractionAmbienceRecipes.softWaterRain
        if natureAmbienceEnabled && !systemRequestsSecondaryAudioSilence {
            activateAmbientAudioSessionIfPossible()
            if !ambiencePlayer.isPlaying {
                ambiencePlayer.volume = 0
                ambiencePlayer.play()
            }
            ambiencePlayer.setVolume(
                Float(natureAmbienceVolume),
                fadeDuration: recipe.fadeIn.timeInterval
            )
        } else {
            ambienceDuckTask?.cancel()
            ambiencePlayer.setVolume(0, fadeDuration: recipe.fadeOut.timeInterval)
            ambienceFadeTask = Task { @MainActor [weak self, weak ambiencePlayer] in
                try? await Task.sleep(for: recipe.fadeOut)
                guard !Task.isCancelled,
                      let self,
                      !self.natureAmbienceEnabled || self.systemRequestsSecondaryAudioSilence else { return }
                ambiencePlayer?.pause()
                ambiencePlayer?.currentTime = 0
            }
        }
    }

    private func duckAmbienceForWarning() {
        guard natureAmbienceEnabled,
              !systemRequestsSecondaryAudioSilence,
              let ambiencePlayer,
              ambiencePlayer.isPlaying else { return }
        ambienceDuckTask?.cancel()
        let recipe = InteractionAmbienceRecipes.softWaterRain
        let duckedGain = Float(natureAmbienceVolume) * decibelGain(recipe.duckUnderWarningDecibels)
        ambiencePlayer.setVolume(duckedGain, fadeDuration: 0.08)
        ambienceDuckTask = Task { @MainActor [weak self, weak ambiencePlayer] in
            try? await Task.sleep(for: .milliseconds(650))
            guard !Task.isCancelled,
                  let self,
                  self.natureAmbienceEnabled,
                  !self.systemRequestsSecondaryAudioSilence,
                  ambiencePlayer?.isPlaying == true else { return }
            ambiencePlayer?.setVolume(Float(self.natureAmbienceVolume), fadeDuration: 0.4)
        }
    }

    private func stopEarcons() {
        for player in earconPlayers.values where player.isPlaying {
            player.stop()
            player.currentTime = 0
        }
    }

    private func enforceVoiceLimit(for incoming: InteractionFeedbackRecipe) {
        var playing = earconPlayers.compactMap { event, player -> (InteractionFeedbackRecipe, AVAudioPlayer)? in
            guard player.isPlaying else { return nil }
            return (InteractionFeedbackRecipes.recipe(for: event), player)
        }

        if incoming.interruptsLowerPriority {
            for (recipe, player) in playing where recipe.priority < incoming.priority {
                player.stop()
                player.currentTime = 0
            }
            playing.removeAll { !$0.1.isPlaying }
        }

        while playing.count >= InteractionFeedbackRecipes.maximumSimultaneousEarcons,
              let lowest = playing.min(by: { $0.0.priority < $1.0.priority }) {
            lowest.1.stop()
            lowest.1.currentTime = 0
            playing.removeAll { $0.1 === lowest.1 }
        }
    }

    private func emitExternalHapticIfAvailable(_ intent: OptionalExternalHapticIntent?) {
        guard externalAccessoryHapticsEnabled,
              externalAccessoryHapticsAvailable,
              let intent,
              let adapter = externalHapticAdapter else { return }
        Task {
            try? await adapter.emit(intent)
        }
    }

    private func activateAmbientAudioSessionIfPossible() {
        let session = AVAudioSession.sharedInstance()
        do {
            try session.setCategory(.ambient, mode: .default, options: [.mixWithOthers])
            try session.setActive(true)
        } catch {
            // Playback may still work with the process's existing audio session.
            resourceError = "System audio-session preferences could not be applied. Visual feedback remains active."
        }
    }

    private func decibelGain(_ decibels: Float) -> Float {
        pow(10, decibels / 20)
    }
}

struct InteractionFeedbackSettingsButton: View {
    @EnvironmentObject private var feedback: InteractionFeedbackController
    @State private var isPresented = false

    var body: some View {
        Button {
            isPresented.toggle()
        } label: {
            Image(systemName: feedback.uiFeedbackEnabled ? "speaker.wave.2.fill" : "speaker.slash.fill")
                .frame(width: 24, height: 24)
        }
        .buttonStyle(.bordered)
        .accessibilityLabel("Sound and accessory haptic settings")
        .accessibilityValue(feedback.uiFeedbackEnabled ? "UI feedback on" : "UI feedback off")
        .popover(isPresented: $isPresented, arrowEdge: .top) {
            settingsPanel
                .frame(width: 380)
                .padding(24)
                .presentationCompactAdaptation(.popover)
        }
    }

    private var settingsPanel: some View {
        VStack(alignment: .leading, spacing: 18) {
            Label("Interaction feedback", systemImage: "waveform.badge.plus")
                .font(.title3.bold())

            Text("Short sounds confirm committed actions. Gaze, head movement, and continuous hand tracking never trigger audio.")
                .font(.caption)
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)

            Toggle("UI feedback sounds", isOn: $feedback.uiFeedbackEnabled)

            LabeledContent("UI volume") {
                Slider(value: $feedback.uiFeedbackVolume, in: 0 ... 1)
                    .frame(width: 180)
                    .disabled(!feedback.uiFeedbackEnabled)
            }

            Button("Preview gentle confirmation") {
                feedback.previewFeedback()
            }
            .buttonStyle(.bordered)
            .disabled(!feedback.uiFeedbackEnabled)

            Divider()

            Toggle("Optional water ambience", isOn: $feedback.natureAmbienceEnabled)
            Text("Off by default. This is a comfort preference, not anxiety treatment or a clinical intervention.")
                .font(.caption2)
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)

            if feedback.systemRequestsSecondaryAudioSilence {
                Label("Ambience is paused while another app requests audio priority.", systemImage: "speaker.slash")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }

            LabeledContent("Ambience volume") {
                Slider(
                    value: $feedback.natureAmbienceVolume,
                    in: 0 ... Double(InteractionAmbienceRecipes.softWaterRain.maximumGain)
                )
                    .frame(width: 180)
                    .disabled(!feedback.natureAmbienceEnabled)
            }

            Divider()

            Toggle("External accessory haptics", isOn: $feedback.externalAccessoryHapticsEnabled)
                .disabled(!feedback.externalAccessoryHapticsAvailable)
            Text(feedback.externalAccessoryHapticsAvailable
                 ? "A compatible accessory reported haptic capability."
                 : "Vision Pro has no built-in general-purpose vibration; no compatible accessory is connected.")
                .font(.caption2)
                .foregroundStyle(.secondary)
                .fixedSize(horizontal: false, vertical: true)

            if let error = feedback.resourceError {
                Label(error, systemImage: "exclamationmark.triangle.fill")
                    .font(.caption2)
                    .foregroundStyle(ExperienceTheme.amber)
            }
        }
    }
}

private extension Duration {
    var timeInterval: TimeInterval {
        let parts = components
        return Double(parts.seconds) + Double(parts.attoseconds) / 1_000_000_000_000_000_000
    }
}

private extension Comparable {
    func clamped(to range: ClosedRange<Self>) -> Self {
        min(max(self, range.lowerBound), range.upperBound)
    }
}

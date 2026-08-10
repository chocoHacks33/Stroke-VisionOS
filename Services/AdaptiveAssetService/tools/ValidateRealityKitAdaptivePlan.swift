import Foundation
import RealityKit

@main
struct ValidateRealityKitAdaptivePlan {
  @MainActor
  static func main() {
    do {
      try run()
    } catch {
      fputs("adaptive plan validation failed: \(error.localizedDescription)\n", stderr)
      exit(1)
    }
  }

  @MainActor
  private static func run() throws {
    guard CommandLine.arguments.count >= 8 else {
      fputs(
        "usage: ValidateRealityKitAdaptivePlan <source.usdz> <edit-response.json> <bindings.json> <profiles.json> <audience> <detail> <motion> [--patient-education] [--fallback-presented] [--family-authorized] [--family-privacy-confirmed]\n",
        stderr)
      exit(64)
    }

    let flags = Array(CommandLine.arguments.dropFirst(8))
    let flagSet = Set(flags)
    guard flagSet.count == flags.count,
      flagSet.isSubset(of: [
        "--patient-education", "--fallback-presented", "--family-authorized",
        "--family-privacy-confirmed",
      ])
    else {
      fputs("unknown or duplicate validation flag\n", stderr)
      exit(64)
    }

    let executionContext: AdaptiveExecutionContext =
      flagSet.contains("--patient-education")
      ? .patientEducation : .developerPreview

    let packageURL = URL(fileURLWithPath: CommandLine.arguments[1]).standardizedFileURL
    let responseURL = URL(fileURLWithPath: CommandLine.arguments[2]).standardizedFileURL
    let bindingsURL = URL(fileURLWithPath: CommandLine.arguments[3]).standardizedFileURL
    let profilesURL = URL(fileURLWithPath: CommandLine.arguments[4]).standardizedFileURL
    let expectedPresentation = AdaptiveExpectedPresentation(
      audience: CommandLine.arguments[5],
      detailPreference: CommandLine.arguments[6],
      motionPreference: CommandLine.arguments[7],
      familyParticipationAuthorized: flagSet.contains("--family-authorized"),
      familyPrivacyConfirmed: flagSet.contains("--family-privacy-confirmed")
    )
    let response = try RealityKitAdaptivePlanSession.decodeResponse(
      Data(contentsOf: responseURL)
    )
    let authorization = try AdaptiveLocalPlanAuthorization(
      bindingsURL: bindingsURL,
      profilesURL: profilesURL
    )
    let session = try RealityKitAdaptivePlanSession.load(contentsOf: packageURL)
    let fallbackPresentation: AdaptiveFallbackPresentation =
      flagSet.contains(
        "--fallback-presented")
      ? .appPresented(response.applicationPlan.fallbackIfUnresolved) : .notRequired
    let report = try session.apply(
      response,
      executionContext: executionContext,
      authorization: authorization,
      animationBaseline: .pristineLoadedRoot,
      fallbackPresentation: fallbackPresentation,
      expectedPresentation: expectedPresentation,
      uiReadiness: AdaptivePresentationUIReadiness(
        adaptationDisclosureVisible: true,
        comfortControlsAvailable: true,
        contentWarningPresented: true,
        progressiveDisclosureAvailable: true)
    )

    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    FileHandle.standardOutput.write(try encoder.encode(report))
    FileHandle.standardOutput.write(Data("\n".utf8))
    session.restoreOriginalPresentation()
  }
}

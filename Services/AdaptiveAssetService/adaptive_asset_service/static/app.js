"use strict";

const byId = (id) => document.getElementById(id);

const elements = {
  form: byId("adaptation-form"),
  assetFilter: byId("asset-filter"),
  assetSelect: byId("asset-id"),
  assetSummary: byId("asset-summary"),
  catalogCount: byId("catalog-count"),
  adaptationSource: byId("adaptation-source"),
  demoSettings: byId("demo-settings"),
  simulateTier: byId("simulate-tier"),
  simulationSeed: byId("simulation-seed"),
  detailSection: byId("detail-section"),
  submitButton: byId("submit-button"),
  resetButton: byId("reset-button"),
  recipeState: byId("recipe-state"),
  visualStage: byId("visual-stage"),
  stageTier: byId("stage-tier"),
  stageMotion: byId("stage-motion"),
  stageCaption: byId("stage-caption"),
  metricGroups: byId("metric-groups"),
  metricGroupsNote: byId("metric-groups-note"),
  metricBlood: byId("metric-blood"),
  metricLabels: byId("metric-labels"),
  metricMotion: byId("metric-motion"),
  metricMotionNote: byId("metric-motion-note"),
  gateTitle: byId("gate-title"),
  gateDetail: byId("gate-detail"),
  candidateCard: byId("candidate-card"),
  candidateTitle: byId("candidate-title"),
  candidateDetail: byId("candidate-detail"),
  visibleLayers: byId("visible-layers"),
  hiddenLayers: byId("hidden-layers"),
  mappingStatus: byId("mapping-status"),
  requestJson: byId("request-json"),
  responseJson: byId("response-json"),
  curlCommand: byId("curl-command"),
  copyRequest: byId("copy-request"),
  copyResponse: byId("copy-response"),
  copyCurl: byId("copy-curl"),
  jobCard: byId("job-card"),
  jobTitle: byId("job-title"),
  jobDetail: byId("job-detail"),
  jobLinks: byId("job-links"),
  toast: byId("toast"),
};

const state = {
  assets: [],
  selectedAssetId: "",
  lastRequest: null,
  lastResponse: null,
  pollRevision: 0,
  toastTimer: null,
};

function checkedValue(name) {
  const checked = document.querySelector(`input[name="${name}"]:checked`);
  return checked ? checked.value : "";
}

function titleCase(value) {
  return String(value || "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function compactModule(value) {
  const text = String(value || "Unspecified module");
  return text.length > 48 ? `${text.slice(0, 45)}…` : text;
}

function currentAsset() {
  return state.assets.find((asset) => asset.asset_id === elements.assetSelect.value) || null;
}

function setRecipeState(kind, label) {
  elements.recipeState.className = `recipe-state state-${kind}`;
  elements.recipeState.lastChild.textContent = label;
}

function showToast(message) {
  window.clearTimeout(state.toastTimer);
  elements.toast.textContent = message;
  elements.toast.classList.add("is-visible");
  state.toastTimer = window.setTimeout(() => elements.toast.classList.remove("is-visible"), 2200);
}

function assetMatches(asset, query) {
  if (!query) return true;
  const searchable = [asset.asset_id, asset.title, asset.module, asset.description]
    .join(" ")
    .toLocaleLowerCase();
  return searchable.includes(query);
}

function renderAssetOptions(query = "") {
  const normalized = query.trim().toLocaleLowerCase();
  const previous = elements.assetSelect.value || state.selectedAssetId;
  const matches = state.assets.filter((asset) => assetMatches(asset, normalized));
  const fragment = document.createDocumentFragment();

  for (const asset of matches) {
    const option = document.createElement("option");
    option.value = asset.asset_id;
    option.textContent = `${asset.title} · ${asset.asset_id}`;
    fragment.append(option);
  }

  elements.assetSelect.replaceChildren(fragment);
  if (matches.some((asset) => asset.asset_id === previous)) {
    elements.assetSelect.value = previous;
  } else if (matches.length) {
    elements.assetSelect.value = matches[0].asset_id;
  }
  state.selectedAssetId = elements.assetSelect.value;
  elements.catalogCount.textContent = `${matches.length} of ${state.assets.length} assets`;
  renderAssetSummary();
}

function renderAssetSummary() {
  const asset = currentAsset();
  elements.assetSummary.replaceChildren();

  const module = document.createElement("span");
  module.className = "asset-module";
  const title = document.createElement("strong");
  const description = document.createElement("p");

  if (!asset) {
    module.textContent = "No matching asset";
    title.textContent = "Refine the search or clear the filter.";
    description.textContent = "A manifest-backed asset is required before a request can be sent.";
  } else {
    module.textContent = compactModule(asset.module);
    title.textContent = asset.title;
    description.textContent = asset.description || `${asset.asset_id} · ${asset.clinical_review_status}`;
  }

  elements.assetSummary.append(module, title, description);
  elements.submitButton.disabled = !asset;
}

function preferredInitialAsset() {
  const candidates = [
    "brain_anatomy_realistic_v2",
    "artery_wall_cutaway_v2",
    "brain_orientation_calm_educational_v1",
  ];
  return candidates.find((id) => state.assets.some((asset) => asset.asset_id === id))
    || state.assets[0]?.asset_id
    || "";
}

async function loadCatalog() {
  elements.submitButton.disabled = true;
  try {
    const response = await fetch("/v1/catalog", { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error(`Catalog request failed with HTTP ${response.status}`);
    const document = await response.json();
    if (!Array.isArray(document.assets) || !document.assets.length) {
      throw new Error("The local manifest catalog is empty");
    }
    state.assets = document.assets;
    state.selectedAssetId = preferredInitialAsset();
    renderAssetOptions();
    elements.assetSelect.value = state.selectedAssetId;
    renderAssetSummary();
    elements.catalogCount.textContent = `${document.catalog.assets} assets · ${document.catalog.manifests} manifests`;
  } catch (error) {
    elements.catalogCount.textContent = "Catalog unavailable";
    elements.assetSummary.innerHTML = "";
    const strong = document.createElement("strong");
    const message = document.createElement("p");
    strong.textContent = "Could not load the local catalog.";
    message.textContent = error instanceof Error ? error.message : "Unknown catalog error";
    elements.assetSummary.append(strong, message);
    setRecipeState("error", "Catalog unavailable");
  }
}

function updateDemoControls() {
  const simulated = elements.adaptationSource.value === "simulated_demo";
  elements.demoSettings.hidden = !simulated;
  const simulateTier = simulated && elements.simulateTier.checked;
  elements.detailSection.classList.toggle("is-simulated", simulateTier);
  for (const input of elements.detailSection.querySelectorAll("input")) {
    input.disabled = simulateTier;
  }
}

function updateSubmitCopy() {
  const generate = checkedValue("mode") === "generate";
  elements.submitButton.firstElementChild.textContent = generate
    ? "Queue abstract review draft"
    : "Build preview recipe";
}

function updateSketchFromControls() {
  const detail = checkedValue("detail") || "simulated";
  const motion = checkedValue("motion") || "system_default";
  elements.visualStage.dataset.detail = detail === "simulated" ? "simplified" : detail;
  elements.visualStage.dataset.motion = motion;
  elements.stageTier.textContent = titleCase(detail).toLocaleUpperCase();
  elements.stageMotion.textContent = `${titleCase(motion).toLocaleUpperCase()} MOTION`;
}

function buildPayload() {
  const asset = currentAsset();
  if (!asset) throw new Error("Select a manifest-backed asset");

  const source = elements.adaptationSource.value;
  const payload = {
    asset_id: asset.asset_id,
    audience: checkedValue("audience"),
    mode: checkedValue("mode"),
    adaptation_source: source,
    motion_preference: checkedValue("motion"),
  };

  const useSimulatedTier = source === "simulated_demo" && elements.simulateTier.checked;
  if (!useSimulatedTier) {
    payload.detail_preference = checkedValue("detail");
  }
  if (source === "simulated_demo") {
    const seed = Number(elements.simulationSeed.value);
    if (!Number.isSafeInteger(seed) || seed < 0) {
      throw new Error("The browser demo seed must be a non-negative safe integer");
    }
    payload.simulation_seed = seed;
  }
  return payload;
}

function buildCurl(payload) {
  const serialized = JSON.stringify(payload);
  return [
    "curl --fail-with-body \\",
    "  -H 'Content-Type: application/json' \\",
    "  --data '" + serialized + "' \\",
    "  http://127.0.0.1:8765/v1/visual-adaptations",
  ].join("\n");
}

function rgbaToRgbChannels(rgba) {
  if (!Array.isArray(rgba) || rgba.length < 3) return "128, 203, 214";
  const channels = rgba.slice(0, 3).map((value) => {
    const numeric = Number(value);
    return Number.isFinite(numeric) ? Math.round(Math.min(1, Math.max(0, numeric)) * 255) : 128;
  });
  return channels.join(", ");
}

function renderLayerList(element, layers, placeholder) {
  element.replaceChildren();
  if (!Array.isArray(layers) || !layers.length) {
    const item = document.createElement("li");
    item.className = "placeholder";
    item.textContent = placeholder;
    element.append(item);
    return;
  }
  for (const layer of layers) {
    const item = document.createElement("li");
    item.textContent = String(layer);
    element.append(item);
  }
}

function formatPercent(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? `${Math.round(numeric * 100)}%` : "—";
}

function renderGate(response) {
  const contract = response.application_contract || response.generation_contract || {};
  elements.gateTitle.textContent = contract.patient_display_authorized === false
    || contract.display_authorized === false
    ? "Blocked by prototype policy"
    : "No patient-display approval reported";
  elements.gateDetail.textContent = contract.authorization_notice
    || (contract.review_gate
      ? titleCase(contract.review_gate)
      : "A completed recipe is not an approval to show adapted content to a patient.");
}

function renderCandidate(candidate) {
  if (!candidate) {
    elements.candidateCard.hidden = true;
    return;
  }
  elements.candidateCard.hidden = false;
  elements.candidateTitle.textContent = candidate.asset_id;
  elements.candidateDetail.textContent = candidate.co_load_with_source === false
    ? "Orientation-only replacement. Keep the source available and never co-load both."
    : "External specialist and human-factors review is required.";
}

function renderRecipe(response) {
  const recipe = response.recipe;
  const preference = response.presentation_preference || {};
  const detail = recipe.adaptation_tier || preference.detail_preference || "standard";
  const motion = recipe.motion || {};
  const visible = recipe.detail?.visible_layer_groups || [];
  const hidden = recipe.detail?.hidden_layer_groups || [];
  const applicationPlan = response.application_plan || null;
  const operationCounts = applicationPlan?.operation_counts || {};

  elements.visualStage.dataset.detail = detail;
  elements.visualStage.dataset.motion = motion.preference || "system_default";
  elements.visualStage.style.setProperty("--stage-tint", rgbaToRgbChannels(recipe.materials?.tint_rgba));
  elements.visualStage.style.setProperty("--blood-opacity", String(recipe.opacity?.blood_and_particles ?? 0));
  elements.visualStage.style.setProperty("--secondary-opacity", String(recipe.opacity?.secondary_anatomy ?? 0.5));
  elements.stageTier.textContent = titleCase(detail).toLocaleUpperCase();
  elements.stageMotion.textContent = `${titleCase(motion.preference || "system_default").toLocaleUpperCase()} MOTION`;
  elements.stageCaption.textContent = `${response.source_asset?.title || response.source_asset?.asset_id || "Asset"} · ${titleCase(detail)} presentation`;

  elements.metricGroups.textContent = String(visible.length);
  elements.metricGroupsNote.textContent = applicationPlan
    ? `${hidden.length} deferred · ${operationCounts.visibility || 0} exact edits`
    : `${hidden.length} deferred`;
  elements.metricBlood.textContent = formatPercent(recipe.opacity?.blood_and_particles);
  elements.metricLabels.textContent = String(recipe.annotations?.maximum_visible_labels ?? "—");
  elements.mappingStatus.textContent = applicationPlan
    ? `Exact SHA-bound map · ${(operationCounts.visibility || 0) + (operationCounts.materials || 0) + (operationCounts.animations || 0)} operations`
    : "Mapping not configured · fallback required";
  elements.metricMotion.textContent = Number.isFinite(Number(motion.speed_multiplier))
    ? `${Number(motion.speed_multiplier).toFixed(2)}×`
    : "—";
  elements.metricMotionNote.textContent = motion.autoplay ? "Autoplay permitted" : "Manual start / paused";

  renderLayerList(elements.visibleLayers, visible, "No visible groups returned");
  renderLayerList(elements.hiddenLayers, hidden, "No deferred groups returned");
  renderGate(response);
  renderCandidate(response.orientation_asset_candidate || response.generation_contract?.orientation_asset_candidate);
}

function renderResponse(response) {
  state.lastResponse = response;
  elements.responseJson.textContent = JSON.stringify(response, null, 2);
  renderRecipe(response);
  setRecipeState("ready", response.resolved_mode === "generate" ? "Draft queued" : "Recipe ready");
}

function resetJobCard() {
  state.pollRevision += 1;
  elements.jobCard.hidden = true;
  elements.jobCard.classList.remove("is-ready");
  elements.jobLinks.replaceChildren();
}

function renderJob(job) {
  elements.jobCard.hidden = false;
  const status = job.status || "queued";
  elements.jobTitle.textContent = titleCase(status);
  elements.jobDetail.textContent = job.display_authorized === false
    ? "Display authorization remains false. This artifact is for governed review only."
    : "Waiting for the local deterministic template.";
  elements.jobCard.classList.toggle("is-ready", status === "awaiting_clinician_review");
  elements.jobLinks.replaceChildren();

  if (status === "awaiting_clinician_review" && job.draft_artifacts) {
    for (const [label, artifact] of Object.entries(job.draft_artifacts)) {
      const link = document.createElement("a");
      link.href = artifact.href;
      link.textContent = `Review ${titleCase(label)}`;
      link.setAttribute("download", "");
      elements.jobLinks.append(link);
    }
  }
}

async function pollJob(jobId, revision, attempt = 0) {
  if (revision !== state.pollRevision || attempt > 30) return;
  try {
    const response = await fetch(`/v1/jobs/${encodeURIComponent(jobId)}`, { headers: { Accept: "application/json" } });
    const document = await response.json();
    if (!response.ok) throw new Error(document.error?.message || `Job request failed with HTTP ${response.status}`);
    renderJob(document);
    if (document.status === "queued") {
      window.setTimeout(() => pollJob(jobId, revision, attempt + 1), 350);
    }
  } catch (error) {
    elements.jobTitle.textContent = "Job polling stopped";
    elements.jobDetail.textContent = error instanceof Error ? error.message : "Unknown job error";
  }
}

async function submitAdaptation(event) {
  event.preventDefault();
  resetJobCard();
  let payload;
  try {
    payload = buildPayload();
  } catch (error) {
    setRecipeState("error", "Check request");
    showToast(error instanceof Error ? error.message : "Invalid request");
    return;
  }

  state.lastRequest = payload;
  elements.requestJson.textContent = JSON.stringify(payload, null, 2);
  elements.curlCommand.textContent = buildCurl(payload);
  elements.submitButton.disabled = true;
  setRecipeState("loading", payload.mode === "generate" ? "Queueing draft" : "Computing recipe");

  try {
    const response = await fetch("/v1/visual-adaptations", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
    });
    const document = await response.json();
    if (!response.ok) {
      throw new Error(document.error?.message || `Request failed with HTTP ${response.status}`);
    }
    renderResponse(document);
    if (document.generation_contract?.job_id) {
      renderJob(document.generation_contract);
      const revision = state.pollRevision;
      pollJob(document.generation_contract.job_id, revision);
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown endpoint error";
    elements.responseJson.textContent = JSON.stringify({ error: message }, null, 2);
    setRecipeState("error", "Request failed");
    showToast(message);
  } finally {
    elements.submitButton.disabled = !currentAsset();
  }
}

async function copyText(value, label) {
  if (!value) {
    showToast("Nothing to copy yet");
    return;
  }
  try {
    await navigator.clipboard.writeText(value);
  } catch {
    const temporary = document.createElement("textarea");
    temporary.value = value;
    temporary.setAttribute("readonly", "");
    temporary.style.position = "fixed";
    temporary.style.opacity = "0";
    document.body.append(temporary);
    temporary.select();
    document.execCommand("copy");
    temporary.remove();
  }
  showToast(`${label} copied`);
}

function resetControls() {
  elements.form.reset();
  elements.assetFilter.value = "";
  state.selectedAssetId = preferredInitialAsset();
  renderAssetOptions();
  elements.assetSelect.value = state.selectedAssetId;
  renderAssetSummary();
  updateDemoControls();
  updateSubmitCopy();
  updateSketchFromControls();
  resetJobCard();
  elements.stageCaption.textContent = "Configure a request to inspect its visual policy.";
  elements.mappingStatus.textContent = "Awaiting exact map";
  setRecipeState("idle", "Awaiting request");
}

elements.assetFilter.addEventListener("input", () => renderAssetOptions(elements.assetFilter.value));
elements.assetSelect.addEventListener("change", () => {
  state.selectedAssetId = elements.assetSelect.value;
  renderAssetSummary();
});
elements.adaptationSource.addEventListener("change", updateDemoControls);
elements.simulateTier.addEventListener("change", updateDemoControls);
elements.form.addEventListener("change", (event) => {
  if (event.target instanceof HTMLInputElement && event.target.name === "mode") updateSubmitCopy();
  updateSketchFromControls();
});
elements.form.addEventListener("submit", submitAdaptation);
elements.resetButton.addEventListener("click", resetControls);
elements.copyRequest.addEventListener("click", () => copyText(
  state.lastRequest ? JSON.stringify(state.lastRequest, null, 2) : "",
  "Request",
));
elements.copyResponse.addEventListener("click", () => copyText(
  state.lastResponse ? JSON.stringify(state.lastResponse, null, 2) : "",
  "Response",
));
elements.copyCurl.addEventListener("click", () => copyText(elements.curlCommand.textContent, "cURL command"));

updateDemoControls();
updateSubmitCopy();
updateSketchFromControls();
loadCatalog();

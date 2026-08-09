(function (root, factory) {
  "use strict";

  var api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  } else {
    root.VisualDetailSelectorV1 = api;
  }
}(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  var TIERS = Object.freeze(["minimal", "reduced80", "full"]);

  function fail(message) {
    throw new Error("VisualDetailSelectorV1: " + message);
  }

  function requireExplicitTier(tier) {
    if (typeof tier !== "string" || tier.length === 0) {
      fail("tier is required explicitly");
    }
    if (TIERS.indexOf(tier) === -1) {
      fail("unknown tier '" + tier + "'; expected minimal, reduced80, or full");
    }
    return tier;
  }

  function requireAssetId(assetId) {
    if (typeof assetId !== "string" || assetId.length === 0) {
      fail("assetId must be a non-empty string");
    }
    return assetId;
  }

  function requireCatalog(catalog) {
    if (!catalog || typeof catalog !== "object") {
      fail("catalog object is required");
    }
    if (catalog.catalog_id !== "visual_detail_variant_catalog_v1") {
      fail("unsupported catalog_id");
    }
    if (catalog.patient_display_authorized !== false) {
      fail("catalog must keep patient display disabled");
    }
    if (!Array.isArray(catalog.tier_order) ||
        catalog.tier_order.length !== TIERS.length ||
        catalog.tier_order.some(function (tier, index) { return tier !== TIERS[index]; })) {
      fail("catalog tier_order does not match the v1 contract");
    }
    if (!Array.isArray(catalog.assets) || !Array.isArray(catalog.variants)) {
      fail("catalog assets and variants arrays are required");
    }
  }

  function createSelector(catalog) {
    requireCatalog(catalog);

    var assetById = Object.create(null);
    var variantById = Object.create(null);

    catalog.assets.forEach(function (asset) {
      if (!asset || typeof asset.asset_id !== "string" || assetById[asset.asset_id]) {
        fail("catalog contains an invalid or duplicate asset_id");
      }
      assetById[asset.asset_id] = asset;
    });

    catalog.variants.forEach(function (variant) {
      if (!variant || typeof variant.variant_id !== "string" || variantById[variant.variant_id]) {
        fail("catalog contains an invalid or duplicate variant_id");
      }
      requireExplicitTier(variant.tier);
      variantById[variant.variant_id] = variant;
    });

    function select(assetId, tier) {
      requireAssetId(assetId);
      requireExplicitTier(tier);
      if (!assetById[assetId]) {
        fail("unknown asset_id '" + assetId + "'");
      }
      var variantId = assetId + "::" + tier;
      var variant = variantById[variantId];
      if (!variant || variant.asset_id !== assetId || variant.tier !== tier) {
        fail("catalog is missing variant '" + variantId + "'");
      }
      if (!variant.presentation_parameters || typeof variant.presentation_parameters !== "object") {
        fail("variant is missing resolved presentation_parameters");
      }
      var selection = {};
      Object.keys(variant).forEach(function (key) {
        selection[key] = variant[key];
      });
      selection.assembly_domain = assetById[assetId].assembly_domain;
      selection.presentation_parameters = Object.freeze(
        Object.assign({}, variant.presentation_parameters)
      );
      return Object.freeze(selection);
    }

    function selectMany(assetIds, tier) {
      requireExplicitTier(tier);
      if (!Array.isArray(assetIds)) {
        fail("assetIds must be an array");
      }
      return assetIds.map(function (assetId) {
        return select(assetId, tier);
      });
    }

    function getAsset(assetId) {
      requireAssetId(assetId);
      return assetById[assetId] || null;
    }

    return Object.freeze({
      getAsset: getAsset,
      select: select,
      selectMany: selectMany,
      listTiers: function () { return TIERS.slice(); }
    });
  }

  return Object.freeze({
    createSelector: createSelector,
    tiers: TIERS
  });
}));

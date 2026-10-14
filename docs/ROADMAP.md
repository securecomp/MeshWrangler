# Post-baseline roadmap (not shipped functionality)

1. **Pipeline launcher:** v1 implemented as `wrangle_it_v1.sh`, with stage failure stopping, stdout/stderr logging, and Mac validation. Future refinements to reporting/restart handling are optional enhancements, not current baseline requirements.
2. **Regional offline mode:** selectable geographic area and zoom range, permitted basemap package and optional local DEM; explicit online/offline switch and mode-specific settings. Never bulk-download OpenStreetMap public tile servers. Evaluate provider rights, package size and regional terrain sources first.
3. **Analysis improvements:** clarify observed exposure vs proven message delivery, stationary/mobile receiver context, historical coverage, connectivity indicators, and network fragmentation.
4. **Classification:** revisit aircraft-candidate and elevated/stationary semantics after current Explorer release.
5. **Reconciliation:** review 30 reported name variants and 11 public-key conflicts without corrupting source provenance.

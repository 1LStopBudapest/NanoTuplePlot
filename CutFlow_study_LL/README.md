# Cut-flow study for the long-lived analysis

Work in progress. A fork of the BR-weighted newComb pipeline that, instead of variable histograms, fills a single cut-flow histogram by walking the selection sequentially (filters, MET cut, HT cut, ISR cut, tau veto, lepton cut, extra-lepton veto, extra-jet veto, dphi cut, search region) for every mass point and BR.

Same scaffold as `../preselection_efficiency/`: `write_test_commands.py` generates `execute_test.sh` (and `execute_test_mini.sh` is a small hand-made subset for quick checks), each job runs `1DPlot_LL_BR_weighted_bothBR_newComb_cutFlow.py` with the worker `FillHistos_LL_bothBR_newComb_cutFlow.py`, and the results are appended to `../Run_results_csv/info_test_cutFlow_*.csv`. The `plot_cutFlow*.py` scripts draw the per-point and integrated cut-flows; `plot_cutFlow_integrated_allBR.py` overlays the BR range.

`1DPlot_test_lepton_truth.py` and `FillHistos_test_lepton_truth.py` are a further fork studying the truth origin of the selected leptons.

## Lepton truth matching

Two schemes, switched by the module-level `USE_GENPARTFLAV_MATCHING` flag at the top of `FillHistos_test_lepton_truth.py` — edit it by hand, there is no CLI flag.

- `False` (default, the one actually used): DeltaR matching of the leading reconstructed lepton to a final-state gen lepton (`status==1`, e/mu/tau, `pt>1`, `|eta|<2.5`), accepted below `DeltaR < 0.01`, followed by an ancestry walk to find where in the stop decay chain that gen lepton came from.
- `True`: the old NanoAOD `{Muon,Electron,LowPtElectron}_genPartFlav` flag, matched if the flag is 1 (prompt) or 15 (from prompt tau). Kept only for comparison. It cannot say the lepton came from *the stop* specifically, and it depends on NanoAOD's own reco-gen matching succeeding, which is the suspected reason it underperformed on displaced leptons.

### Origin classification

`get_stop_ancestry()` walks up `GenPart_genPartIdxMother` and returns the **signed** pdgId of the stop it ended on (0 if it never reaches one) plus the list of pdgIds crossed. `classify_lepton_origin()` then assigns exactly one bucket, testing in this order:

| Test | Bucket | Code |
|---|---|---|
| chain never reaches a stop | `not_from_stop` | 1 |
| leg is 2-body | `stop_2body` | 6 |
| no hadron in chain, tau present | `W_leptonic_tau` | 3 |
| no hadron in chain, no tau | `W_leptonic` | 2 |
| hadron present, W (±24) in chain | `W_hadronic` | 5 |
| hadron present, no W, bare b quark in chain | `stop_b` | 4 |
| hadron present, no W, b hadron only | `maybe_from_stop_b` | 7 |
| hadron present, no W, c hadron | `W_hadronic` | 5 |
| hadron present, no W, light hadron | `W_hadronic` | 5 |
| nothing above matched | `unclassified` | 8 |

The order matters. Bottom is tested before charm because a `B -> D l nu` cascade puts both flavours in one chain; the 2-body test comes first because a 2-body leg (`stop -> c chi0`) produces charm that would otherwise be read as a hadronic W.

Codes deliberately start at **1**, not 0, so the first bin of the histogram stays empty and visible. `unclassified` should stay empty — it is a canary for a logic hole, not a real category.

Points to keep in mind:

- **`maybe_from_stop_b` exists because of NanoAOD gen pruning.** A lepton from a b decay always has a B hadron in its chain, but the bare `b` quark is frequently pruned away, so `ell <- B <- stop` cannot prove the b came from the stop rather than from a (very rare) `W* -> c b` decay. `stop_b` is the confirmed case, `maybe_from_stop_b` the inferred one; the physical b population is the sum of the two, and `stop_b` alone is expected to be small.
- **Do not require an explicit W for the leptonic buckets.** The 4-body decay is a genuine four-body matrix element, so the virtual W is often not written to the record at all — `ell <- stop` directly is normal. The criterion is "no hadron crossed", not "a W was seen".
- **`leg_is_2body()` reads `stopDecay`/`stopAntiDecay` (>3.5 = 4-body, <3.5 = 2-body).** Which branch goes with which sign of the stop is still to be verified on the samples; a good check is that the 2-body fraction should vanish at BR=1.0 and grow like (1-BR).

### What gets filled

A lepton counts as truth-matched only if its origin is `W_leptonic` or `W_leptonic_tau`. Besides `truthMatchedLepton`, the fillers write a `lepOrigin` histogram holding the `ORIGIN_CODES` value of the matched gen lepton, so the origin composition of the leading lepton can be read off directly. It is only filled when the DeltaR match succeeds, so its integral is below the event count, and it stays empty in `genPartFlav` mode.

`1DPlot_test_lepton_truth.py` must pass `vList` (not `cutflow`) into `FillHistosBothBR` — `vList` seeds the per-event `var03`/`var10` key set, and any histogram whose key is missing there triggers the "missing in var03dictionary" print on every event that does not set it.

`LeptonTruthMatcher.py` is a **standalone copy of the same logic** packaged as a class, dependency-free apart from `math`, meant to be handed to another analyst to drop into their own `FillHistos`-style script. It takes a plain reco-lepton dict of the shape `TreeVarSel_LL.getSortedLepVar()` returns rather than importing the selection itself. Keep its classifier in sync with `FillHistos_test_lepton_truth.py` if either changes.

This folder was not part of the July 2026 reorg and is being updated by the analyst directly, so leave it alone unless asked.

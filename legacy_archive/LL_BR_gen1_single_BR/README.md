# BR pipeline, generation 1: single-BR reweighting

The first attempt at BR-reweighted signal plots. `1DPlot_LL_BR_weighted.py` plus `FillHistos_LL_BR.py` run over one splitted signal sample at a time (`SampleChainSplitted`, sample keys like `Sig_Splitted_300_280_BR_0p300`) and apply the `ReweightBRctau` weight for the target BR. There is no combination of the BR=0.3 and BR=1.0 samples yet, no ctau-tail handling, and no CSV output.

Superseded first by the both-BR combination (see `../../ctau_fit_study/`) and ultimately by `../../preselection_efficiency/`.

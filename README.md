This python based framework works in any system where ROOT is installed (Higgs machine at ELTE would be appropriate as all the samples are there).
There are scipts which analyze nanoAOD root files and produce histograms.
More stuff will be added time to time.

```
git clone git@github.com:1LStopBudapest/NanoTuplePlot.git

cd 1LStopBudapest/NanoTuplePlot

```
change path name under Dir.py file

Run 1DPlot.py for producing 1D histograms.
Foe example,

```
python 1DPlot.py --sample TTSingleLep_pow --startfile 0 --nfiles 10

```

Likewise, run RatioPlot.py to make Ration plots.

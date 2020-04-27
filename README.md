This python based framework works in any system where ROOT is installed (Higgs machine at ELTE would be appropriate as all the samples are there).
There are scipts which analyze nanoAOD root files and produce histograms.
More stuff will be added time to time.

```
git clone git@github.com:1LStopBudapest/NanoTuplePlot.git
git clone git@github.com:1LStopBudapest/Sample.git
git clone git@github.com:1LStopBudapest/Helper.git

cd Sample

```
change path name under Dir.py file

Sample information are listed in FileList_2016.py (only 2016 sample info, rest will be added later)
Now plotting script

```
cd ../NanoTuplePlot

```
Run 1DPlot.py for producing 1D histograms.

For example,

```
python 1DPlot.py --sample TTSingleLep_pow --startfile 0 --nfiles 10

```

Likewise, run RatioPlot.py to make Ratio plots. This is for shape comparison so for now, histograms are unit normalised. More option can be added later.

```
python RatioPlot.py --sample1 Stop_500_480_tau10mm_fast --sample2 Stop_500_480_tau10mm_fast

```

For the Data-MC comparison, we have stack plotting script
```
StackPlotScript.py

```
This file runs StackHistMaker.py script for the given samples using GPU parallel program.
for that parallel program needs to be installed in the system (can be checked just typing parallel in terminal)
if not installed, please install it.

Few parameters need to be provided like samplesRun (lisf of samples) , fileperjobMC, fileperjobData, TotJobs(number parallel jobs)
A txt file is created with run command of  StackHistMaker.py . The number of lines of the txt file will run in parallel
A shell file is produced, and then executed. First, the txt files will be processed to produce root files with histograms then it runs StackPlot.py with the list of sample (from given samplesRun) which creats the stack histograms.
This python based framework works in any system where ROOT is installed (Higgs machine at ELTE would be appropriate as all the samples are there).
There are scipts which analyze nanoAOD root files and produce histograms.
More stuff will be added time to time.

One needs to checkout following directories from the github repository 1LStopBudapest

```
git clone git@github.com:1LStopBudapest/NanoTuplePlot.git
git clone git@github.com:1LStopBudapest/Sample.git
git clone git@github.com:1LStopBudapest/Helper.git

cd Sample

```
Add user and change path name under (if needed) Dir.py file 

Sample information are listed in FileList_*.py files (2017 sample info missing, will be added soon)
(check Sample readme)


Now plotting script

```
cd ../NanoTuplePlot

```

There are two kind of scripts: for prompt analysis and for displaced or long-lived analysis. Displaced scripts have suffix '_LL'.

Run 1DPlot.py for plotting physics objects or variables. Script produces 1D histograms of those variables.

For example,

```
python 1DPlot.py --sample TTSingleLep_pow --startfile 0 --nfiles 10

```

For the signal sample, give the sample name like T2tt_500_490. T2tt is the name of the signal (though its 4 body but saved bt this name), the fist value is stop mass and the next one is neutralino. This is like a single signal point from the fastsim signal grid. One can also plot variable from the pilot signal point (both fullsim and fastsim) by using sample name like 'Sig_Prompt_500_470_full' or 'Sig_Prompt_500_470_fast' 



For the Data-MC comparison, we have stack plotting script
```
python StackPlotScript.py

```
This StackPlotScript.py file runs StackHistMaker.py script for the given samples using GPU parallel program.
For this, parallel program needs to be installed in the system (can be checked just typing parallel in terminal).
if not installed, please install it.

Few parameters need to be provided like samplesRun (lisf of samples) , fileperjobMC, fileperjobData, TotJobs(number parallel jobs) inside StackPlotScript.py

A txt file is created with run command of  StackHistMaker.py . The number of lines of the txt file will run in parallel

A shell file is produced, and then executed. First, the txt files will be processed to produce root files with histograms then it runs StackPlot.py with the list of samples (from given samplesRun) which creats the stack histograms.


To Make root fiels containing Region histogram for all signal points and SM processes and data, run the following script

```
python MakeRegionHistScripy.py --sample Signal
```
This will run over all the signal points. For SM and data, use --sample Other

The deafault region is SR+CR (search and control regions), to make histogram with other region, use --region option



One can run RatioPlot.py to make Ratio plots between two samples for a given variable. This is for shape comparison so for now, histograms are unit normalised. More option can be added later.

```
python RatioPlot.py --sample1 Stop_500_480_tau10mm_fast --sample2 Stop_500_480_tau10mm_fast

```
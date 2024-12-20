This python based framework works in any system where ROOT is installed (Higgs machine at ELTE would be appropriate as all the samples are there).
There are scipts which analyze nanoAOD root files and produce histograms.
More stuff will be added time to time.

One needs to checkout following directories from the github repository 1LStopBudapest

```
git clone git@github.com:1LStopBudapest/NanoTuplePlot.git
git clone git@github.com:1LStopBudapest/Sample.git
git clone git@github.com:1LStopBudapest/Helper.git

```

Go to the Sample directory. 
Add user and change path name for plotDir under Dir.py file. userpath is the intial path for the directory where input samples are located (rest of the path is mentioned in FileList_.py files). No need to change userpath unless one need to use private input sample (In that case, pathname in FileList_.py file should also be changed).

```
cd Sample

```
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
python 1DPlot.py --sample TTSingleLep_pow --startfile 0 --nfiles 10 --nevents 10000

```

For the signal sample, give the sample name like T2tt_500_490. T2tt is the name of the signal (though its 4 body but saved by this name), the fist value is stop mass and the next one is neutralino. This is like a single signal point from the fastsim signal grid. One can also plot variable from the pilot signal point (both fullsim and fastsim) by using sample name like 'Sig_Prompt_500_470_full' or 'Sig_Prompt_500_470_fast' 



For the Data-MC comparison, we have stack plotting script
```
python StackPlotScript.py

```
This StackPlotScript.py file runs StackHistMaker.py script for the given samples using GPU parallel program.
For this, parallel program needs to be installed in the system (can be checked just typing parallel in terminal).
if not installed, please install it.

Few parameters need to be provided like samplesRun (lisf of samples) , fileperjobMC, fileperjobData, TotJobs(number parallel jobs) inside StackPlotScript.py

A txt file is created with run command of  StackHistMaker.py . The number of lines of the txt file will run in parallel

A shell file is produced, and then executed. First, the txt files will be processed to produce root files with histograms then it runs StackPlot.py with the list of samples (from given samplesRun) which creats the stack histograms plots in pdf or png format. 


To make the region histograms for the different BK processes (also for pilot fast/full sim signal points and data; please dont run over data while in "blind" state), and to plot the stack histograms of different BKs, run the following script

```
python StackPlotScript_Region.py
```

Another set of scripts are there to make root files containing Region histogram for all signal points and SM processes and data, run the following script. Dont run over data while in "blind" state

```
python MakeRegionHistScripy.py --sample Signal
```
This will run over all the signal points. For SM and data, use --sample Other

The deafault region is SR+CR (search and control regions), to make histogram with other region, use --region option



Make Histograms for the datacard(DC). We use cut&count DC, so the following scripts produce the root file containing the hostograms which will be used as input to make the cut&count DC

```
python CountDCHistScript.py

```
The above command makes the root file containing the rate histograms as well as several systematics. Please check CountDCHistScript.py and modify the sample or region or year if needed.


For the JEC & JER systematics, we need to run a seeparate script as follows
```
python CountDCHistJECScript.py

```
The above command makes the root file containing the rate histograms(the nominal one) as well as JEC & JER up/down systematics


The following one might not work as RatioPlot.py needs to be modified to run over latest samples.

One can run RatioPlot.py to make Ratio plots between two samples for a given variable. This is for shape comparison so for now, histograms are unit normalised. More option can be added later.

```
python RatioPlot.py --sample1 Stop_500_480_tau10mm_fast --sample2 Stop_500_480_tau10mm_fast

```
parallel --jobs 1 < parallelJobsubmit.txt
hadd StackHist_WJetsToLNu.root StackHist_WJetsToLNu_HT70to100*.root StackHist_WJetsToLNu_HT100to200*.root StackHist_WJetsToLNu_HT200to400*.root StackHist_WJetsToLNu_HT400to600*.root StackHist_WJetsToLNu_HT600to800*.root
mv StackHist_WJetsToLNu.root /home/mleoncoe/stopAnalysis/test/Plots/StackFiles/Displaced/Dxy2/total
hadd StackHist_TTbar.root StackHist_TTSingleLep_pow*.root StackHist_TTLep_pow*.root
mv StackHist_TTbar.root /home/mleoncoe/stopAnalysis/test/Plots/StackFiles/Displaced/Dxy2/total
hadd StackHist_ST.root StackHist_T_tch_pow*.root StackHist_TBar_tch_pow*.root StackHist_T_tWch_ext*.root StackHist_TBar_tWch_ext*.root
mv StackHist_ST.root /home/mleoncoe/stopAnalysis/test/Plots/StackFiles/Displaced/Dxy2/total
hadd StackHist_DYJetsToLL.root StackHist_DYJetsToLL_M50_HT70to100*.root StackHist_DYJetsToLL_M50_HT100to200*.root StackHist_DYJetsToLL_M50_HT200to400*.root StackHist_DYJetsToLL_M50_HT400to600*.root StackHist_DYJetsToLL_M50_HT600to800*.root
mv StackHist_DYJetsToLL.root /home/mleoncoe/stopAnalysis/test/Plots/StackFiles/Displaced/Dxy2/total
hadd StackHist_ZJetsToNuNu.root StackHist_ZJetsToNuNu_HT100to200*.root StackHist_ZJetsToNuNu_HT200to400*.root StackHist_ZJetsToNuNu_HT400to600*.root StackHist_ZJetsToNuNu_HT600to800*.root StackHist_ZJetsToNuNu_HT800to1200*.root
mv StackHist_ZJetsToNuNu.root /home/mleoncoe/stopAnalysis/test/Plots/StackFiles/Displaced/Dxy2/total
hadd StackHist_QCD.root StackHist_QCD_HT300to500*.root StackHist_QCD_HT500to700*.root StackHist_QCD_HT700to1000*.root StackHist_QCD_HT1000to1500*.root StackHist_QCD_HT1500to2000*.root
mv StackHist_QCD.root /home/mleoncoe/stopAnalysis/test/Plots/StackFiles/Displaced/Dxy2/total
hadd StackHist_TTV.root StackHist_TTWToLNu*.root StackHist_TTWToQQ*.root StackHist_TTW_LO*.root StackHist_TTZ_LO*.root StackHist_TTG*.root
mv StackHist_TTV.root /home/mleoncoe/stopAnalysis/test/Plots/StackFiles/Displaced/Dxy2/total
hadd StackHist_VV.root StackHist_WW*.root StackHist_WWTo2L2Nu*.root StackHist_WWTo1L1Nu2Q*.root StackHist_WZTo1L1Nu2Q*.root StackHist_WZTo1L3Nu*.root
mv StackHist_VV.root /home/mleoncoe/stopAnalysis/test/Plots/StackFiles/Displaced/Dxy2/total
hadd StackHist_Sig_Displaced_300_290_full.root StackHist_Sig_Displaced_300_290_full_*.root
mv StackHist_Sig_Displaced_300_290_full.root /home/mleoncoe/stopAnalysis/test/Plots/StackFiles/Displaced/Dxy2/total
hadd StackHist_Sig_Displaced_350_335_full.root StackHist_Sig_Displaced_350_335_full_*.root
mv StackHist_Sig_Displaced_350_335_full.root /home/mleoncoe/stopAnalysis/test/Plots/StackFiles/Displaced/Dxy2/total
hadd StackHist_Sig_Displaced_400_380_full.root StackHist_Sig_Displaced_400_380_full_*.root
mv StackHist_Sig_Displaced_400_380_full.root /home/mleoncoe/stopAnalysis/test/Plots/StackFiles/Displaced/Dxy2/total
mv StackHist_*.root /home/mleoncoe/stopAnalysis/test/Plots/StackFiles/Displaced/Dxy2
python  StackPlot_LL.py -l WJetsToLNu TTbar ST DYJetsToLL ZJetsToNuNu QCD TTV VV Sig_Displaced_300_290_full Sig_Displaced_350_335_full Sig_Displaced_400_380_full
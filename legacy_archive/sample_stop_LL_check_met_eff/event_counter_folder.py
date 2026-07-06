import ROOT
import os

def count_events_chain(folder_path):
    """Count total events using TChain (most efficient method)"""
    chain = ROOT.TChain("Events")
    
    # Add all .root files in the folder to the chain
    for filename in os.listdir(folder_path):
        if filename.endswith(".root"):
            file_path = os.path.join(folder_path, filename)
            print("adding file "+str(file_path))
            chain.Add(file_path)
    
    total_events = chain.GetEntries()
    return total_events

# Usage
#folder_path = "/eos/cms/store/group/phys_susy/hephy/StopsCompressed/SMS-T2tt-4bd_genMET-100_genHT200_mStop-250To1100_dM-10To30_TuneCP5_LLStop_13TeV-madgraphMLM-pythia8/crab_RunIISummer20UL16MiniAODv2-FSUL16_106X_mcRun2_asymptotic_v17-v1_privateUL16nanov9/0000/"
folder_path = "/media/moises/Data/workspacePcElte/sampleSplitting/susySamples/2017/SMS_T2tt_mStop_250to1100_dM_10to30_LL/"

total_events = count_events_chain(folder_path)
print(f"Total events: {total_events}")
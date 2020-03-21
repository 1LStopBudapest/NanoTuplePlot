import ROOT

XlabelDict = {

    'MET' : 'MET (GeV)',
    'HT'  : 'HT (GeV)',
    'ISRJetPt' : 'ISR Jet p_{T} (GeV)',
    'Njet20' : 'N_{jets}(>20 GeV)',
    'Njet30' : 'N_{jets}(>30 GeV)',
    'Nbjet30' : 'N_{bjets}(>30 GeV)',
    'Nbjet20' : 'N_{bjets}(>20 GeV)',
    'jet1pt' : 'Leading jet p_{T} (GeV)',
    'jet2pt' : '2nd leading jet p_{T} (GeV)',
    'Muonpt' : '#mu p_{T}',
    'Muondxy' : '#mu d_{xy}',
    'Muondz' : '#mu d_{z}',
    'Elept' : 'e p_{T}',
    'Eledxy' : 'e d_{xy}',
    'Eledz' : 'e d_{z}',
    'Nmu'   : 'N_{#mu}',
    'Ne'  :  'N_{e}',
}

colDict = {
    'Signal' : ROOT.kBlack,
    'TTSingleLep_pow'  : ROOT.kAzure+2,

}

RatioTitleDict = {
'fastfull' : 'fast / full'

}

RatioLegendDict = {
'fastfull' : ['FastSim', 'FullSim']

}

def getXTitle(title):
    return XlabelDict[title]

def getColor(sample):
    if "Stop" in sample:
        return colDict['Signal']
    else:
        return colDict[sample]

def getRatioTitle(comp):
    return RatioTitleDict[comp]

def getRatioLegendTitle(h1, h2, comp):
    if 'fastfull' in comp:
        return RatioLegendDict['fastfull']
    else:
        return [h1.GetName().strip(h1.GetTitle()+"_"), h2.GetName().strip(h2.GetTitle()+"_")]

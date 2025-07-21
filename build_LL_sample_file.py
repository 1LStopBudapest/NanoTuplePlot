
valid_masses = [[250, 240], [300, 280], [325, 315], [350, 340], [350, 320], \
                [375, 365], [375, 355], [400, 390], [425, 400], [500, 490], \
                [525, 515], [550, 535], [600, 590], [600, 575], [650, 635], \
                [675, 665], [725, 715], [725, 705], [800, 790], [850, 840], \
                [900, 875], [925, 900], [975, 965], [1000, 990], [1075, 1065]]

for massList in valid_masses:

    mStop = massList[0]
    mX0 = massList[1]

    print("samples['Sig_Splitted_mStop_"+str(mStop)+"to"+str(mX0)+"_BR_1p000'] = [os.path.join(userpath, NoSplittedSignal_dir, '"+str(mStop)+"_"+str(mX0)+"_files/BR_1.000/'), ]")
    print("samples['Sig_Splitted_mStop_"+str(mStop)+"to"+str(mX0)+"_BR_0p300'] = [os.path.join(userpath, NoSplittedSignal_dir, '"+str(mStop)+"_"+str(mX0)+"_files/BR_0.300/'), ]")

#samples['Sig_Splitted_mStop_250to1100_full'] = [os.path.join(userpath, NoSplittedSignal_dir), ]


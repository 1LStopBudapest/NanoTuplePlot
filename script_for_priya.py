

delta_m_stop = 25
delta_m_x0 = [10,15,20,25,30]

for mStop in range(250,1100+delta_m_stop,delta_m_stop):
    print("mStop = "+str(mStop))
    for Dmx0 in delta_m_x0:
        mX0 = mStop-Dmx0
        print("mx0 = "+str(mX0))
        
        #Mask for cutting the files
        cut = "Max$(GenPart_mass*(abs(GenPart_pdgId)==1000006))=="+str(mStop)+"&&Max$(GenPart_mass*(abs(GenPart_pdgId)==1000022))=="+str(mX0)
        cut2 = "Max$(GenModel_T2tt_4bd_"+str(mStop)+"_"+str(mX0)+"_0.300)=="+str(1)
        cut3 = cut+"&&"+cut2

#call the function HVEffPosQC8Stand and convert the position in the stand in the mapped HV channel
#this script gives in output the fisrt part of the string needed for the query of an element in the table ELEMENTS_ALL (it contains the HV values for each )
# the returned string is of the form cms_gem_dcs_1:CAEN/904_HV_mainframe/board00/channel007
import HVEffPosQC8Stand

def HVQC8Mapping ( position, runNumber ):
	#print ( position, runNumber )
	
	position = position.replace("/","_")
	

	ChannelMapList = [ "Top_G3Bot", "Top_G3Top", "Top_G2Bot", "Top_G2Top", "Top_G1Bot", "Top_G1Top", "Top_Drift", "Bot_G3Bot", "Bot_G3Top", "Bot_G2Bot", "Bot_G2Top", "Bot_G1Bot", "Bot_G1Top", "Bot_Drift"]
        
        #MainframeMapList and BoardMapList lists follow the order of ChamberMapList
        ChamberMapList = [ "1_1", "1_2", "1_3", "2_1", "2_2", "2_3", "3_1", "3_2", "3_3", "4_1", "4_2", "4_3", "5_1", "5_2", "5_3" ]
        MainframeMapList = [ "904_HV_mainframe",  "904_HV_mainframe",  "904_HV_mainframe",  "904_HV_mainframe",  "904_HV_mainframe",  "904_HV_mainframe",  "904_HV_mainframe",  "904_HV_mainframe",  "904_HV_mainframe", "904_Shared_mainframe",  "904_Shared_mainframe",  "904_Shared_mainframe",  "904_Shared_mainframe",  "904_Shared_mainframe",  "904_Shared_mainframe" ]
        BoardMapList = [ "board00", "board01", "board02", "board03", "board04", "board05", "board06", "board07", "board08", "board10", "board14", "board15", "board11", "board12", "board13" ]
        
        
        channelList = [ "G3Bot", "G3Top", "G2Bot", "G2Top", "G1Bot", "G1Top", "Drift"]
	
	#print position[:3]
	chamberIdx = ChamberMapList.index(str(position[:3]))
	#print chamberIdx
	#print ChamberMapList[ chamberIdx ]

	#prepare the string for the query in table ELEMENTS_ALL
	firstPartQueryString = "cms_gem_dcs_1:CAEN/"+MainframeMapList[chamberIdx]+"/"+BoardMapList[chamberIdx]+"/"

	if position[4] == "T":
		firstPartQueryString = firstPartQueryString + "channel000"
	elif position[4] == "B":
		firstPartQueryString = firstPartQueryString + "channel007"
	
	return firstPartQueryString



#TEST CODE
#print HVEffPosQC8Stand.HVEffPosQC8Stand ( "GE1/1-X-L-CERN-0001",1 )
#pos = HVEffPosQC8Stand.HVEffPosQC8Stand ( "GE1/1-X-L-CERN-0001",1 )


#HVQC8Mapping(pos, 1)

#print HVQC8Mapping(pos, 1)

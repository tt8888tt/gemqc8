import cx_Oracle
import ROOT
import os
import time
from operator import itemgetter
from array import array

#in the DB the DeltaV between pins are saved, not the V from ground

#time interval considered to extract the data
#sta_period = "'2018-07-17 08:00:01'"
#end_period = "'2018-07-17 14:30:01'"

#to control the status there are data in the period 
#sta_period = "'2018-12-06 22:00:01'"
#end_period = "'2019-03-15 08:00:01'"

#test with board 4 channel 2 : 2-2-Top

sta_period = raw_input("Insert start time in format YYYY-MM-DD HH:mm:ss\n")
type(sta_period)
end_period = raw_input("Insert end time in format YYYY-MM-DD HH:mm:ss\n")
type(end_period)

#to remove ' and space
start=sta_period.replace(" ", "_")
end=end_period.replace(" ", "_")
#start = start[1:-1]
#end = end[1:-1]
start=start.replace(":", "-")
end=end.replace(":", "-")
#print(start)
#print(end)

#add ' at beginning and end to have the date in the format for the query
sta_period = "'" + sta_period + "'"
end_period = "'" + end_period + "'"
#print(sta_period)
#print(end_period)

# I also include some root histogram in case some plot are needed..
fileName = "QC8_HV_monitor_start_"+start+"_end_"+end+".root"
f1=ROOT.TFile( fileName,"RECREATE")

#boards must be 15 (from 0 to 14) because in the DB the board 15 is not declared
insertedBoards = 15
insertedChannels = 14

#insert the list of chambers in DCS convention
howManyChambers = raw_input("Tell me how many chambers you are using\n")
type(howManyChambers)

chamberList = []
print ("Tell me the chambers' names in DCS convention (for example 1-2-Top)")

for cont in range(int(howManyChambers)):
	chamberName = raw_input("Chamber: ")
	type(chamberName)
	chamberName = chamberName.replace("-","_")
	chamberList.append(chamberName)

print(chamberList)

indexB=0
indexC=0
counter=0
howMany345 = 0
howMany6789 = 0
howMany10 = 0
howMany11 = 0
mismatch=0
mismatch2=0
mismatch3=0
mismatch4=0
mismatch5=0
mismatch6=0
#bits of the error status
nBit = 12

ImonTh1List = []
VmonTh1List = []
SmonTh1List = []
SmonMeaningListList = [] #a list of lists (one list for each channel of each board considered)
			 # each of the inner lists has the meaning of the status

ImonTgraph1List = []
VmonTgraph1List = []
SmonTgraph1List = []

ChannelMapList = [ "Top_G3Bot", "Top_G3Top", "Top_G2Bot", "Top_G2Top", "Top_G1Bot", "Top_G1Top", "Top_Drift", "Bot_G3Bot", "Bot_G3Top", "Bot_G2Bot", "Bot_G2Top", "Bot_G1Bot", "Bot_G1Top", "Bot_Drift"]

#MainframeMapList and BoardMapList lists follow the order of ChamberMapList
ChamberMapList = [ "1_1", "1_2", "1_3", "2_1", "2_2", "2_3", "3_1", "3_2", "3_3", "4_1", "4_2", "4_3", "5_1", "5_2", "5_3" ]
MainframeMapList = [ "904_HV_mainframe",  "904_HV_mainframe",  "904_HV_mainframe",  "904_HV_mainframe",  "904_HV_mainframe",  "904_HV_mainframe",  "904_HV_mainframe",  "904_HV_mainframe",  "904_HV_mainframe", "904_Shared_mainframe",  "904_Shared_mainframe",  "904_Shared_mainframe",  "904_Shared_mainframe",  "904_Shared_mainframe",  "904_Shared_mainframe" ]
BoardMapList = [ "board00", "board01", "board02", "board03", "board04", "board05", "board06", "board07", "board08", "board10", "board14", "board15", "board11", "board12", "board13" ]


channelList = [ "G3Bot", "G3Top", "G2Bot", "G2Top", "G1Bot", "G1Top", "Drift"]

for indexB in range(len(chamberList)): #loop on the selected boards
	#create directories
        firstDir = f1.mkdir("Chamber"+chamberList[indexB])
        firstDir.cd()
	
	for indexC in range(len(channelList)): #ok for channels from 0 to 6
		#if indexB < 10:
       		#	NameB = "board0"+str(indexB) #board in the format board04
		#elif indexB >= 10:
       		#	NameB = "board"+str(indexB) #board in the format board04
	
		#if indexC < 10:
       		#	NameC = "channel00"+str(indexC) #channel in format channel002
		#elif indexC >=10:
       		#	NameC = "channel0"+str(indexC)
					
		#create directories
		secondDir = firstDir.mkdir("Channel"+channelList[indexC])
		secondDir.cd()
		
		#print("indexB="+str(indexB)+" indexC="+str(indexC)) 
		#th1List.append(NameB+" "+NameC) 

		#set bin size
		IMinHV = -10		#uA
		IMaxHV = 10  		#uA
		IResolutionHV = 0.02 	#uA
		INbinHV = int((IMaxHV - IMinHV)/IResolutionHV) 
		
		Imonh1 = ROOT.TH1F("HV_ImonChamber"+chamberList[indexB]+"_"+channelList[indexC]+"_TH1","HV_ImonChamber"+chamberList[indexB]+"_"+channelList[indexC]+"_TH1", INbinHV, IMinHV, IMaxHV)	
		Imonh1.GetXaxis().SetTitle("I [uA]")
                Imonh1.GetYaxis().SetTitle("counts")

		#set bin size	
		VMinHV = -50		#V
                VMaxHV = 2000  		#V
                VResolutionHV = 0.02 	#V
                VNbinHV = int((VMaxHV - VMinHV)/VResolutionHV) 
	
		Vmonh1 = ROOT.TH1F("HV_VmonChamber"+chamberList[indexB]+"_"+channelList[indexC]+"_TH1","HV_VmonChamber"+chamberList[indexB]+"_"+channelList[indexC]+"_TH1",VNbinHV,VMinHV,VMaxHV)	
		Vmonh1.GetXaxis().SetTitle("V [V]")
                Vmonh1.GetYaxis().SetTitle("counts")

		ImonTh1List.append(Imonh1)
		VmonTh1List.append(Vmonh1)
		
		#I define 5 status categories
		#type 0: off (bit 0)
		#type 1: on (bit 0)
		#type 2: RUP (bit 1), RDW (bit 2)
		#type 3: OVC (3), OVV (4), UVV (5)
		#type 4: etx trip (6), MAX V (7), EXT disable (8), Internal Trip (9), calibration error(10)
		#type 5: calib error (10)
		#type 6: unplugged (11)
		
		Smonh1 = ROOT.TH1F("HV_StatusChamber"+chamberList[indexB]+"_"+channelList[indexC]+"_TH1","HV_StatusChamber"+chamberList[indexB]+"_"+channelList[indexC]+"_TH1",9,-1, 8)	
                Smonh1.GetXaxis().SetTitle("Status cathegory")
                Smonh1.GetYaxis().SetTitle("counts")

		SmonTh1List.append(Smonh1)

		SmonMeaningList = []
#print(ImonTh1List)
#print("ImonTh1List lenght ="+str(len(ImonTh1List)))
#print("VmonTh1List lenght ="+str(len(VmonTh1List)))

#now I call channels and boards to fill them one by one

#for boardN in range(insertedBoards): #ok for boards from 0 to 15
#	for channelN in range(insertedChannels): #ok for channels from 0 to 13
		
		#find the number of the board from the name		
		indexTB = 0
		for form1 in ChamberMapList:
			form2 = chamberList[indexB][:-4] #remove -Top or -Bot from the name to make a match
			#print("form1 e form2:", form1, form2)
			isMatch = False
			if form2 == form1:
				isMatch = True
				if indexTB < 10:
					board = "board0"+str(indexTB) #board in the format board04
				elif indexTB >= 10:
					board = "board"+str(indexTB) #board in the format board04
			if isMatch == True:
				break

			indexTB = indexTB +1


	
		#print("board", board)
		
		#add 7 for bot chambers (from 7 to 13), top (0-6)
		
		indexTC = indexC
		if chamberList[indexB][4:] == "Bot":
			indexTC = indexC + 7

		if indexTC < 10:
			channel = "channel00"+str(indexTC) #channel in format channel002
		elif indexTC >=10:
			channel = "channel0"+str(indexTC)

		#indexTB is the posiion in the list when the required chamber is found
		print (MainframeMapList[indexTB], " ", BoardMapList[indexTB], " ", channel)
		#print (board, " ", channel)
		len(chamberList)
		len(channelList)
		
		#print ("counter:", counter)
		
		# this 3 parameters can be input to the script
		
		imon_name="'cms_gem_dcs_1:CAEN/"+MainframeMapList[indexTB]+"/"+BoardMapList[indexTB]+"/"+channel+".actual.iMon'"
                vmon_name="'cms_gem_dcs_1:CAEN/"+MainframeMapList[indexTB]+"/"+BoardMapList[indexTB]+"/"+channel+".actual.vMon'"
                status_name="'cms_gem_dcs_1:CAEN/"+MainframeMapList[indexTB]+"/"+BoardMapList[indexTB]+"/"+channel+".actual.status'"
		#imon_name="'cms_gem_dcs_1:CAEN/904_HV_mainframe/"+board+"/"+channel+".actual.iMon'"
		#vmon_name="'cms_gem_dcs_1:CAEN/904_HV_mainframe/"+board+"/"+channel+".actual.vMon'"
		#status_name="'cms_gem_dcs_1:CAEN/904_HV_mainframe/"+board+"/"+channel+".actual.status'"

		#this is the connection to DB, and the contact point to DB should be input to the script 
		#to avoid the have explicitely the pw in the script (lo schema e' il primo campo, la parte a destra e' il server) 
		db = cx_Oracle.connect('GEM_904_COND/904CondDB@INT2R')
		cur=db.cursor()

		#query =  "select ELEMENT_ID, ELEMENT_NAME from ELEMENTS"
		#cur.execute(query)
		#for rname in cur:
		#   print rname

		#ELEMENTS is the table in the DB
		#ELEMENT_ID and also ELEMENT_NAME are fields in the table
		#where ELEMENT_NAME is the row of the column ELEMENT_ID

		# this a tytpical query to extract the ELEMENT_ID from the  ELEMENT_NAME.
		# iMon element
		query = "select ELEMENT_ID from ELEMENTS where ELEMENT_NAME="+imon_name
		cur.execute(query)
		imon_id = cur.fetchone()[0];

		# vMon element
		query = "select ELEMENT_ID from ELEMENTS where ELEMENT_NAME="+vmon_name
		cur.execute(query)
		vmon_id = cur.fetchone()[0];
		
		# status element
		query = "select ELEMENT_ID from ELEMENTS where ELEMENT_NAME="+status_name
		cur.execute(query)
		status_id = cur.fetchone()[0];

		print "IMON_ID ", imon_id," VMON_ID ", vmon_id," STATUS_ID ", status_id
		
		#do the query to fill the Histos with I
		#fill current
		query = "select TS,VALUE_NUMBER from EVENTHISTORY where ELEMENT_ID = "+str(imon_id)+" and TS > to_date ("+sta_period+",'YYYY-MM-DD HH24:MI:SS') and TS < to_date ("+end_period+",'YYYY-MM-DD HH24:MI:SS')"
		cur.execute(query)                                                                                                                             
		curimon=cur
		imonRec=[]
		imonOnlyT = array ( 'd' )
		imonOnlyI = array ( 'd' )
		contatoreI = 0
		isNotEmptyImon = False
		for result in curimon:
		   #start ts: the first read Ts
                   if contatoreI == 0:
                        #print("dentroI", contatoreI)
                        startTsImon = result[0]
		   isNotEmptyImon = True
		   ImonTh1List[counter].Fill(result[1])
		   imonRec+=[(result[0],result[1],"Imon")]
		   #print("startTsImon",startTsImon, "present ts", result[0])
                   currentTsImon = result[0] #put the present TS value in currentTsImon
                   #print("TSImon", currentTsImon-startTsImon)
                   #micro=(currentTsImon-startTsImon).microseconds
                   tot_secondsImon = (currentTsImon-startTsImon).total_seconds()
                   #print("micro=", micro)
                   #print("totsecImon=", tot_secondsImon)
                   tot_milliImon=tot_secondsImon*1000.
                   #print("totmilliImon=", tot_milliImon)
                   #print(imonRec[contatoreI])
		   
		   #lists with only I and t
		   imonOnlyT.append(tot_secondsImon)
		   imonOnlyI.append(result[1])
		   
                   contatoreI=contatoreI+1

		ImonTh1List[counter].Write()
	
		#create a TGraph for Imon (I vs time)
		if len(imonOnlyT) != len(imonOnlyI):
			print ("filling vector different lenght")
			file = open("HVErr.log", "w")
                        file.write("ERROR: imonOnlyT and imonOnlyV have different lenght")
                        file.close()

		#sort the array of imonOnlyT and the imonOnlyV
                #in the case the query is not executed in order (negative times)
                #pair the time with status and the meaning list
                SortListI = []
                for sortCountI in range(len(imonOnlyT)):
                	internalListI = (imonOnlyT[sortCountI], imonOnlyI[sortCountI])
                	SortListI.append(internalListI)
                                                                                                                
                #print(SortListI)
                SortListI = sorted(SortListI, key=lambda elementI: elementI[0])
                #print(SortListI)
                
                for refillI in range(len(imonOnlyT)):
                	imonOnlyT[refillI]=SortListI[refillI][0]
                	imonOnlyI[refillI]=SortListI[refillI][1]
                                                                                                                
                #print(imonOnlyT)
                #print(imonOnlyI)
                
                #rescale the negative times
		if (len(imonOnlyT))==0:
			print("imonOnlyT lenght", len(imonOnlyT))
			print("------------------------------------------------------------------")
			print("ERROR: there are no I current data for chamber "+ chamberList[indexB]+ " channel "+ channelList[indexC])
			print("------------------------------------------------------------------")
		
			file = open("HVErr.log", "w") 
			file.write("ERROR: there are no I current data for chamber "+ chamberList[indexB]+ " channel "+ channelList[indexC]) 
			file.close() 
			
				
			continue
			

                negativeStartI = imonOnlyT[0]
                if imonOnlyT[0] < 0:
                	for iterTimeI in range(len(imonOnlyT)):
                		imonOnlyT[iterTimeI] = imonOnlyT[iterTimeI] + negativeStartI*(-1)
                #print(imonOnlyT)


		#Imontg1 = ROOT.TGraph(n,x,y); x and y is the name of arrays with numbers of time and I
		Imontg1 = ROOT.TGraph(len(imonOnlyT),imonOnlyT,imonOnlyI)
   		Imontg1.SetLineColor(2)
		Imontg1.SetLineWidth(4)
		Imontg1.SetMarkerColor(4)
		Imontg1.SetMarkerStyle(21)
		Imontg1.SetMarkerSize(1)
		Imontg1.SetName("HV_ImonChamber"+chamberList[indexB]+"_"+channelList[indexC]+"_time")
		Imontg1.SetTitle("HV_ImonChamber"+chamberList[indexB]+"_"+channelList[indexC]+"_time")
		Imontg1.GetXaxis().SetTitle("time [s]")
		Imontg1.GetYaxis().SetTitle("Imon "+chamberList[indexB]+" "+channelList[indexC]+" [uA]")
		#Imontg1.Draw("ACP")

		#ImonTgraph1List += [Imontg1]
		ImonTgraph1List.append(Imontg1)
		ImonTgraph1List[counter].Write()	

		#fill Voltage
		query = "select TS,VALUE_NUMBER from EVENTHISTORY where ELEMENT_ID = "+str(vmon_id)+" and TS > to_date ("+sta_period+",'YYYY-MM-DD HH24:MI:SS') and TS < to_date ("+end_period+",'YYYY-MM-DD HH24:MI:SS')"
		cur.execute(query)
		
		#result[0] is the present TS
		#result[1] is the voltage
		curvmon=cur
		vmonRec=[]
		vmonOnlyT = array ( 'd' )
                vmonOnlyV = array ( 'd' )
		contatoreV = 0
		isNotEmptyVmon = False
		for result in curvmon:
		   #start ts: the first read Ts
		   if contatoreV == 0: 
	   	   	#print("dentroV", contatoreV)
		   	startTsVmon = result[0]
		   isNotEmptyVmon = True
		   VmonTh1List[counter].Fill(result[1])
		   vmonRec+=[(result[0],result[1],"Vmon")]
		   #print("startTsVmon",startTsVmon, "present ts", result[0])
		   currentTsVmon = result[0] #put the present TS value in currentTsVmon
		   #print("TSVmon", currentTsVmon-startTsVmon)
		   #micro=(currentTsVmon-startTsVmon).microseconds
		   tot_secondsVmon = (currentTsVmon-startTsVmon).total_seconds()
		   #print("micro=", micro)
		   #print("totsecVmon=", tot_secondsVmon)
		   tot_milliVmon=tot_secondsVmon*1000.
		   #print("totmilliVmon=", tot_milliVmon)
		   #print(vmonRec[contatoreV])
		   contatoreV=contatoreV+1
		
		   #lists with only V and t
                   vmonOnlyT.append(tot_secondsVmon)
                   vmonOnlyV.append(result[1])

		VmonTh1List[counter].Write()
		
		#create a TGraph for Imon (V vs time)
                if len(vmonOnlyT) != len(vmonOnlyV):
                	print ("filling vector different lenght")
			file = open("HVErr.log", "w")
                        file.write("ERROR: vmonOnlyT and vmonOnlyV have different lenght")
                        file.close()




		#sort the array of vmonOnlyT and the vmonOnlyV
                #in the case the query is not executed in order (negative times)
                #pair the time with status and the meaning list
                SortListV = []
                for sortCountV in range(len(vmonOnlyT)):
                	internalListV = (vmonOnlyT[sortCountV], vmonOnlyV[sortCountV])
                	SortListV.append(internalListV)
                                                                                                                
                #print(SortListV)
                SortListV = sorted(SortListV, key=lambda elementV: elementV[0])
                #print(SortListV)
                
                for refillV in range(len(vmonOnlyT)):
                	vmonOnlyT[refillV]=SortListV[refillV][0]
                	vmonOnlyV[refillV]=SortListV[refillV][1]
                                                                                                                
                #print(vmonOnlyT)
                #print(vmonOnlyV)
               
		if (len(vmonOnlyT))==0:
			print("vmonOnlyT lenght", len(vmonOnlyT))
                	print("------------------------------------------------------------------")
                	print("ERROR: there are no HV voltage data for chamber "+ chamberList[indexB]+ " channel "+ channelList[indexC])
                	print("------------------------------------------------------------------")
                
                	file = open("HVErr.log", "w") 
                	file.write("ERROR: there are no HV voltage data for chamber "+ chamberList[indexB]+ " channel "+ channelList[indexC]) 
                	file.close() 
                	
                		
                	continue

 
                #rescale the negative times
                negativeStartV = vmonOnlyT[0]
                if vmonOnlyT[0] < 0:
                	for iterTimeV in range(len(vmonOnlyT)):
                		vmonOnlyT[iterTimeV] = vmonOnlyT[iterTimeV] + negativeStartV*(-1)
                #print(vmonOnlyT)


                #Vmontg1 = ROOT.TGraph(n,x,y); x and y is the name of arrays with numbers of time and V
                Vmontg1 = ROOT.TGraph(len(vmonOnlyT),vmonOnlyT,vmonOnlyV)
                Vmontg1.SetLineColor(2)
                Vmontg1.SetLineWidth(4)
                Vmontg1.SetMarkerColor(4)
                Vmontg1.SetMarkerStyle(21)
		Vmontg1.SetMarkerSize(1)
                Vmontg1.SetName("HV_VmonChamber"+chamberList[indexB]+"_"+channelList[indexC]+"_time")
                Vmontg1.SetTitle("HV_VmonChamber"+chamberList[indexB]+"_"+channelList[indexC]+"_time")
                Vmontg1.GetXaxis().SetTitle("time [s]")
                Vmontg1.GetYaxis().SetTitle("Vmon "+chamberList[indexB]+" "+channelList[indexC]+" [V]")
                #Vmontg1.Draw("ACP")

                #VmonTgraph1List += [Vmontg1]
                VmonTgraph1List.append(Vmontg1)
                VmonTgraph1List[counter].Write()
		
		#status query
		query = "select TS,VALUE_NUMBER from EVENTHISTORY where ELEMENT_ID = "+str(status_id)+" and TS > to_date ("+sta_period+",'YYYY-MM-DD HH24:MI:SS') and TS < to_date ("+end_period+",'YYYY-MM-DD HH24:MI:SS')"
		cur.execute(query)                                                                                                                             
		curstat=cur
		statRec=[]
		smonOnlyT = array ( 'd' )
		smonOnlyS = array ( 'd' )
		smonOnlyBinStat = []
		smonOnlyMeaningStat = []
		contatoreS = 0
		isNotEmptySmon = False
		for result in curstat:
		   #print ("nel for")
		   if contatoreS == 0:
		   	#print("dentroS", contatoreS)
		   	startTsSmon = result[0]
		   isNotEmptySmon = True
		   statRec+=[(result[0],result[1],"Status")]
		   #print ( "time", result[0], "status", result[1]  )
		   #print ("statusbin", bin(int(result[1])))
		   currentTsSmon = result[0] #put the present TS value in currentTsSmon
		   tot_secondsSmon = (currentTsSmon-startTsSmon).total_seconds()	
		   #use milli seconds to sort the time vector (at the end)
		   tot_milliSmon=int(tot_secondsSmon*1000.) 
	 
		   #print a 12 bit binary status number
		   binStat = bin(int(result[1]))[2:] #to take away the 0b in front of the binary number
		   lenStat = len(binStat)
		   binStat = str(0) * (nBit - lenStat) + binStat	
		   binStat = "0b"+binStat	
		   smonOnlyBinStat.append(binStat)
		   #print("time", result[0], "status bin", binStat )
		   #print("status totseconds", tot_secondsSmon)		  

		   extensibleStat = ""
		   #if len(binStat) != 14:
		   	#mismatch = mismatch + 1 
		   #masks for the bins
		   if binStat == "0b000000000000": #these are binary numbers
		   	channelStat = 0 #zero type of status (OFF)
		   	#print("channel status OFF")
		   	StatusMeaning = "OFF"
		   	extensibleStat = extensibleStat + StatusMeaning + " "
		   	#print(StatusMeaning)

		   if binStat == "0b000000000001": #these are binary numbers
		   	channelStat = 1 #first type of status (ON)
		   	#print("channel status ON")
		   	StatusMeaning = "ON"
		   	extensibleStat = extensibleStat + StatusMeaning + " "
		   	#print(StatusMeaning)

		   #bin produces a string (so the operation >> can be only made only on int)
		   #I observe the bin number with bin(shift2)
		   #I shift of one bit to delete the bit 0 from the string
		   shift2 = binStat[:-1]
		   
		   #print("binStat:", binStat, "shift2:", shift2 )
		   if len(shift2) != 13:
		   	mismatch2 = mismatch2 + 1
		   
		   #for the second status cathegory I need the last two bins of shift2
		   #print ( "shift2", shift2, "bin 1 and 2", shift2[11:])
		   if int(shift2[11:]) > 0:
		   	#print (shift2[11:])
		   	channelStat = 2 #second type of status
		   	cutBinStr = shift2[11:]
		   	if cutBinStr[1] == "1": #if I have RUP
		   		StatusMeaning = "RUP"
		   		extensibleStat = extensibleStat + StatusMeaning + " "
		   		#print(StatusMeaning)
		   	elif cutBinStr[0] == "1": #if I have RDW
		   		StatusMeaning = "RDW"
		   		extensibleStat = extensibleStat + StatusMeaning + " "
		   		#print(StatusMeaning)
		   
		   #third status 
		   shift3 = binStat[:-3] 
		   if len(shift3) != 11:
                        mismatch3 = mismatch3 + 1
		   
		   #print ( "shift3", shift3, "bin 3, 4, 5", shift3[8:])
		   if int(shift3[8:]) > 0:
		   	#print (shift3[8:])
		   	#howMany345 = howMany345 + 1 
		   	channelStat = 3 #third type of status  
		   	cutBinStr = shift3[8:]
                        if cutBinStr[2] == "1": #if I have OVC
                                StatusMeaning = "OVC"
		   		extensibleStat = extensibleStat + StatusMeaning + " "
		   		#print(StatusMeaning)
                        elif cutBinStr[1] == "1": #if I have OVV
                                StatusMeaning = "OVV"
		   		extensibleStat = extensibleStat + StatusMeaning + " "
		   		#print(StatusMeaning)
		   	elif cutBinStr[0] == "1": #if I have UVV
		   		StatusMeaning = "UVV"
		   		extensibleStat = extensibleStat + StatusMeaning + " "
		   		#print(StatusMeaning)

		   #fourth status                                        
                   shift4 = binStat[:-6] 
                   if len(shift4) != 8:
                        mismatch4 = mismatch4 + 1
                   
                   #print ( "shift4", shift4, "bin 6, 7, 8, 9", shift4[4:])
                   if int(shift4[4:]) > 0:
                   	#print (shift4[4:])
                   	howMany6789 = howMany6789 + 1 
                   	channelStat = 4 #fourth type of status  
		   	cutBinStr = shift4[4:]
                        if cutBinStr[3] == "1": #if I have Ext Trip
                                StatusMeaning = "Ext Trip"
		   		extensibleStat = extensibleStat + StatusMeaning + " "
		   		#print(StatusMeaning)
                        elif cutBinStr[2] == "1": #if I have Max V
                                StatusMeaning = "Max V"
		   		extensibleStat = extensibleStat + StatusMeaning + " "
		   		#print(StatusMeaning)
                        elif cutBinStr[1] == "1": #if I have Ext Disable
                                StatusMeaning = "Ext Disable"
		   		extensibleStat = extensibleStat + StatusMeaning + " "
		   		#print(StatusMeaning)
		   	elif cutBinStr[0] == "1": #if I have Int Trip
                                StatusMeaning = "Int Trip"
		   		extensibleStat = extensibleStat + StatusMeaning + " "
		   		#print(StatusMeaning)

		   #fifth status                                              
                   shift5 = binStat[:-10] 
                   if len(shift5) != 4:
                        mismatch5 = mismatch5 + 1
                   
                   #print ( "shift5", shift5, "bin 10", shift5[3:])
                   if int(shift5[3:]) > 0:
                   	#print (shift5[3:])
                   	howMany10 = howMany10 + 1 
                   	channelStat = 5 #fifth type of status  
		   	cutBinStr = shift5[3:]
                        if cutBinStr[0] == "1": #if I have Calib Error
                                StatusMeaning = "Calib Error"
		   		extensibleStat = extensibleStat + StatusMeaning + " "
		   		#print(StatusMeaning)

		   #sixth status                                              
                   shift6 = binStat[:-11] 
                   if len(shift6) != 3:
                        mismatch6 = mismatch6 + 1
                   
                   #print ( "shift6", shift6, "bin 11", shift6[2:])
                   if int(shift6[2:]) > 0:
                   	#print (shift6[2:])
                   	howMany11 = howMany11 + 1 
                   	channelStat = 6 #fifth type of status  
                   	cutBinStr = shift6[2:]
                        if cutBinStr[0] == "1": #if I have Unplugged
                                StatusMeaning = "Unplugged"
		   		extensibleStat = extensibleStat + StatusMeaning + " "
		   		#print(StatusMeaning)
		   
		   #list S and T for the tgraph status vs time (millisecond int)
		   smonOnlyT.append(tot_secondsSmon)
		   smonOnlyS.append(channelStat)
		   smonOnlyMeaningStat.append(extensibleStat)
		   		   
		   #th1 for status
		   SmonTh1List[counter].Fill(channelStat)
   
		   SmonMeaning = ("StatChamber"+chamberList[indexB]+"_"+channelList[indexC], "time:"+str(result[0]), "Status:"+StatusMeaning )
		   SmonMeaningList.append(SmonMeaning)
		   
		   
		   contatoreS=contatoreS+1 
		
		#th1 status
		SmonTh1List[counter].Write()
		
		#tgraph status
		if len(smonOnlyT) != len( smonOnlyS ):
			print("!!!!!error tgraph status: filling with lists of different lenght!!!!!")
			file = open("HVErr.log", "w")
                        file.write("ERROR: smonOnlyT and smonOnlyS have different lenght")
                        file.close()
		#sort the array of smonOnly and the smonOnly
		#in the case the query is not executed in order (negative times)
		#pair the time with status and the meaning list
		SortList = []
		for sortCount in range(len(smonOnlyT)):
			internalList = (smonOnlyT[sortCount], smonOnlyS[sortCount], SmonMeaningList[sortCount])
			SortList.append(internalList)

		#print(SortList)
		SortList = sorted(SortList, key=lambda element: element[0])
		#print(SortList)
		
		for refill in range(len(smonOnlyT)):
			smonOnlyT[refill]=SortList[refill][0]
			smonOnlyS[refill]=SortList[refill][1]
			SmonMeaningList[refill] = SortList[refill][2]
	
		#print(smonOnlyT)
		#print(smonOnlyS)
		#print(SmonMeaningList)
	

		if (len(smonOnlyT))==0:
                	print("smonOnlyT lenght", len(smonOnlyT))
                	print("------------------------------------------------------------------")
                	print("ERROR: there are no status data for chamber "+ chamberList[indexB]+ " channel "+ channelList[indexC])
                	print("------------------------------------------------------------------")
                
                	file = open("HVErr.log", "w") 
                	file.write("ERROR: there are no status data for chamber "+ chamberList[indexB]+ " channel "+ channelList[indexC]) 
                	file.close() 
                	
                		
                	continue


	
		#rescale the negative times
		negativeStart = smonOnlyT[0]
		if smonOnlyT[0] < 0:
			for iterTime in range(len(smonOnlyT)):
				smonOnlyT[iterTime] = smonOnlyT[iterTime] + negativeStart*(-1)
		#print(smonOnlyT)
		
		#Smontg1 = ROOT.TGraph(n,x,y); x and y is the name of arrays with numbers of time and V
                Smontg1 = ROOT.TGraph(len(smonOnlyT),smonOnlyT,smonOnlyS)
                Smontg1.SetLineColor(2)
                Smontg1.SetLineWidth(4)
                Smontg1.SetMarkerColor(4)
                Smontg1.SetMarkerStyle(21)
                Smontg1.SetMarkerSize(1)
                Smontg1.SetName("HV_StatusChamber"+chamberList[indexB]+"_"+channelList[indexC]+"_time")
                Smontg1.SetTitle("HV_StatusChamber"+chamberList[indexB]+"_"+channelList[indexC]+"_time")
                Smontg1.GetXaxis().SetTitle("time [s]")
                Smontg1.GetYaxis().SetTitle("status cathegory "+chamberList[indexB]+" "+channelList[indexC])
                #Smontg1.Draw("ACP")

		SmonTgraph1List.append(Smontg1)
                SmonTgraph1List[counter].Write()

		#List with all status
		SmonMeaningListList.append(SmonMeaningList)
		#print(SmonMeaningListList[counter])		
		
		#tree for the status
		StatusTree = ROOT.TTree("HV_StatusTree"+chamberList[indexB]+"_"+channelList[indexC], "HV_StatusTree"+chamberList[indexB]+"_"+channelList[indexC]) 

		smonRootTimes = ROOT.vector('float')()
		smonRootBinStat	= ROOT.vector('string')()
		smonRootMeaningStat = ROOT.vector('string')()
		
		StatusTree.Branch( 'TS', smonRootTimes )	
		StatusTree.Branch( 'BinaryStat', smonRootBinStat )	
		StatusTree.Branch( 'MeaningStat', smonRootMeaningStat )	

		for lungh in range(len( smonOnlyT )):
			smonRootTimes.push_back( smonOnlyT[lungh] )
			smonRootBinStat.push_back( smonOnlyBinStat[lungh] )
			smonRootMeaningStat.push_back( smonOnlyMeaningStat[lungh] )

		StatusTree.Fill()
		
		StatusTree.Write()
			
		#FINAL COUNTER
		counter = counter + 1

#f1.Write()

f1.Close()

print('\n-------------------------Output--------------------------------')
print(fileName+ " has been created.")
print("It is organised in directories: to change directory use DIRNAME->cd()")
print('To draw a TH1 or a TGraph: OBJNAME->Draw()')
print('To scan the root file use for example:\nHV_StatusTree2_2_Top_G3Bot->Scan("","","colsize=30")')

#print("mismatch", mismatch)
#print("mismatch2", mismatch2)
#print("mismatch3", mismatch3)
#print("mismatch4", mismatch4)
#print("mismatch5", mismatch5)
#print("mismatch6", mismatch6)
#print("howMany345", howMany345)
#print("howMany6789", howMany6789)
#print("howMany10", howMany10)
#print("howMany11", howMany11)


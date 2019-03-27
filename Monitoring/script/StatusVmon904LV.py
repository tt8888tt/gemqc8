import cx_Oracle
import ROOT
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
fileName = "QC8_LV_monitor_start_"+start+"_end_"+end+".root"
f1=ROOT.TFile( fileName,"RECREATE")

#boards must be 15 (from 0 to 14) because in the DB the board 15 is not declared
#in the LV we have only board 00 04 08 12 16
insertedBoards = 5
insertedChannels = 6

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

#print(chamberList)

indexB=0
indexC=0
counter=0
mismatch=0
mismatch2=0
mismatch3=0
mismatch4=0
mismatch5=0
mismatch6=0
mismatch7=0
mismatch8=0
mismatch9=0
mismatch10=0
mismatch11=0
#bits of the error status
nBit = 16

ImonTh1List = []
VmonTh1List = []
SmonTh1List = []
SmonMeaningListList = [] #a list of lists (one list for each channel of each board considered)
			 # each of the inner lists has the meaning of the status

ImonTgraph1List = []
VmonTgraph1List = []
SmonTgraph1List = []

ChamberMapList = [ "1_1_Top", "1_1_Bot", "1_2_Top", "1_2_Bot", "1_3_Top", "1_3_Bot", "2_1_Top", "2_1_Bot", "2_2_Top", "2_2_Bot", "2_3_Top", "2_3_Bot", "3_1_Top", "3_1_Bot", "3_2_Top", "3_2_Bot", "3_3_Top", "3_3_Bot", "4_1_Top", "4_1_Bot", "4_2_Top", "4_2_Bot", "4_3_Top", "4_3_Bot", "5_1_Top", "5_1_Bot", "5_2_Top", "5_2_Bot", "5_3_Top", "5_3_Bot" ]
BoardMapList = [ "00", "00", "00", "00", "00", "00", "04", "04", "04", "04", "04", "04", "08", "08", "08", "08", "08", "08", "12", "12", "12", "12", "12", "12", "16", "16", "16", "16", "16", "16" ]
ChannelMapList = [ "000", "001", "002", "003", "004", "005", "000", "001", "002", "003", "004", "005", "000", "001", "002", "003", "004", "005", "000", "001", "002", "003", "004", "005", "000", "001", "002", "003", "004", "005" ]

for indexB in range(len(chamberList)): #loop on the selected boards
	#create directories
        firstDir = f1.mkdir("LV_Chamber"+chamberList[indexB])
        firstDir.cd()
	
	#print("indexB="+str(indexB))
	#th1List.append(NameB)                                                                                                                                         
        Imonh1 = ROOT.TH1F("LV_ImonChamber"+chamberList[indexB]+"_TH1","LV_ImonChamber"+chamberList[indexB]+"_TH1",100,10,10)	
        Imonh1.GetXaxis().SetTitle("I [uA]")
        Imonh1.GetYaxis().SetTitle("counts")
        		
        Vmonh1 = ROOT.TH1F("LV_VmonChamber"+chamberList[indexB]+"_TH1","LV_VmonChamber"+chamberList[indexB]+"_TH1",100,0,2000)	
        Vmonh1.GetXaxis().SetTitle("V [V]")
        Vmonh1.GetYaxis().SetTitle("counts")
        
        ImonTh1List.append(Imonh1)
        VmonTh1List.append(Vmonh1)

	#print(len(ChamberMapList))
	#print(len(BoardMapList))

	#I define 5 status categories
        #type 0: off (bit 0)
        
        Smonh1 = ROOT.TH1F("LV_StatusChamber"+chamberList[indexB]+"_TH1","LV_StatusChamber"+chamberList[indexB]+"_TH1",20,-1, 19)	
        Smonh1.GetXaxis().SetTitle("Status cathegory")
        Smonh1.GetYaxis().SetTitle("counts")
                                                                                                                                                                                 
        SmonTh1List.append(Smonh1)
                                                                                                                                                                                 
        SmonMeaningList = []


	#find the number of the board from the name		
        indexTB = 0
        for form1 in ChamberMapList:
        	form2 = chamberList[indexB] #remove -Top or -Bot from the name to make a match
        	#print("form1 e form2:", form1, form2)
        	isMatch = False
        	if form2 == form1:
        		isMatch = True
        		board = "Board"+BoardMapList[indexTB]#board in the format board04
			channel = "channel"+ChannelMapList[indexTB]
        	indexTB = indexTB +1
        	if isMatch == True:
        		break
        #print(indexTB) 
        print("Board", board, "channel", channel)

	#print ("counter:", counter)
        
        # this 3 parameters can be input to the script
	imon_name="'cms_gem_dcs_1:CAEN/904_Shared_mainframe/branchController00/easyCrate0/easy"+board+"/"+channel+".actual.iMon'"
	vmon_name="'cms_gem_dcs_1:CAEN/904_Shared_mainframe/branchController00/easyCrate0/easy"+board+"/"+channel+".actual.vMon'"
	status_name="'cms_gem_dcs_1:CAEN/904_Shared_mainframe/branchController00/easyCrate0/easy"+board+"/"+channel+".actual.status'"
                                                                                                                           
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
        Imontg1.SetName("LV_ImonChamber"+chamberList[indexB]+"_time")
        Imontg1.SetTitle("LV_ImonChamber"+chamberList[indexB]+"_time")
        Imontg1.GetXaxis().SetTitle("time [s]")
        Imontg1.GetYaxis().SetTitle("Imon "+chamberList[indexB]+" [uA]")
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
        Vmontg1.SetName("LV_VmonChamber"+chamberList[indexB]+"_time")
        Vmontg1.SetTitle("LV_VmonChamber"+chamberList[indexB]+"_time")
        Vmontg1.GetXaxis().SetTitle("time [s]")
        Vmontg1.GetYaxis().SetTitle("Vmon "+chamberList[indexB]+" [V]")
        #Vmontg1.Draw("ACP")
                                                                                                         
        #VmonTgraph1List += [Vmontg1]
        VmonTgraph1List.append(Vmontg1)
        VmonTgraph1List[counter].Write()

	#LV boards (CAEN A3016 o A3016 HP)
        #Bit 0: ON/OFF
        #Bit 1: dont care
        #Bit 2: dont care
        #Bit 3: OverCurrent
        #Bit 4: OverVoltage
        #Bit 5: UnderVoltage
        #Bit 6: dont care
        #Bit 7: Over HVmax
        #Bit 8: dont care
        #Bit 9: Internal Trip
        #Bit 10: Calibration Error
        #Bit 11: Unplugged
        #Bit 12: dont care
        #Bit 13: OverVoltage Protection
        #Bit 14: Power Fail
        #Bit 15: Temperature Error

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
                                                                                                                                                                                                                     
           #print a 16 bit binary status number
           binStat = bin(int(result[1]))[2:] #to take away the 0b in front of the binary number
           lenStat = len(binStat)
           binStat = str(0) * (nBit - lenStat) + binStat	
           binStat = "0b"+binStat	
           smonOnlyBinStat.append(binStat)
           #print("time", result[0], "status bin", binStat )
           #print("status totseconds", tot_secondsSmon)		  
                                                                                                                                                                                                                     
           extensibleStat = ""
           if len(binStat) != (nBit + 2) :
           	mismatch = mismatch + 1 
           #masks for the bins
           if binStat == "0b0000000000000000": #these are binary numbers
           	channelStat = 0 #zero type of status (OFF)
           	#print("channel status OFF")
           	StatusMeaning = "OFF"
           	extensibleStat = extensibleStat + StatusMeaning + " "
           	#print(StatusMeaning)
                                                                                                                                                                                                                     
           if binStat == "0b0000000000000001": #these are binary numbers
           	channelStat = 1 #first type of status (ON)
           	#print("channel status ON")
           	StatusMeaning = "ON"
           	extensibleStat = extensibleStat + StatusMeaning + " "
	   	#print(StatusMeaning)
                                                                                                                                                                                                                     
           #bin produces a string (so the operation >> can be only made only on int)
           #I observe the bin number with bin(shift2)
           #I shift of one bit to delete the bit 0 from the string
	   removedBits = 0 - 1 #negative number
           shift2 = binStat[:removedBits]
           
           #print("binStat:", binStat, "shift2:", shift2 )
           if len(shift2) != (nBit + 2) + removedBits:
           	mismatch2 = mismatch2 + 1
          
	   #I have to remove bit 1 and 2 because they are not interesting
	   #len(shift2)-2    -2 because I want the last two bits
	   #print ( "shift2", shift2, "bin 1 and 2", shift2[len(shift2)-2:])
	  
	   #remove bit 1 and 2 : second status cathegory even if it is written mismatch 3: I removed the bits 
	   removedBits = removedBits - 2 #negative number
           shift3 = binStat[:removedBits]
           
           if len(shift3) != (nBit + 2) + removedBits:
           	mismatch3 = mismatch3 + 1

           #for the second status cathegory I need the last two bins of shift3
	   #print ( "shift3", shift3, "bit 3 4 5", shift3[len(shift3)-3:])
           if int(shift3[len(shift3)-3:]) > 0:
           	#print (shift3[len(shift3)-3:])
           	channelStat = 2 #second type of status
           	cutBinStr = shift3[len(shift3)-3:]
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

	   #remove bit 3 4 5
           removedBits = removedBits - 3 #negative number
           shift4 = binStat[:removedBits]
           
           if len(shift4) != (nBit + 2) + removedBits:
           	mismatch4 = mismatch4 + 1

	   #print ( "shift4", shift4, "bit 6", shift4[len(shift4)-1:])
	  
	   #remove bit 6
           removedBits = removedBits - 1 #negative number
           shift5 = binStat[:removedBits]
           
           if len(shift5) != (nBit + 2) + removedBits:
           	mismatch5 = mismatch5 + 1
                                                                                                               
           #for the third status cathegory I need the last four bins of shift5
	   #I dont register the bit 8 beacuse not interesting
           #print ( "shift5", shift5, "bit 7, 8, 9", shift5[len(shift5)-3:])
           if int(shift5[len(shift5)-3:]) > 0: 
           	#print (shift5[len(shift5)-3:])
           	channelStat = 3 #third type of status
           	cutBinStr = shift5[len(shift5)-3:]
           	if cutBinStr[2] == "1": #if I have OHVMax
           		StatusMeaning = "OHVMax"
           		extensibleStat = extensibleStat + StatusMeaning + " "
           		#print(StatusMeaning)
           	elif cutBinStr[0] == "1": #if I have INTTRIP
           		StatusMeaning = "InTrip"
           		extensibleStat = extensibleStat + StatusMeaning + " "
           		#print(StatusMeaning)
                

	   #remove bit 7 8 9 to do the fourth status cathegory
           removedBits = removedBits - 3 #negative number
           shift6 = binStat[:removedBits]
           
           if len(shift6) != (nBit + 2) + removedBits:
           	mismatch6 = mismatch6 + 1

	   #for the fourth status cathegory I need the last bit of shift6
           #print ( "shift6", shift6, "bit 10", shift6[len(shift6)-1:])
           if int(shift6[len(shift6)-1:]) > 0: 
           	#print (shift6[len(shift6)-1:])
           	channelStat = 4 #fourth type of status
           	cutBinStr = shift6[len(shift6)-1:]
                if cutBinStr[0] == "1": #if I have Calib Error
           		StatusMeaning = "CalibERR"
           		extensibleStat = extensibleStat + StatusMeaning + " "
           		#print(StatusMeaning)
                                                                              
           #remove bit 10
           removedBits = removedBits - 1 #negative number
           shift7 = binStat[:removedBits]
           
           if len(shift7) != (nBit + 2) + removedBits:
           	mismatch7 = mismatch7 + 1

                                                                                                               
           #for the fifth status cathegory I need the last bit of shift7
           #print ( "shift7", shift7, "bit 11", shift7[len(shift7)-1:])
           if int(shift7[len(shift7)-1:]) > 0: 
           	#print (shift7[len(shift7)-1:])
           	channelStat = 5 #fifth type of status
           	cutBinStr = shift7[len(shift7)-1:]
          	if cutBinStr[0] == "1": #if I have Unplugged
           		StatusMeaning = "Unplugged"
           		extensibleStat = extensibleStat + StatusMeaning + " "
           		#print(StatusMeaning)

	   #remove bit 11
           removedBits = removedBits - 1 #negative number
           shift8 = binStat[:removedBits]
           
           if len(shift8) != (nBit + 2) + removedBits:
           	mismatch8 = mismatch8 + 1
                                                                      
           #print ( "shift8", shift8, "bit 12", shift8[len(shift8)-1:])   #bit 12 not interesting

	   #remove bit 12 to do the sixth status cathegory
           removedBits = removedBits - 1 #negative number
           shift9 = binStat[:removedBits]
           
           if len(shift9) != (nBit + 2) + removedBits:
           	mismatch9 = mismatch9 + 1
                                                                                                               
           #for the sixth status cathegory I need the last bit of shift9
           #print ( "shift9", shift9, "bit 13", shift9[len(shift9)-1:])
           if int(shift9[len(shift9)-1:]) > 0: 
           	#print (shift9[len(shift9)-1:])
           	channelStat = 6 #sixth type of status
           	cutBinStr = shift9[len(shift9)-1:]
           	if cutBinStr[0] == "1": #if I have OVVPROT
           		StatusMeaning = "OVVPROT"
           		extensibleStat = extensibleStat + StatusMeaning + " "
           		#print(StatusMeaning)

	   #remove bit 13 to do the seventh status cathegory
           removedBits = removedBits - 1 #negative number
           shift10 = binStat[:removedBits]
           
           if len(shift10) != (nBit + 2) + removedBits:
           	mismatch10 = mismatch10 + 1
                                                                                                               
           #for the seventh status cathegory I need the last bit of shift10
           #print ( "shift10", shift10, "bit 14", shift10[len(shift10)-1:])
           if int(shift10[len(shift10)-1:]) > 0: 
           	#print (shift10[len(shift10)-1:])
           	channelStat = 7 #seventh type of status
           	cutBinStr = shift10[len(shift10)-1:]
           	if cutBinStr[0] == "1": #if I have POWFAIL
           		StatusMeaning = "POWFAIL"
           		extensibleStat = extensibleStat + StatusMeaning + " "
           		#print(StatusMeaning)

	   #remove bit 14 to do the eight status cathegory
           removedBits = removedBits - 1 #negative number
           shift11 = binStat[:removedBits]
           
           if len(shift11) != (nBit + 2) + removedBits:
           	mismatch11 = mismatch11 + 1
                                                                                                               
           #for the eight status cathegory I need the last bit of shift11
           #print ( "shift11", shift11, "bit 15", shift11[len(shift11)-1:])
           if int(shift11[len(shift11)-1:]) > 0: 
           	#print (shift11[len(shift11)-1:])
           	channelStat = 8 #eighth type of status
           	cutBinStr = shift11[len(shift11)-1:]
           	if cutBinStr[0] == "1": #if I have TEMPERR
           		StatusMeaning = "TEMPERR"
           		extensibleStat = extensibleStat + StatusMeaning + " "
           		#print(StatusMeaning)

	   #list S and T for the tgraph status vs time (millisecond int)
           smonOnlyT.append(tot_secondsSmon)
           smonOnlyS.append(channelStat)
           smonOnlyMeaningStat.append(extensibleStat)
           		   
           #th1 for status
           SmonTh1List[counter].Fill(channelStat)
                                                                                                                                       
           SmonMeaning = ("StatChamber"+chamberList[indexB], "time:"+str(result[0]), "Status:"+StatusMeaning )
           SmonMeaningList.append(SmonMeaning)
           
           
           contatoreS=contatoreS+1 
        
        #th1 status
        SmonTh1List[counter].Write()
        
        #tgraph status
        if len(smonOnlyT) != len( smonOnlyS ):
        	print("!!!!!error tgraph status: filling with lists of different lenght!!!!!")
                                                                                                                                       
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
        Smontg1.SetName("LV_StatusChamber"+chamberList[indexB]+"_time")
        Smontg1.SetTitle("LV_StatusChamber"+chamberList[indexB]+"_time")
        Smontg1.GetXaxis().SetTitle("time [s]")
        Smontg1.GetYaxis().SetTitle("status cathegory "+chamberList[indexB])
        #Smontg1.Draw("ACP")
                                                                                                                                       
        SmonTgraph1List.append(Smontg1)
        SmonTgraph1List[counter].Write()

	
	#List with all status
        SmonMeaningListList.append(SmonMeaningList)
        #print(SmonMeaningListList[counter])		
        
        #tree for the status
        StatusTree = ROOT.TTree("LV_StatusTree"+chamberList[indexB], "LV_StatusTree"+chamberList[indexB]) 
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

f1.Close()

print('\n-------------------------Output--------------------------------')
print( fileName + " has been created.")
print("It is organised in directories: to change directory use DIRNAME->cd()")
print('To draw a TH1 or a TGraph: OBJNAME->Draw()')
print('To scan the root file use for example:\nLV_StatusTree2_2_Top->Scan("","","colsize=30")')


#print("mismatch", mismatch)
#print("mismatch2", mismatch2)
#print("mismatch3", mismatch3)
#print("mismatch4", mismatch4)
#print("mismatch5", mismatch5)
#print("mismatch6", mismatch6)
#print("mismatch7", mismatch7)
#print("mismatch8", mismatch8)
#print("mismatch9", mismatch9)
#print("mismatch10", mismatch10)
#print("mismatch11", mismatch11)





#!/usr/bin/python
import cx_Oracle
import ROOT
import HVQC8Mapping
import HVEffPosQC8Stand
import HVVoltageSum 
import HVEffSingleVfat
from array import array

#Function used to monitor the efficiency of QC8 chambers
#input: the chamber name (for example GE1/1-VII-L-CERN-0002)
def HVEfficiencyMonitor( chamberName, runNumberList ):
	#print ( chamberName, runNumberList )

	#to create a TGraphErrors I have to prepare the list of HV voltage
	#and a list with the efficiency values
		
	for idxVfat in range( 24 ):
		
		effVfatList = array ( 'd' )
		effVfatErrorList = array ( 'd' )
		HVChamberList = array ( 'd' )
		HVChamberErrorList = array ( 'd' ) 
	
		for idxRunNumber in range( len( runNumberList ) ):
			runNumber = runNumberList[ idxRunNumber ]
			pos = HVEffPosQC8Stand.HVEffPosQC8Stand ( chamberName, runNumber )
			print "Position in QC8 stand: " + pos + " Vfat: " + str(idxVfat)
			queryImportStrList = HVQC8Mapping.HVQC8Mapping( chamberName, pos, runNumber )
			print queryImportStrList
	
			#voltage for this chamber
			totVoltChamberList = HVVoltageSum.HVVoltageSum( queryImportStrList, runNumber, chamberName )
			print totVoltChamberList
			
			totVoltChamber = totVoltChamberList[0]
			totVoltChamberError = totVoltChamberList[1]
			
			#efficiency of this Vfat in this chamber
			effVfatReturnList = HVEffSingleVfat.HVEffSingleVfat( chamberName, runNumber, idxVfat )
			print effVfatReturnList		
			
			effVfat = effVfatReturnList[0]
			effVfatError = effVfatReturnList[1]
			
			effVfatList.append( effVfat )
			effVfatErrorList.append( effVfatError )
			HVChamberList.append( totVoltChamber )
			HVChamberErrorList.append( totVoltChamberError )

			#HVEFFtg1 = ROOT.TGraphErrors(n,x,y,ex,ey) x and y are the names of arrays
                        HVEFFtg1 = ROOT.TGraphErrors(len( effVfatList ), HVChamberList, effVfatList, HVChamberErrorList, effVfatErrorList )
                        HVEFFtg1.SetLineColor(2)
                        HVEFFtg1.SetLineWidth(4)
                        HVEFFtg1.SetMarkerColor(4)
                        HVEFFtg1.SetMarkerStyle(21)
                        HVEFFtg1.SetMarkerSize(1)
			#use a name without - and / for the obljects in the root file
			chamberNameRootObj = chamberName.replace( "/", "-" )
			chamberNameRootObj = chamberNameRootObj.replace( "-", "_" )
                        HVEFFtg1.SetName("Efficiency_vs_HV_"+chamberNameRootObj+"_VFAT"+str(idxVfat))
                        HVEFFtg1.SetTitle("Efficiency_vs_HV_"+chamberNameRootObj+"_VFAT"+str(idxVfat))
                        HVEFFtg1.GetXaxis().SetTitle("Total HV on Chamber [V]")
                        HVEFFtg1.GetYaxis().SetTitle("Efficiency "+chamberName+" "+str(idxVfat))
                        #HVEFFtg1.Draw("ACP")
                                                                                                                 
                HVEFFtg1.Write()

		print "\n-----------------------------------------------------------------------------------\n"

#TEST CODE
#chamberNameTest = "GE1/1-VII-L-CERN-0001"
#runNumberTestList = [1, 2, 9, 10]
#chamberNameTest = "GE1/1-VII-L-CERN-0002"
#chamberNameTest = "GE1/1-VII-L-CERN-0002"
#runNumberTest = 12
#print HVEffPosQC8Stand.HVEffPosQC8Stand ( "GE1/1-X-L-CERN-0001",1 )
#pos = HVEffPosQC8Stand.HVEffPosQC8Stand ( chamberNameTest, runNumberTest )
#queryImportStrList = HVQC8Mapping.HVQC8Mapping( chamberNameTest, pos, runNumberTest )

#HVEfficiencyMonitor( chamberNameTest, runNumberTestList )

#print queryImportStr

#totVOLTCHAMBER = HVVoltageSum ( queryImportStrList, runNumberTest, chamberNameTest )
#print "totVOLTCHAMBER", totVOLTCHAMBER

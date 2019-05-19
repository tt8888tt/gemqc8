#This script takes in input n file with the names of QC8 chambers
#and calls the function for the monitoring of efficiency

import HVEfficiencyMonitoring


fileChamber = "ChambersList.txt"

print ("Efficiency monitoring: reading file "+ fileChamber )

f = open(fileChamber, "r")


#extract from each line of ChambersList.txt the name of the chamber and the run numbers asked for each chamber
for lineNameChamber in f:
	print "\n"
	
	lineNameChamber = lineNameChamber[:-1] #remove \n at the end of the line
	
	spaceIdx = lineNameChamber.find('\t')
	chamberName = lineNameChamber[:spaceIdx]
	#print "Chamber: "+chamberName

	stringNumbers = lineNameChamber[(spaceIdx+1):]
	stringNumbers = stringNumbers.replace(","," ")
	runNumberList = stringNumbers.split()
	#transorm this list of strings in a list of numbers
	for x in runNumberList:
		idxElement = runNumberList.index(x)	
		x = int(x)
		runNumberList[idxElement] = x

	#print "Run Numbers for this chamber: "+str(runNumberList)

	#call the function for the Efficiency monitoring
	HVEfficiencyMonitoring.HVEfficiencyMonitor( chamberName, runNumberList )
	
f.close()

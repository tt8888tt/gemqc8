#this script extracts HV for each voltage channel of the chamber, 
#makes a medium of voltage for each channel on the registered time stamps 
#and finally sums the seven channels 
import HVQC8Mapping
import HVEffPosQC8Stand 
import cx_Oracle

def HVVoltageSum ( firstPartQueryString, runNumber ):
	print "first channel called in the HV query: " + firstPartQueryString

	#retrieve the begin and end time of a run_number from the table
	#QC8_GEM_CH_VFAT_EFF_VIEW_RH
	db = cx_Oracle.connect('GEM_904_COND/904CondDB@INT2R')
	cur=db.cursor()

        query = "select RUN_NUMBER, RUN_BEGIN, RUN_END from CMS_GEM_MUON_VIEW.QC8_GEM_CH_VFAT_EFF_VIEW_RH where RUN_NUMBER="+str(runNumber)
        cur.execute(query)
        curRunDates = cur
        for result in curRunDates:
        	run_number 	= result[0]
        	run_begin 	= result[1]
        	run_end 	= result[2]
	
	print ("run_number:", run_number, "run_begin:", run_begin, "run_end:", run_end )
	#these dates are in the format YYYY-MM-DD HH24:mm:ss, good for the query

	run_begin = str( run_begin )
	run_end = str( run_end )
	print run_begin, run_end

	#retrieve HV data for a single HV channel ( HV data are in table ELEMENTS_ALL ) 
	vmon_name = "'" + firstPartQueryString + ".actual.vMon'"
        query = "select ELEMENT_ID from ELEMENTS_ALL where ELEMENT_NAME="+vmon_name
        cur.execute(query)
        vmon_id = cur.fetchone()[0];
        
	print "VMON_ID ", vmon_id
        
        query = "select TS,VALUE_NUMBER from EVENTHISTORY where ELEMENT_ID = "+str(vmon_id) +" and TS > to_date ('"+run_begin+"','YYYY-MM-DD HH24:MI:SS') and TS < to_date ('"+run_end+"','YYYY-MM-DD HH24:MI:SS')"
	cur.execute(query)
	
	voltageSum = 0
	voltageCounter = 0

	curvmon = cur
	for result in curvmon:
		ts = result[0]
		voltage =  result[1]
		print voltage
		voltageSum = voltageSum + voltage
		voltageCounter = voltageCounter + 1

	print voltageSum
	#voltageMedium = voltageSum/voltageCounter
	#print voltageMedium



#TEST CODE
#chamberNameTest = "GE1/1-X-L-CERN-0001"
#chamberNameTest = "GE1/1-VII-L-CERN-0002"
chamberNameTest = "GE1/1-VII-L-CERN-0001"
runNumberTest = 11
#print HVEffPosQC8Stand.HVEffPosQC8Stand ( "GE1/1-X-L-CERN-0001",1 )
pos = HVEffPosQC8Stand.HVEffPosQC8Stand ( chamberNameTest, runNumberTest )
queryImportStr = HVQC8Mapping.HVQC8Mapping(pos, runNumberTest )

#print queryImportStr

HVVoltageSum ( queryImportStr, runNumberTest )

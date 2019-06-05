import cx_Oracle
import os, sys, io

def getConfigurationTable(run_num):
    print "Downloading StandConfigurationTable for run {0}".format(run_num)

    db = cx_Oracle.connect('GEM_904_COND/904CondDB@INT2R')
	cur = db.cursor()

    query = "select * from CMS_GEM_MUON_VIEW.QC8_GEM_STAND_GEOMETRY_VIEW_RH where RUN_NUMBER="+run_num
    cur.execute(query)

    configTablesPath = os.path.abspath("config_creator.py").split('QC8Test')[0] + 'QC8Test/src/Analysis/GEMQC8/data/StandConfigurationTables/'
    outfile_name = configTablesPath + 'gem11' + str(runConfig.StandConfiguration[i]) + '_c' + str(column) + '_r' + str(row) + '.xml'

    with open(outfile_name,"w+") as outfile:
        line = "CH_SERIAL_NUMBER,GEM_NUM,POSITION,CH_TYPE,FLIP,AMC,OH,FLOW_METER,RUN_NUMBER"
        outfile.write(line)
        for result in cur:
            chamber_name = result[0]
            gem_num      = result[1]
            position     = result[2]
            ch_type      = result[3]
            flip         = result[4]
            amc          = result[5]
            oh           = result[6]
            flow_meter   = result[7]
            run_number   = result[8]
            line = chamber_name + "," + gem_num + "," + position + "," + ch_type + "," + flip + "," + amc + "," + oh + "," + flow_meter + "," + run_number
            outfile.write(line)

if __name__ == '__main__':
    runNumber = sys.argv[1]
    tableType = sys.argv[2]
    if tableType == "ConfigurationTable":
        getConfigurationTable(runNumber)
    if tableType == "AligmentTable":
        getAlignmentTable(runNumber)
    if tableType == "DeadStripsTable":
        getDeadStripsTable(runNumber)
    if tableType == "HotStripsTable":
        getHotStripsTable(runNumber)

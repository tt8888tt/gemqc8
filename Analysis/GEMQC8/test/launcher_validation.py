import csv
import os
import sys
import io
import subprocess
import time

if __name__ == '__main__':

    run_number = sys.argv[1]
    xlsx_csv_conversion_flag = sys.argv[2]
    userDB_add = sys.argv[3]

    cmsswBase = os.environ['CMSSW_BASE']
    # Different paths definition
    srcPath = cmsswBase+'/src'
    pyhtonModulesPath = srcPath+'/gemqc8/Analysis/GEMQC8/python/'
    runPath = srcPath+'/gemqc8/Analysis/GEMQC8/test/'
    configTablesPath = srcPath+'/gemqc8/Analysis/GEMQC8/data/StandConfigurationTables/'
    alignmentTablesPath = srcPath+'/gemqc8/Analysis/GEMQC8/data/StandAligmentTables/'
    resDirPath = srcPath

    sys.path.insert(0,pyhtonModulesPath)

    import gemqc8.Analysis.config_creator as config_creator 
    import gemqc8.Analysis.geometry_files_creator as geometry_files_creator
    import gemqc8.Analysis.date_time_runInfoDB as date_time_runInfoDB

    # Conversion from excel to csv files
    if (xlsx_csv_conversion_flag == "xlsxTOcsv=ON"):
        import excel_to_csv
        fileToBeConverted = configTablesPath + "StandGeometryConfiguration_run" + run_number + ".xlsx"
        excel_to_csv.conversion(fileToBeConverted)
        fileToBeConverted = alignmentTablesPath + "StandAlignmentValues_run" + run_number + ".xlsx"
        excel_to_csv.conversion(fileToBeConverted)

    # Generate configuration file
    config_creator.configMaker(run_number)
    time.sleep(1)

    # Generate geometry files
    geometry_files_creator.geomMaker(run_number,"--yesAlignment")
    time.sleep(1)

    # Retrieve start date and time of the run
    #startDateTimeFromDB = date_time_runInfoDB.startDateTime(run_number,userDB_add)
    startDateTimeFromDB = "2019-03-14 09:04:00"
    startDateTimeFromDB = startDateTimeFromDB.rsplit(':', 1)[0]
    startDateTimeFromDB = startDateTimeFromDB.split(' ')[0] + '_' + startDateTimeFromDB.split(' ')[1]
    time.sleep(1)

    # Compiling after the generation of the geometry files
    scramCommand = "scram build -j 4"
    scramming = subprocess.Popen(scramCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=srcPath)
    while scramming.poll() is None:
        line = scramming.stdout.readline()
        print(line)
    print scramming.stdout.read()
    scramming.communicate()
    time.sleep(1)

    # Running the CMSSW code
    runCommand = "cmsRun -n 8 runGEMCosmicStand_validation.py"
    running = subprocess.Popen(runCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=runPath)
    while running.poll() is None:
        line = running.stdout.readline()
        print(line)
    print running.stdout.read()
    running.communicate()
    time.sleep(1)

    """
    #  # Creating folder outside the CMMSW release to put the output files and plots
    outDirName = "Results_QC8_validation_run_"+run_number
    #---# Remove old version if want to recreate
    if (os.path.exists(resDirPath+outDirName)):
        rmDirCommand = "rm -rf "+outDirName
        rmDir = subprocess.Popen(rmDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=resDirPath)
        rmDir.communicate()
    #---# Create the new empty folder
    resDirCommand = "mkdir " + resDirPath+outDirName
    resDir = subprocess.Popen(resDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=resDirPath)
    resDir.communicate()
    time.sleep(1)

    # Create folders for ouput plots per chamber
    import configureRun_cfi as runConfig
    SuperChType = runConfig.StandConfiguration
    effoutDir = srcPath + outDirName
    for i in range (0,30):
        if (SuperChType[int(i/2)] != '0'):
            plotsDirCommand = "mkdir outPlots_Chamber_Pos_" + str(i)
            plotsDirChamber = subprocess.Popen(plotsDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=effoutDir)
            plotsDirChamber.communicate()
    time.sleep(1)

    # Selecting the correct output file, changing the name and moving to the output folder
    out_name = 'out_run_'
    for i in range(6-len(run_number)):
        out_name = out_name + '0'
    out_name = out_name + run_number + '.root'

    mvToDirCommand = "mv validation_" + out_name + " " + resDirPath+outDirName + "/validation_" + out_name
    movingToDir = subprocess.Popen(mvToDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=runPath)
    movingToDir.communicate()
    time.sleep(1)

    mvToDirCommand = "mv " + out_name + " " + resDirPath+outDirName + "/" + out_name
    movingToDir = subprocess.Popen(mvToDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=runPath)
    movingToDir.communicate()
    time.sleep(1)

    # Efficiency computation & output
    effCommand = "root -l -q " + runPath + "macro_validation.c(" + run_number + ",\"" + configTablesPath + "\",\"" + startDateTimeFromDB + "\")"
    efficiency = subprocess.Popen(effCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=effoutDir)
    while efficiency.poll() is None:
        line = efficiency.stdout.readline()
        print(line)
    print efficiency.stdout.read()
    efficiency.communicate()
    time.sleep(1)
    """

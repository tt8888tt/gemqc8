import csv
import os
import sys
import io
import subprocess
import time

def cmsRunner(split):
  runCommand = "cmsRun -n "+str(split)+" runGEMCosmicStand_alignment.py"
  running = subprocess.Popen(runCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=runPath)
  while running.poll() is None:
    line = running.stdout.readline()
    print(line)
  print running.stdout.read()
  running.communicate()
  time.sleep(1)

def align_stopper(run_number, step):
  runPath = os.path.abspath("geometry_files_creator.py").split('QC8Test')[0] + 'QC8Test/src/Analysis/GEMQC8/test/'
  sys.path.insert(0,runPath)
  dx,rz = []
  alignmentTablesPath = os.path.abspath("align_stopper.py").split('QC8Test')[0] + 'QC8Test/src/Analysis/GEMQC8/data/StandAligmentTables/'

  infileName = alignmentTablesPath + "StandAlignmentValues_run" + run_number + "_step" + str(step) + ".csv"
  if (os.path.exists(infileName)):
    with open(infileName) as infile:
      for line in infile:
        if ('\n' in line):
          line = line.split('\n')[0]
        if ('\r' in line):
          line = line.split('\r')[0]
        if (line.split(',')[0]=='RunNumber' and line.split(',')[1]!=run_number):
          sys.exit('StandAlignmentValues file has something wrong: run rumber not matching...')
        if (line.split(',')[0]!='RunNumber' and line.split(',')[0]!='Position'):
          dx.append(float(line.split(',')[1]))
          rz.append(float(line.split(',')[6]))

  if([dx_ < 0.03 for dx_ in dx] and [rz_ < 0.03 for rz_ in rz]):
    return True

if __name__ == '__main__':

  run_number = sys.argv[1]
  xlsx_csv_conversion_flag = sys.argv[2]

  # Different paths definition
  srcPath = os.path.abspath("launcher_alignment.py").split('QC8Test')[0]+'QC8Test/src/'
  pyhtonModulesPath = os.path.abspath("launcher_alignment.py").split('QC8Test')[0]+'QC8Test/src/Analysis/GEMQC8/python/'
  runPath = os.path.abspath("launcher_alignment.py").split('QC8Test')[0] + 'QC8Test/src/Analysis/GEMQC8/test/'
  configTablesPath = os.path.abspath("launcher_alignment.py").split('QC8Test')[0] + 'QC8Test/src/Analysis/GEMQC8/data/StandConfigurationTables/'
  alignmentTablesPath = os.path.abspath("launcher_alignment.py").split('QC8Test')[0] + 'QC8Test/src/Analysis/GEMQC8/data/StandAligmentTables/'
  resDirPath = os.path.abspath("launcher_alignment.py").split('QC8Test')[0]

  sys.path.insert(0,pyhtonModulesPath)

  import config_creator
  import geometry_files_creator

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

  # Compiling after the generation of the geometry files
  scramCommand = "scram build -j 4"
  scramming = subprocess.Popen(scramCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=srcPath)
  while scramming.poll() is None:
    line = scramming.stdout.readline()
    print(line)
  print scramming.stdout.read()
  scramming.communicate()
  time.sleep(1)

  stop_align = False
  step = 0

  import configureRun_cfi as runConfig
  cores = 6

  # Generate geometry files
  geometry_files_creator.geomMaker(run_number, "--noAlignment")
  time.sleep(1)

  while not(stop_align or step>5):
    '''
    # Running the CMSSW code
    poll = Poll(cores)
    poll.map(cmsRunner , range(cores))
    poll.close()
    poll.join()

    # Merging the outfile
    haddCommand = "hadd " runConfig.OutputFileName+ ' ' +runConfig.OutputFileName.split('.root')[0]+'_part*.root'
    hadd = subprocess.Popen(haddCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=runPath)
    hadd.communicate()
    time.sleep(1)
    '''
    cmsRunner(cores)
    #  # Creating folder outside the CMMSW release to put the output files and plots
    outDirName = "Results_QC8_alignment_run_"+run_number
    #---# Remove old version if want to recreate
    if (os.path.exists(resDirPath+outDirName)):
      rmDirCommand = "rm -rf "+outDirName
      rmDir = subprocess.Popen(rmDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=resDirPath)
      rmDir.communicate()
    #---# Create the new empty folder
    resDirCommand = "mkdir "+outDirName
    resDir = subprocess.Popen(resDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=resDirPath)
    resDir.communicate()
    time.sleep(1)

    # Create folders for ouput plots per chamber
    SuperChType = runConfig.StandConfiguration
    alignoutDir = os.path.abspath("launcher_alignment.py").split('QC8Test')[0] + outDirName
    for i in range (0,30):
      if (SuperChType[int(i/2)] != '0'):
        plotsDirCommand = "mkdir outPlots_Chamber_Pos_" + str(i)
        plotsDirChamber = subprocess.Popen(plotsDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=alignoutDir)
        plotsDirChamber.communicate()
    time.sleep(1)

    # Selecting the correct output file, changing the name and moving to the output folder
    out_name = 'out_run_'
    for i in range(6-len(run_number)):
      out_name = out_name + '0'
    out_name = out_name + run_number + '.root'

    mvToDirCommand = "mv alignment_" + out_name + " " + resDirPath+outDirName + "/alignment_" + out_name
    movingToDir = subprocess.Popen(mvToDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=runPath)
    movingToDir.communicate()
    time.sleep(1)

    mvToDirCommand = "mv " + out_name + " " + resDirPath+outDirName + "/" + out_name
    movingToDir = subprocess.Popen(mvToDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=runPath)
    movingToDir.communicate()
    time.sleep(1)

    # Alignment computation & output2
    alignCommand = "root -l -q " + runPath + "macro_alignment.c(" + str(run_number) + ",\"" + runPath + "\",\"" + configTablesPath + "\"," + str(step) + ")"
    alignment = subprocess.Popen(alignCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=alignoutDir)
    while alignment.poll() is None:
      line = alignment.stdout.readline()
      print(line)
    print alignment.stdout.read()
    alignment.communicate()
    time.sleep(1)

    stop_align = align_stopper(run_number, step)
    i += 1

    # Generate geometry files
    geometry_files_creator.geomMaker(run_number, "--yesAlignment")
    time.sleep(1)

  # Running the CMSSW code for the last step of alignment
  runCommand = "cmsRun runGEMCosmicStand_alignment.py"
  running = subprocess.Popen(runCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=runPath)
  while running.poll() is None:
    line = running.stdout.readline()
    print(line)
  print running.stdout.read()
  running.communicate()
  time.sleep(1)

  #  # Creating folder outside the CMMSW release to put the output files and plots
  outDirName = "Results_QC8_alignment_run_"+run_number
  #---# Remove old version if want to recreate
  if (os.path.exists(resDirPath+outDirName)):
    rmDirCommand = "rm -rf "+outDirName
    rmDir = subprocess.Popen(rmDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=resDirPath)
    rmDir.communicate()
  #---# Create the new empty folder
  resDirCommand = "mkdir "+outDirName
  resDir = subprocess.Popen(resDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=resDirPath)
  resDir.communicate()
  time.sleep(1)

  # Create folders for ouput plots per chamber
  import configureRun_cfi as runConfig
  SuperChType = runConfig.StandConfiguration
  tiltitwistoutDir = os.path.abspath("launcher_alignment.py").split('QC8Test')[0] + outDirName
  for i in range (0,30):
    if (SuperChType[int(i/2)] != '0'):
      plotsDirCommand = "mkdir outPlots_Chamber_Pos_" + str(i)
      plotsDirChamber = subprocess.Popen(plotsDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=tiltitwistoutDir)
      plotsDirChamber.communicate()
  time.sleep(1)

  # Selecting the correct output file, changing the name and moving to the output folder
  out_name = 'out_run_'
  for i in range(6-len(run_number)):
    out_name = out_name + '0'
  out_name = out_name + str(run_number) + '.root'

  mvToDirCommand = "mv alignment_" + out_name + " " + resDirPath+outDirName + "/alignment_" + out_name
  movingToDir = subprocess.Popen(mvToDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=runPath)
  movingToDir.communicate()
  time.sleep(1)

  mvToDirCommand = "mv " + out_name + " " + resDirPath+outDirName + "/" + out_name
  movingToDir = subprocess.Popen(mvToDirCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=runPath)
  movingToDir.communicate()
  time.sleep(1)

  # Alignment computation & output
  tilttwistCommand = "root -l -q " + runPath + "macro_tilt_twist.c(" + run_number + ",\"" + runPath + "\",\"" + configTablesPath + "\")"
  tilttwist = subprocess.Popen(tilttwistCommand.split(),stdout=subprocess.PIPE,universal_newlines=True,cwd=tilttwistoutDir)
  while tilttwist.poll() is None:
    line = tilttwist.stdout.readline()
    print(line)
  print tilttwist.stdout.read()
  tilttwist.communicate()
  time.sleep(1)

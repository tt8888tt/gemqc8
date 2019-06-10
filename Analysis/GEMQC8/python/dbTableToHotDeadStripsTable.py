import os, sys, io

from rawIDmapping import map

def SwMappingHotDeadStrips(run_number,mask_reason):

    if (mask_reason == "HotStrips"):
        hotStripsTablesPath = os.path.abspath("dbTableToHotDeadStripsTable.py").split('QC8Test')[0] + 'QC8Test/src/Analysis/GEMQC8/data/HotStripsTables/'
        in_name = hotStripsTablesPath + "HotStrips_run{0}.csv".format(run_number)
    elif (mask_reason == "DeadStrips"):
        deadStripsTablesPath = os.path.abspath("dbTableToHotDeadStripsTable.py").split('QC8Test')[0] + 'QC8Test/src/Analysis/GEMQC8/data/DeadStripsTables/'
        in_name = deadtripsTablesPath + "DeadStrips_run{0}.csv".format(run_number)
    else: print("This mask type does not exist!")

    if (os.path.exists(in_name)):
        outfile_name = "Mask_" + in_name[:-4] + '.dat'
        with open(outfile_name,"w+") as outfile:
            with open(in_name) as infile:
                for line in infile:
                    if ('\n' in line):
                        line = line.split('\n')[0]
                    if ('\r' in line):
                        line = line.split('\r')[0]

                    if (line.split(',')[0]!='CH_SERIAL_NUMBER'):

                        position = line.split(',')[2]
                        row = int(position.split('/')[0])
                        column = int(position.split('/')[1])
                        SCnumber = (5 * (column - 1)) + (row - 1)

                        vfat = int(line.split(',')[3])
                        eta = 8 - (vfat%8)

                        strip = int(line.split(',')[5])

                        det_pos = str(SCnumber) + "/" + str(eta)

                        rawId = map.get(det_pos)

                        outfile.write(rawId + " " + strip + "\n")

		print("\n")
		print("Success: " + in_name + " read to generate " + out_name)
		print("\n")

    else:
		print("\n")
		print("The input file does not exist!")
		print("\n")

if __name__ == '__main__':
    run_num = sys.argv[1]
    mask_type = sys.argv[2]
    SwMappingHotDeadStrips(run_num,mask_type)

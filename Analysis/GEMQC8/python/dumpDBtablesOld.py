import cx_Oracle
import datetime
import sys

def printRow(r,fout):
   for i in r:
      fout.write(" ")
      #print type(i)
      if type(i) is str:
         fout.write(i)
      elif type(i) is int:
         fout.write("{0}".format(i))
      elif type(i) is float:
         fout.write("{0:0.5f}".format(i))
      else:
         print type(i)
         fout.write("{0}".format(type(i)))
   fout.write("\n")
# end of printRow


def dumpTable(db,tableName,fout,runnumber):
   query = "select * from {0}".format(tableName)
   #print "{0}".format(type(runnumber))
   if (runnumber!='-1'):
      query+=" where run_number={0}".format(runnumber)

   print query
   cur=db.cursor()
   cur.execute(query)
   count=0
   for r in cur:
      print r
      printRow(r,fout)
      count+=1

   fout.write(" got {0} rows".format(count))
   print " got {0} rows".format(count)

   # print column names
   names = [description[0] for description in cur.description]
   print names
   printRow(names,fout)
# end of dumpTable


#
# Main code
#

if len(sys.argv)==1:
   print "\nplease provide the runNumber"
   print "  python dumpViewsQC8.py runNumber"
   print "If runNumber=-1, the script selects all entries\n"
   exit()

runnumber=sys.argv[1]
print "runnumber={0}".format(runnumber)

f = open("test-qc8-dump-{0}.out".format(runnumber),'w')

db = cx_Oracle.connect('CMS_GEM_APPUSER_R/GEM_Reader_2015@INT2R')

dumpTable(db,"CMS_GEM_MUON_VIEW.QC8_GEM_STAND_GEOMETRY_VIEW_RH",f,runnumber)
f.write("\n\n");
dumpTable(db,"CMS_GEM_MUON_VIEW.QC8_GEM_ALIGNMENT_VIEW_RH",f,runnumber)
f.write("\n\n");
dumpTable(db,"CMS_GEM_MUON_VIEW.QC8_GEM_CH_VFAT_EFF_VIEW_RH",f,runnumber)
f.write("\n");
f.write("{0}".format(datetime.datetime.now()))
f.close();

exit()

query = "select * from CMS_GEM_MUON_VIEW.QC8_GEM_STAND_GEOMETRY_VIEW_RH"
print query

cur=db.cursor()
cur.execute(query)
for r in cur:
   print r
   printRow(r,f)

# print column names
names = [description[0] for description in cur.description]
print names
printRow(names,f)
#for n in names:
#   f.write(" {0}".format(n))

f.close()

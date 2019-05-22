#!/usr/bin/env python
from datetime import datetime,date,time
#from time import sleep
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
#import serial
import time
import xlrd
from xlrd import xldate
import re
import datetime
import sys
#import statistics
from xmlConversion import generateXMLHeader, generateDataSet, writeToFile,writeToFile1
from xmlConversion import generateXMLDatafastamb,generateXMLDatafast,generateXMLDatalongamb,generateXMLDatalong, generateXMLData3,generateXMLData3a,generateXMLData4,generateXMLData4a,generateXMLData5a,generateXMLData5,generateXMLData4s, generateXMLDataChVfatEfficiency


#QC3
def xml_from_excel3(excel_file):
	wb = xlrd.open_workbook(excel_file)
	sh = wb.sheet_by_index(0)
	user = ''#sys.argv[3]
        #chamber=sh.cell(10,1).value
#       chamber=sys.argv[2]
#       Run=sys.argv[3]
	location=''#sys.argv[2]
	Startdate=sh.cell(2,1).value#sys.argv[5]
	Stopdate=sh.cell(3,1).value#sys.argv[6]
	Start = datetime.datetime(*xlrd.xldate_as_tuple(Startdate, wb.datemode))
	Stop = datetime.datetime(*xlrd.xldate_as_tuple(Stopdate, wb.datemode))
	#Date=str(Start[0:10])
	comment=''#sys.argv[4]
	chamber = sh.cell(1,1).value#sys.argv[7]
        #Elog=sys.argv[7]
        #File=sys.argv[8]
        #Comment=sys.argv[9]
	Run = sh.cell(0,1).value
	root = generateXMLHeader("QC8_GEM_CH_VFAT_EFFICIENCY","GEM CH VFAT EFFICIENCY QC8","GEM CH VFAT EFFICIENCY",str(Run),str(Start),str(Stop),str(comment),str(location),str(user))
	dataSet = generateDataSet(root,comment,"1","GEM Chamber",str(chamber))	
	for row in range(5,sh.nrows):
		vfat_posn= sh.row_values(row)[0]
		efficiency= sh.row_values(row)[1]
		efficiency_error =sh.row_values(row)[2]
		cluster_size_avg =sh.row_values(row)[3]
		cluster_size_sigma =sh.row_values(row)[4]
		percent_masked =sh.row_values(row)[5]
		generateXMLDataChVfatEfficiency(dataSet,str(vfat_posn),str(efficiency), str(efficiency_error),str(cluster_size_avg),str(cluster_size_sigma), str(percent_masked))
		writeToFile(fileName, tostring(root))
if __name__ =="__main__":	
	#fname=raw_input("Enter excel data file name:")
	fname = sys.argv[1]
	fileName=fname+".xml"
	#datafile=fname+"_Data.xml"
	#testfile=fname+"_summry.xml"
	xml_from_excel3(fname)	

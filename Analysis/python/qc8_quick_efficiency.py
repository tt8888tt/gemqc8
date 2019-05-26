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
from xmlConversion import generateXMLDatafastamb,generateXMLDatafast,generateXMLDatalongamb,generateXMLDatalong, generateXMLData3,generateXMLData3a,generateXMLData4,generateXMLData4a,generateXMLData5a,generateXMLData5,generateXMLData4s, generateXMLDataChVfatEfficiency, generateXMLDataQuickEfficiencyQC8


#QC3
def xml_from_excel3(excel_file):
	wb = xlrd.open_workbook(excel_file)
	sh = wb.sheet_by_index(0)
	user = sys.argv[3]
        #chamber=sh.cell(10,1).value
#       chamber=sys.argv[2]
#       Run=sys.argv[3]
	location=sys.argv[2]
	Start=sys.argv[5]
	Stop=sys.argv[6]
	#Date=str(Start[0:10])
	comment=sys.argv[4]
	chamber = sh.cell(1,1).value#sys.argv[7]
	overall_efficiency = sh.cell(2,1).value
        error_efficiency = sh.cell(3,1).value
	Run = sh.cell(0,1).value
	root = generateXMLHeader("QC8_GEM_QUICK_EFFICIENCY","GEM QUICK EFFICIENCY QC8","GEM QUICK EFFICIENCY",str(Run),str(Start),str(Stop),str(comment),str(location),str(user))
	dataSet = generateDataSet(root,comment,"1","GEM Chamber",str(chamber))	
	generateXMLDataQuickEfficiencyQC8(dataSet,str(overall_efficiency),str(error_efficiency))
	writeToFile(fileName, tostring(root))
if __name__ =="__main__":	
	#fname=raw_input("Enter excel data file name:")
	fname = sys.argv[1]
	fileName=fname+".xml"
	#datafile=fname+"_Data.xml"
	#testfile=fname+"_summry.xml"
	xml_from_excel3(fname)	

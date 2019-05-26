import os, sys, io
from sqlalchemy import create_engine

def startDateTime(run_number, USER_add):

	DB_NAME = 'gem904_ri'
	DB_HOST = 'gem904nas01'
	DB_PORT = 3306
	DB_USER = 'GEM_904' + USER_add

	engine = create_engine('mysql://{}:{}@{}:{}/{}'.format(DB_USER,DB_USER,DB_HOST,DB_PORT,DB_NAME), echo=False)
	cnx = engine.connect()
	query = 'SELECT bookingtime FROM runnumbertbl WHERE runnumber LIKE {}'.format(run_number)
	res = cnx.execute(query)

	for num in res:
		print "Run {:03d} started on {}".format(run_number,str(num[0]))
		return(str(num[0]))

if __name__ == '__main__':
	run_num = sys.argv[1]
	username_add = sys.argv[2]
	startDateTime(run_num, username_add)

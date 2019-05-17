from sqlalchemy import create_engine

def configMaker(run_number, DB_USER):

	DB_NAME = 'gem904_ri'
	DB_HOST = 'gem904nas01'
	DB_PORT = 3306

	engine = create_engine('mysql://{}:{}@{}:{}/{}'.format(DB_USER,DB_USER,DB_HOST,DB_PORT,DB_NAME), echo=False)
	cnx    = engine.connect()
	query = 'SELECT bookingtime FROM runnumbertbl WHERE runnumber LIKE {}'.format(run_number)
	res = cnx.execute(query)
	
	for num in res:
		return(str(num[0]))

if __name__ == '__main__':
	run_num = sys.argv[1]
	username = sys.argv[2]
	configMaker(run_num, username)

import logging as log

def configureProjectLogging() :
	log.basicConfig(
		datefmt="%Y-%m-%d %H:%M:%S", 
		filename='Groovester.log', 
		format='%(levelname)s;%(asctime)s;%(message)s', 
		level=log.DEBUG
	)

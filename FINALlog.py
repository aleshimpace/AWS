import logging

#LOG_FILE_ONE = "/home/pi/zAWS/ADCdata.csv"
LOG_FILE_TWO = "/home/pi/zAWS/UPLOADcount.log"
LOG_FILE_THREE = "/home/pi/zAWS/Parameters.csv"

LOG_FILE_FOUR = "/home/pi/zAWS/UPLOADcount_rain.log"
LOG_FILE_FIVE = "/home/pi/zAWS/tipping_bucket.log"

def createLOGs():

    #setup_logger('log_one', LOG_FILE_ONE)
    setup_logger('log_two', LOG_FILE_TWO)
    setup_logger('log_three', LOG_FILE_THREE)
    setup_logger('log_four', LOG_FILE_FOUR)
    setup_logger('log_five', LOG_FILE_FIVE)

def writePara(actualval):
    logger(actualval, 'info', 'Parameters')

def tipBucket():
    logger(1, 'info', 'tipping_bucket')

def writeUpcount():
    logger('upload', 'info', 'UPLOADcount')

def writeUpcount_Rain():
    logger('upload', 'info', 'UPLOADcount_rain')


    

def setup_logger(logger_name, log_file, level=logging.INFO):

    log_setup = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fileHandler = logging.FileHandler(log_file, mode='a')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    log_setup.setLevel(level)
    log_setup.addHandler(fileHandler)
    log_setup.addHandler(streamHandler)

def logger(msg, level, logfile):
 
    if logfile == 'ADCdata'   : log = logging.getLogger('log_one')
    if logfile == 'UPLOADcount'   : log = logging.getLogger('log_two')
    if logfile == 'Parameters'   : log = logging.getLogger('log_three')
    if logfile == 'UPLOADcount_rain'   : log = logging.getLogger('log_four')
    if logfile == 'tipping_bucket'   : log = logging.getLogger('log_five')
    if level == 'info'    : log.info(msg) 
    if level == 'warning' : log.warning(msg)
    if level == 'error'   : log.error(msg)

if __name__ == "__main__":

    createLOGs()


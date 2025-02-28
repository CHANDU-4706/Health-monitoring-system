import time
import os
f = open("state.txt", "r")
state = int(f.read(1)) #0 or 1
f.close()
while True:
    # sleep for 5 minutes
    f = open("state.txt", "w")
    print(state)
    f.write("2")
    print("state changed to 2")
    f.close()
    #run a map reduce job
    os.system("$HADOOP_HOME/bin/hadoop jar MapReduce.jar HealthMapReduce")
    os.system(f"rm -r SparkOutput{state+1}/")
    os.system(f"rm -r MapReduceOutput")
    os.system("mkdir MapReduceOutput")
    os.system("hdfs dfs -copyToLocal /Output/* MapReduceOutput")
    print(f"removed SparkOutput{state+1}")
    state = (state+1)%2  #switch to the other realtime view with the recent data

    f = open("state.txt", "w")
    f.write(str(state))
    f.close()

    f = open("realTimeView.txt", "w")
    f.write(str(state+1))
    f.close()

    time.sleep(60*60)

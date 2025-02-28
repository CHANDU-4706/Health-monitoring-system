import os
import time
files = os.listdir("Input_data/")
files = [x for x in files if x.endswith('.csv')]

for file in files:
    os.system(f"cp Input_data/{file} Spark_data/")
    os.system(f"hdfs dfs -copyFromLocal Input_data/{file} /Input/")
    print(f"file: {file} copied")
    time.sleep(30)
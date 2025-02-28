# Health Monitoring System

## Problem statement

Modern systems now follow a very well-known architectural pattern known as
microservices. Microservices refer to a group of small servers communicating to
achieve a given task or group of tasks. Each service tends to work independently
and communicate with another service whenever some calculation or information
is needed and cannot be found locally. Since these services work independent from
each other, the system is susceptible to partial failures when some services fail.
Moreover, as services are free to be deployed on different machines and platforms
and may not share the same computing resources, these resources need to be
monitored. For example, storage disks may reach their capacities, CPUs may be
highly utilized, memory may be highly utilized. Therefore, a health monitoring
system is needed to monitor the health of the system services and the resources
they may use. <br>

The goal is to use the lambda architecture for our health
monitor system. See the figure below:<br>
![https://github.com/AmrMomtaz/Health-Monitoring-System/blob/main/images/lambda.png](https://github.com/AmrMomtaz/Health-Monitoring-System/blob/main/images/lambda.png)<br>

* The data is persisted in the batch layer using HDFS commands initiated from the scheduler.
* Then the data is processed regularly using map-reduce to generate batch views creating the serving layer.
* For the speed layer, Spark jobs are initiated for new data generating realtime views.
* The output of mapreduce and spark jobs are <b>PARQUET</b> files.
* We've used <b>DuckDB</b> for both NOSQL databes for the serving layer and speed layer.
* The scheduler handles initiating the mapreduce jobs periodically and expiring the realtime views.

<b>Please note that you should have hadoop installed (single node or multi-node setup) and you should have $HADOOP_HOME and $HADOOP_CLASSPATH paths are set correctly. (you can follow this <a href = "https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/SingleCluster.html">link</a> for hadoop setup guide)</b>

## Micro-services 

The mock microservices system is built in which
services send health messages to a certain client server. The client server should
receive these messages, catalog, and persist them on HDFS.
![https://github.com/AmrMomtaz/Health-Monitoring-System/blob/main/images/microservices.png](https://github.com/AmrMomtaz/Health-Monitoring-System/blob/main/images/microservices.png)<br>
* The health messages will be in JSON format. Each message contains the service
name, timestamp, CPU utilization percentage, RAM total and free space in GBs,
and Disk total and free space in GBs.<br>
* The services will send messages to the Health Monitor system using the UDP
protocol. Use port 3500 on the Health Monitor side. The message will simply
contain the health message json string.<br>

<b>Please Note:</b> In the next sections we've developed tha mapreduce jobs and spark jobs to work on CSV files.
So you will find a script which converts the JSON file to CSV in mock_microservices directory. Finally the data should have
the following form:<br>
![[data](https://github.com/AmrMomtaz/Health-Monitoring-System/blob/main/images/data.png)](https://github.com/AmrMomtaz/Health-Monitoring-System/blob/main/images/data.png)

## MapReduce

The map reduce jobs will calculate the required statistics:
* The mean CPU utilization for each service.
* The mean Disk utilization for each service.
* The mean RAM utilization for each service.
* The peak of utilization for each resource for each service.
* The count of health messages received for each service.<br>

The map step of any map-reduce job processes each record
individually producing a record or more as a result. The reduce step collects all
records having a common attribute and produces one record summarizing,
reducing, these records.<br>
You can find the MapReduce.jar in the mapreduce directory. Run the mapreduce job using the following command.<br>
```
$HADOOP_HOME/bin/hadoop jar MapReduce.jar HealthMapReduce
```
<b>PLEASE NOTE:</b> You should create a /Input directory in HDFS and put the data in it.
The data should be in .csv files as shown before. You will use the following commands
to create new directory and to move the data to HDFS
```
$HADOOP_HOME/bin/hdfs dfs -mkdir <folder name>
$HADOOP_HOME/bin/hdfs dfs -copyFromLocal <local file path>  <dest(present on hdfs)>
```
If you want to change the source code and create a new mapredeuce.jar file use the following commands:
```
To compile the code:
$HADOOP_HOME/bin/hadoop com.sun.tools.javac.Main HealthMapReduce.java
To create JAR file:
jar cf MapReduce.jar HealthMapReduce*.class
```
Here is an example of a mapreduce job running:
![https://github.com/AmrMomtaz/Health-Monitoring-System/blob/main/images/mapreduce.png](https://github.com/AmrMomtaz/Health-Monitoring-System/blob/main/images/mapreduce.png)<br>

<b>IMPORTANT NOTES:</b>
* The percision of queries is in minutes.
* The mapreduce creates <b>5 PARQUET files</b> which are [year.parquet , mounth.parquet , day.parquet , hour.parquet , minute.parquet] 
to make the queries faster and reduce query latency.
* The mapreduce writes the parquet files in /Output directory in HDFS and everytime mapreduce job is initiated it overwrites them.
 Here is the mapreduce output:
![https://github.com/AmrMomtaz/Health-Monitoring-System/blob/main/images/mapreduce_output.png](https://github.com/AmrMomtaz/Health-Monitoring-System/blob/main/images/mapreduce_output.png)
* We use DuckDB to query the parquet files. (you will find the query code in the mapreduce directory)

## Spark
* The spark job represents the real time view of the system.
It listens to "Spark_data" folder for new inputs to start processing it immediatly.
* When a query is made, it utilized both the realtime view and the batch view where the realtime view represents only the last hour and the batch view represents all the data since the beginning
* While the mapreduce job is running, 2 spark jobs are being fired, the old one which has the data since the last mapreduce job and a new one that starts with the new mapreduce job.
The query still uses the old spark job.
* When the mapreduce job ends, the old spark job is deleted and the new spark job continues till the next mapreduce fire.

### Spark files:
* "SparkSession.py" the spark job execution code
* "state.txt" it tells the schedular what is the state of the realtime view
#### There are 3 possible states:
 * 0: the first spark job is running
 * 1: the second spark job is running
 * 2: both spark jobs are running "when the mapreduce job is in-progress".
 
### Output folders:
* "MapReduceOutput" where the parquet files are downloaded locally from hadoop
* "Spark_data" a folder where the spark jon listens to
* "SparkOutput1"/"SparkOutput2" where the parquet files are added locally from spark jobs depending on which job is running.
they are all added to spark folder.
#### Make sure these folder exists under /spark/ directory.

## Simulations:
* "Spark/QueryAllData.py" is a script that fetches the needed data both the realtime and the batch views.
* "Spark/Simulator.py"/"Spark/schedular.py" is used to simulate the working flow of the realtime view and the batch view:
To start the simulation:
* Start the hadoop server as mentioned above.
* Start the spark job using the SparkSession.py script.
* Run both the simulator.py and schedular.py scripts.
* The simulator periodically adds the services files to "spark_data" folder where spark listens.
* The schedular waits for a given time and then starts the mapreduce job and adjusts the spark jobs to work accordingly.

### Notes:
* Make sure all paths are adjusted according to your working space
* Make sure the mapreduce.jar exists in the same directory as the schedular.
* Add Spark_data folder and adjust the path to it in the SparkSession.py script if needed.

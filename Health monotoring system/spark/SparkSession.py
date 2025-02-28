from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType, TimestampType

CSV_PATH = '/home/hdoop/Desktop/spark/Spark_data'
SPARK_PATH = "/home/hdoop/Desktop/spark/"
spark = SparkSession.builder.appName("sparkSession").getOrCreate()

schema = schema = StructType([
    StructField("service", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("CPU", DoubleType(), True),
    StructField("total_ram", DoubleType(), True),
    StructField("free_ram", DoubleType(), True),
    StructField("total_disk", DoubleType(), True),
    StructField("free_disk", DoubleType(), True)])

def operateFile(sparkRead, epich_id):
    f = open("state.txt", "r")
    state = int(f.read(1))
    print(state)
    f.close()

    sparkRead = sparkRead.withColumn('timestamp', from_unixtime('timestamp', 'yyyy-MM-dd HH:mm').cast(
        TimestampType())).withWatermark("timestamp", "1 minutes")
    sparkRead.printSchema()

    dfResult = sparkRead.withColumn('disk_utilization', (col("total_disk") - col("free_disk")) / col("total_disk"))
    dfResult = dfResult.withColumn('ram_utilization', (col("total_ram") - col("free_ram")) / col("total_ram"))
    dfResult = dfResult.groupBy("service", "timestamp").agg(avg("CPU"), max("CPU"), avg('disk_utilization'),
                                                            max('disk_utilization'), avg('ram_utilization'),
                                                            max('ram_utilization'), count("*"))
    dfResult = dfResult.withColumnRenamed('avg(CPU)', 'avg_cpu').withColumnRenamed('max(CPU)', 'max_cpu') \
        .withColumnRenamed('avg(disk_utilization)', 'avg_disk').withColumnRenamed('max(disk_utilization)', 'max_disk') \
        .withColumnRenamed('avg(ram_utilization)', 'avg_ram').withColumnRenamed('max(ram_utilization)', 'max_ram') \
        .withColumnRenamed('count(1)', 'count')

    print("processing file number:", epich_id)
    dfResult.show()
    if state == 0:
        dfResult.repartition(1).write.mode('append').parquet(SPARK_PATH+"SparkOutput1")
        return
    elif state == 1:
        dfResult.repartition(1).write.mode('append').parquet(SPARK_PATH+"SparkOutput2")
        return
    elif state == 2:
        dfResult.repartition(1).write.mode('append').parquet(SPARK_PATH+"SparkOutput1")
        dfResult.repartition(1).write.mode('append').parquet(SPARK_PATH+"SparkOutput2")
    return

sparkRead = spark.readStream.schema(schema).format("csv").option('header', True).csv(CSV_PATH, inferSchema=True)
sparkRead.writeStream.foreachBatch(operateFile).start().awaitTermination()


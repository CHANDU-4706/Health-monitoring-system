import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.*;
import org.apache.hadoop.mapreduce.lib.input.*;
import org.apache.hadoop.mapreduce.lib.output.*;
import org.apache.parquet.avro.AvroParquetWriter;
import org.apache.parquet.hadoop.ParquetWriter;
import org.apache.parquet.hadoop.metadata.CompressionCodecName;

import java.io.*;
import java.net.URI;
import java.sql.Timestamp;


public class HealthMapReduce {

    public static class TokenizerMapper
            extends Mapper<Object, Text, Text, Text> {

        // Key and Value returned by the mapper class
        private static final Text KEY = new Text();
        private static final Text VALUE = new Text();

        public void map(Object key, Text value, Context context
        ) throws IOException, InterruptedException {
            // Record format -> service,timestamp,CPU,total_ram,free_ram,total_disk,free_disk
            if (value.getLength()==61)
                return;

            // Getting timestamp to string
            String[] record = value.toString().split(",");
            Timestamp ts = new Timestamp(Long.parseLong(record[1])*1000);
            String ts_string = ts.toLocalDateTime().toString().replaceAll("[-T:]","");
            // Creating the five new tuples for each record
            VALUE.set(record[1]+"000" +","+ record[2] +","+ record[3] +","+ record[4] +","+ record[5] +","+ record[6]);
            KEY.set(record[0] + ts_string.substring(0,4));
            context.write(KEY,VALUE); // year
            KEY.set(record[0] + ts_string.substring(0,6));
            context.write(KEY,VALUE); // month
            KEY.set(record[0] + ts_string.substring(0,8));
            context.write(KEY,VALUE); // day
            KEY.set(record[0] + ts_string.substring(0,10));
            context.write(KEY,VALUE); // hours
            KEY.set(record[0] + ts_string.substring(0,12));
            context.write(KEY,VALUE); // minutes
        }
    }

    public static class HealthMessageReducer
            extends Reducer<Text,Text,Text,Text> {

        private static ParquetWriter<GenericData.Record> writer_year,writer_month,writer_day,writer_hour,writer_minute;
        private	static final Schema AVRO_SCHEMA = new	Schema.Parser().parse(
                "{\"type\":\"record\",\"name\":\"healthRecord\",\"doc\":\"health records\",\"fields\":[{\"name\":\"service\","+
                    "\"type\":\"string\"},{\"name\":\"timestamp\",\"type\":\"string\"},{\"name\":\"avg_cpu\",\"type\":\"double\"},"+
                    "{\"name\":\"max_cpu\",\"type\":\"double\"},{\"name\":\"max_time_cpu\",\"type\":\"string\"},{\"name\":\"avg_ram\","+
                    "\"type\":\"double\"},{\"name\":\"max_ram\",\"type\":\"double\"},{\"name\":\"max_time_ram\",\"type\":\"string\"" +
                    "},{\"name\":\"avg_disk\",\"type\":\"double\"},{\"name\":\"max_disk\",\"type\":\"double\"},{\"name\":\"max_time_disk\","+
                    "\"type\":\"string\"},{\"name\":\"count\",\"type\":\"long\"}]}");

        @Override
        @Deprecated
        public void setup(Context context) throws IOException {
            // Initializing parquet writers
            Path path =	new	Path("/Output/year.parquet");
            writer_year = initializeWriter(path);
            path = 	new	Path("/Output/month.parquet");
            writer_month = initializeWriter(path);
            path = 	new	Path("/Output/day.parquet");
            writer_day = initializeWriter(path);
            path = 	new	Path("/Output/hour.parquet");
            writer_hour = initializeWriter(path);
            path = 	new	Path("/Output/minute.parquet");
            writer_minute = initializeWriter(path);
        }

        @Override
        public void cleanup(Context context) throws IOException {
            // Closing all parquet writers
            writer_year.close();
            writer_month.close();
            writer_day.close();
            writer_hour.close();
            writer_minute.close();
        }


        // Function which initialize a writer
        @Deprecated
        private static ParquetWriter<GenericData.Record> initializeWriter(Path path) throws IOException {
            return AvroParquetWriter.
                    <GenericData.Record>builder(path)
                    .withRowGroupSize(ParquetWriter.DEFAULT_BLOCK_SIZE)
                    .withPageSize(ParquetWriter.DEFAULT_PAGE_SIZE)
                    .withSchema(AVRO_SCHEMA)
                    .withConf(new Configuration())
                    .withCompressionCodec(CompressionCodecName.SNAPPY)
                    .withValidation(false)
                    .withDictionaryEncoding(false)
                    .build();
        }

        // Function which creates the casandra record
        private static GenericData.Record createRecord(double meanCPU, double meanRAM , double meanDisk,
                                                       double maxCPU, double maxRAM, double maxDisk,
                                                       String maxPeakCPU, String maxPeakRAM ,String maxPeakDisk,
                                                       String service, String ts, long count){
            GenericData.Record record = new GenericData.Record(AVRO_SCHEMA);
            record.put("service", service);
            record.put("timestamp", ts);
            record.put("avg_cpu",meanCPU);
            record.put("max_cpu",maxCPU);
            record.put("max_time_cpu",maxPeakCPU);
            record.put("avg_ram",meanRAM);
            record.put("max_ram",maxRAM);
            record.put("max_time_ram",maxPeakRAM);
            record.put("avg_disk",meanDisk);
            record.put("max_disk",maxDisk);
            record.put("max_time_disk",maxPeakDisk);
            record.put("count",count);
            return record;
        }

        // Function which prints ts in desired format ("YYYY-MM-DD HH:MM")
        private static String adjustTimestampFormat(String ts){
            if (ts.length()==4)
                return ts;
            else if (ts.length()==6)
                return ts.substring(0,4) + "-" + ts.substring(4,6);
            else if (ts.length()==8)
                return ts.substring(0,4) + "-" + ts.substring(4,6) + "-" + ts.substring(6,8);
            else if (ts.length()==10)
                return ts.substring(0,4) + "-" + ts.substring(4,6) + "-" + ts.substring(6,8) +
                        " " + ts.substring(8,10);
            else return ts.substring(0,4) + "-" + ts.substring(4,6) + "-" + ts.substring(6,8) +
                        " " + ts.substring(8,10) + ":" + ts.substring(10);
        }

        @Override
        public void reduce(Text key, Iterable<Text> values,
                           Context context) throws IOException {
            // Initializing return values
            String service = key.toString().substring(0,9);
            String ts = key.toString().substring(9);
            double meanCPU = 0,meanRAM = 0 ,meanDisk = 0;
            double maxCPU = 0,maxRAM = 0, maxDisk = 0 ;
            String maxPeakCPU = "",maxPeakRAM = "", maxPeakDisk = "";
            long count = 0;
            // Inner loop variables for computations
            String current_timestamp;
            double current_cpu,current_ram,current_disk;
            for (Text value : values){
                String[] record = value.toString().split(",");
                current_timestamp = record[0];
                current_cpu = Double.parseDouble(record[1]);
                current_ram = (Double.parseDouble(record[2])-Double.parseDouble(record[3])) / Double.parseDouble(record[2]);
                current_disk = (Double.parseDouble(record[4])-Double.parseDouble(record[5])) / Double.parseDouble(record[4]);
                meanCPU += current_cpu; meanRAM += current_ram; meanDisk += current_disk;
                if(current_cpu > maxCPU){
                    maxCPU = current_cpu;
                    maxPeakCPU=current_timestamp;
                }
                if(current_ram > maxRAM){
                    maxRAM = current_ram;
                    maxPeakRAM=current_timestamp;
                }
                if(current_disk > maxDisk){
                    maxDisk = current_disk;
                    maxPeakDisk=current_timestamp;
                }
                count++;
            }
            meanCPU/=count; meanRAM/=count; meanDisk/=count;
            // Converting timestamps to dates
            Timestamp timestamp_to_date = new Timestamp(Long.parseLong(maxPeakCPU));
            String peakCPU = timestamp_to_date.toLocalDateTime().toString();
            timestamp_to_date.setTime(Long.parseLong(maxPeakRAM));
            String peakRAM = timestamp_to_date.toLocalDateTime().toString();
            timestamp_to_date.setTime(Long.parseLong(maxPeakDisk));
            String peakDisk = timestamp_to_date.toLocalDateTime().toString();
            String tsInFormat = adjustTimestampFormat(ts);
            // Writing record
            GenericData.Record record = createRecord(meanCPU,meanRAM,meanDisk,maxCPU,maxRAM,maxDisk,
                    peakCPU,peakRAM,peakDisk,service,tsInFormat,count);
            if (ts.length()==12)
                writer_minute.write(record);
            else if (ts.length()==10)
                writer_hour.write(record);
            else if (ts.length()==8)
                writer_day.write(record);
            else if (ts.length()==6)
                writer_month.write(record);
            else
                writer_year.write(record);
        }
    }

    // Driver code for setting the job and deleting old data for re-computation algorithm
    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        // Deleting old batch views
        Path output = new Path("/Output");
        FileSystem hdfs = FileSystem.get(URI.create("hdfs://localhost:9000"),conf);
        if (hdfs.exists(output)) {
            hdfs.delete(output, true);
        }
        // Setting job
        Job job = Job.getInstance(conf, "job1");
        job.setJarByClass(HealthMapReduce.class);
        job.setMapperClass(HealthMapReduce.TokenizerMapper.class);
        job.setReducerClass(HealthMapReduce.HealthMessageReducer.class);
        job.setMapOutputKeyClass(Text.class);
        job.setMapOutputValueClass(Text.class);
        job.setInputFormatClass(TextInputFormat.class);
        TextInputFormat.addInputPath(job, new Path("/Input"));
        job.setOutputFormatClass(NullOutputFormat.class);
        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }
}

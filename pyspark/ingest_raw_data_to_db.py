from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pyspark.sql.functions as fn
from real_time_streaming_data_pipeline import save_to_postgresql_table

# Kafka Broker
KAFKA_TOPIC_NAME_CONS = "server-live-status"
KAFKA_BOOTSTRAP_SERVERS_CONS = '172.16.30.89:9092'

# PostgresSQL Database Server Details
postgresql_host_name = "172.16.30.89"
postgresql_port_no = "5432"
postgresql_user_name = "demouser"
postgresql_password = "demouser"
postgresql_database_name = "event_message_db"
postgresql_driver = "org.postgresql.Driver"


# Create the Database properties
db_properties = {}
db_properties['user'] = postgresql_user_name
db_properties['password'] = postgresql_password
db_properties['driver'] = postgresql_driver


if __name__ == "__main__":
    print("Ingestion raw data into postgres....")

    spark = SparkSession \
        .builder \
        .appName("Real-time Streaming Data Pipeline") \
        .getOrCreate()

    event_message_detail_df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS_CONS) \
        .option("subscribe", KAFKA_TOPIC_NAME_CONS) \
        .option("startingOffsets", "latest") \
        .load()

    # Schema Code Block Starts Here
    event_message_detail_schema = StructType([
      StructField("event_id", StringType()),
      StructField("event_server_status_color_name_severity_level", StringType()),
      StructField("event_datetime", StringType()),
      StructField("event_server_type", StringType()),
      StructField("event_country_code", StringType()),
      StructField("event_country_name", StringType()),
      StructField("event_city_name", StringType()),
      StructField("event_estimated_issue_resolution_time", IntegerType()),
      StructField("event_server_status_other_param_1", StringType()),
      StructField("event_server_status_other_param_2", StringType()),
      StructField("event_server_status_other_param_3", StringType()),
      StructField("event_server_status_other_param_4", StringType()),
      StructField("event_server_status_other_param_5", StringType()),
      StructField("event_server_config_other_param_1", StringType()),
      StructField("event_server_config_other_param_2", StringType()),
      StructField("event_server_config_other_param_3", StringType()),
      StructField("event_server_config_other_param_4", StringType()),
      StructField("event_server_config_other_param_5", StringType())
    ])

    # Data Processing/Data Transformation
    event_message_detail_df_1 = event_message_detail_df.selectExpr("CAST(value AS STRING)")

    event_message_detail_df_2 = event_message_detail_df_1.select(from_json(col("value"), event_message_detail_schema).alias("event_message_detail"))

    event_message_detail_df_3 = event_message_detail_df_2.select("event_message_detail.*")

    event_message_detail_df_4 = event_message_detail_df_3\
        .withColumn("event_server_status_color_name", split(event_message_detail_df_3["event_server_status_color_name_severity_level"], '\|')[0]) \
        .withColumn("event_server_status_severity_level", split(event_message_detail_df_3["event_server_status_color_name_severity_level"], '\|')[1]) \
        .withColumn("event_message_count", lit(1))

    postgresql_table_name = "raw_event_message_db"

    event_message_detail_df_4 \
    .writeStream \
    .trigger(processingTime='1 seconds') \
    .outputMode("update") \
    .foreachBatch(lambda current_df, epoc_id: save_to_postgresql_table(current_df, epoc_id, postgresql_table_name)) \
    .start()

    # Write result dataframe into console for debugging purpose
    event_message_detail_write_stream = event_message_detail_df_4 \
        .writeStream \
        .trigger(processingTime='1 seconds') \
        .outputMode("update") \
        .option("truncate", "false")\
        .format("console") \
        .start()
    
    event_message_detail_write_stream.awaitTermination()

    print("Real-Time Streaming Data Pipeline Completed.")
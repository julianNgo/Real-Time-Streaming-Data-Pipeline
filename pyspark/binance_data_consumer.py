from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pyspark.sql.functions as fn

# Kafka Broker
KAFKA_TOPIC_NAME_CONS = "binance-live-data-streaming"
KAFKA_BOOTSTRAP_SERVERS_CONS = '172.16.30.89:9092'
Coin_Symbol =  "btcusdt"

# PostgresSQL Database Server Details
postgresql_host_name = "172.16.30.89"
postgresql_port_no = "5432"
postgresql_user_name = "demouser"
postgresql_password = "demouser"
postgresql_database_name = "crypto_data_db"
postgresql_driver = "org.postgresql.Driver"

# Create the Database properties
db_properties = {}
db_properties['user'] = postgresql_user_name
db_properties['password'] = postgresql_password
db_properties['driver'] = postgresql_driver

def save_to_postgresql_table(current_df, epoc_id, postgresql_table_name):
    # PostgresSQL Database Server Details
    postgresql_host_name = "172.16.30.89"
    postgresql_port_no = "5432"
    postgresql_database_name = "crypto_data_db"

    print("Inside save_to_postgresql_table function")
    print("Printing epoc_id: ")
    print(epoc_id)
    print("Printing postgresql_table_name: " + postgresql_table_name)

    postgresql_jdbc_url = "jdbc:postgresql://" + postgresql_host_name + ":" + str(postgresql_port_no) + "/" + postgresql_database_name

    #Save the dataframe to the table.
    current_df.write.jdbc(url = postgresql_jdbc_url,
                  table = postgresql_table_name,
                  mode = 'append',
                  properties = db_properties)

    print("Exit out of save_to_postgresql_table function")

if __name__ == "__main__":
    print("Ingestion raw data into postgres....")
    
    spark = SparkSession \
        .builder \
        .appName("finance-data-streaming") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    event_message_detail_df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS_CONS) \
        .option("subscribe", KAFKA_TOPIC_NAME_CONS) \
        .option("startingOffsets", "latest") \
        .load()

    event_message_detail_df.printSchema()

    # Schema Code Block Starts Here
    event_message_detail_schema = StructType([
      StructField("Timestamp", StringType()),
      StructField("symbol", StringType()),
      StructField("price", StringType()),
      StructField("qty", StringType())
    ])
    # Data Processing/Data Transformation
    event_message_detail_df_1 = event_message_detail_df.selectExpr("CAST(value AS STRING)")
    event_message_detail_df_2 = event_message_detail_df_1.select(from_json(col("value"), event_message_detail_schema).alias("event_message_detail"))

    event_message_detail_df_3 = event_message_detail_df_2.select("event_message_detail.*")
    event_message_detail_df_3.printSchema()

    postgresql_table_name = "raw_data"
    event_message_detail_df_3 \
    .writeStream \
    .trigger(processingTime='5 seconds') \
    .outputMode("update") \
    .foreachBatch(lambda current_df, epoc_id: save_to_postgresql_table(current_df, epoc_id, postgresql_table_name)) \
    .start()

    # Write result dataframe into console for debugging purpose
    event_message_detail_write_stream = event_message_detail_df_3 \
        .writeStream \
        .trigger(processingTime='5 seconds') \
        .outputMode("update") \
        .option("truncate", "false")\
        .format("console") \
        .start()
    
    event_message_detail_write_stream.awaitTermination()

    print("Real-Time Streaming Data Pipeline Completed.")
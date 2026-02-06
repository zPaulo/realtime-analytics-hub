import os
import sys

# Para rodar local com pyspark; no Docker usamos spark-submit com --packages no comando
os.environ.setdefault(
    'PYSPARK_SUBMIT_ARGS',
    '--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,io.delta:delta-spark_2.12:3.0.0,org.apache.hadoop:hadoop-aws:3.3.4 pyspark-shell'
)

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, sum, window
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
from delta import *

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "http://minio:9000")
ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
DELTA_BUCKET = os.environ.get("DELTA_LAKE_BUCKET", "delta-lake")
DELTA_LAKE_PATH = f"s3a://{DELTA_BUCKET}/sales_realtime"
CHECKPOINT_PATH = f"s3a://{DELTA_BUCKET}/checkpoints/sales_realtime"

def get_spark_session():
    builder = SparkSession.builder \
        .appName("StreamingSalesAggregator") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT) \
        .config("spark.hadoop.fs.s3a.access.key", ACCESS_KEY) \
        .config("spark.hadoop.fs.s3a.secret.key", SECRET_KEY) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.sql.shuffle.partitions", "4")

    return configure_spark_with_delta_pip(builder).getOrCreate()

def main():
    spark = get_spark_session()
    spark.sparkContext.setLogLevel("WARN") 

    schema = StructType([
        StructField("event_id", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("platform", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("total", DoubleType(), True),
        StructField("product_id", StringType(), True),
        StructField("region", StringType(), True)
    ])

    df_kafka = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", "ecommerce-events") \
        .option("startingOffsets", "earliest") \
        .load()

    df_parsed = df_kafka.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*") \
        .withColumn("timestamp", col("timestamp").cast(TimestampType()))

    # Apenas vendas com total válido
    df_sales = df_parsed.filter(
        (col("event_type") == "sale") & col("total").isNotNull()
    )

    df_agg = df_sales \
        .withWatermark("timestamp", "2 minutes") \
        .groupBy(
            col("platform"),
            window(col("timestamp"), "1 minute")
        ) \
        .agg(sum("total").alias("total_revenue")) \
        .select(
            col("platform"),
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("total_revenue")
        )

    # Trigger a cada 10 segundos para micro-batches mais frequentes
    query = df_agg.writeStream \
        .format("delta") \
        .outputMode("append") \
        .option("checkpointLocation", CHECKPOINT_PATH) \
        .trigger(processingTime="10 seconds") \
        .start(DELTA_LAKE_PATH)

    query.awaitTermination()

if __name__ == "__main__":
    main()
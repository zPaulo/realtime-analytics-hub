import os
# Mesma configuração de Jars
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,io.delta:delta-spark_2.12:3.0.0,org.apache.hadoop:hadoop-aws:3.3.4 pyspark-shell'

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType, expr
from delta import *

KAFKA_SERVER = "kafka:9092"
MINIO_ENDPOINT = "http://minio:9000"
DELTA_ALERTS_PATH = "s3a://delta-lake/alerts"
CHECKPOINT_PATH = "s3a://delta-lake/checkpoints/alerts"

def get_spark_session():
    # Configuração idêntica ao anterior...
    builder = SparkSession.builder \
        .appName("AlertDetector") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT) \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") 
    return configure_spark_with_delta_pip(builder).getOrCreate()

def main():
    spark = get_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    # Schema precisa incluir stock_quantity para esse job
    schema = StructType([
        StructField("event_id", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("platform", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("product_name", StringType(), True),
        StructField("stock_quantity", IntegerType(), True), # Importante aqui
        StructField("total", DoubleType(), True)
    ])

    df_kafka = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_SERVER) \
        .option("subscribe", "ecommerce-events") \
        .load()

    df_parsed = df_kafka.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")

    # REGRA 1: Estoque Baixo
    low_stock_alerts = df_parsed.filter(
        (col("event_type") == "stock_update") & 
        (col("stock_quantity") < 10)
    ).withColumn("alert_type", lit("LOW_STOCK")) \
     .withColumn("message", expr("concat('Estoque crítico: ', product_name, ' (', stock_quantity, ' un)')"))

    # REGRA 2: Venda Grande (High Ticket)
    high_ticket_alerts = df_parsed.filter(
        (col("event_type") == "sale") & 
        (col("total") > 3000)
    ).withColumn("alert_type", lit("HIGH_TICKET")) \
     .withColumn("message", expr("concat('Venda Alta na ', platform, ': R$ ', total)"))

    # Unir alertas
    all_alerts = low_stock_alerts.unionByName(high_ticket_alerts, allowMissingColumns=True) \
        .select("timestamp", "platform", "alert_type", "message", "event_id")

    # Escrever no Delta
    query = all_alerts.writeStream \
        .format("delta") \
        .outputMode("append") \
        .option("checkpointLocation", CHECKPOINT_PATH) \
        .start(DELTA_ALERTS_PATH)

    query.awaitTermination()

if __name__ == "__main__":
    main()
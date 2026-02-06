# Job de streaming: Spark 3.5 + Kafka + Delta + S3/MinIO
FROM apache/spark:3.5.0

USER root

# Delta Spark Python API (compatível com Spark 3.5)
RUN pip install --no-cache-dir delta-spark==3.0.0

# Ivy precisa de /home/spark/.ivy2 para baixar --packages; a imagem oficial não cria esse dir (SPARK-45557)
ARG SPARK_UID=185
RUN mkdir -p /home/spark/.ivy2/cache /home/spark/.ivy2/jars \
    && chown -R ${SPARK_UID}:${SPARK_UID} /home/spark

USER ${SPARK_UID}

# Pré-baixa os JARs (Kafka, Delta, S3A) no build para não depender do Ivy em runtime
RUN echo 'from pyspark.sql import SparkSession; SparkSession.builder.getOrCreate().stop()' > /tmp/resolve_deps.py \
    && /opt/spark/bin/spark-submit --master 'local[1]' \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,io.delta:delta-spark_2.12:3.0.0,org.apache.hadoop:hadoop-aws:3.3.4 \
    /tmp/resolve_deps.py

WORKDIR /opt/spark-jobs

# Script será montado via volume; spark-submit é passado no docker-compose
ENTRYPOINT []

from pyspark.sql import SparkSession
from django.conf import settings
import pandas as pd

class DeltaLakeReader:
    """Classe para ler dados do Delta Lake"""
    
    def __init__(self):
        self.spark = self._get_spark_session()
    
    def _get_spark_session(self):
        """Cria sessão Spark configurada para MinIO"""
        spark = SparkSession.builder \
            .appName("EcommerceAPI") \
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
            .config("spark.hadoop.fs.s3a.endpoint", f"http://{settings.MINIO_ENDPOINT}") \
            .config("spark.hadoop.fs.s3a.access.key", settings.MINIO_ACCESS_KEY) \
            .config("spark.hadoop.fs.s3a.secret.key", settings.MINIO_SECRET_KEY) \
            .config("spark.hadoop.fs.s3a.path.style.access", "true") \
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
            .getOrCreate()
        
        # Reduzir logs
        spark.sparkContext.setLogLevel("ERROR")
        
        return spark
    
    def read_table(self, table_name):
        """
        Lê uma tabela Delta Lake e retorna como Pandas DataFrame
        
        Args:
            table_name: Nome da tabela (ex: 'sales_realtime')
        
        Returns:
            pandas.DataFrame
        """
        try:
            path = settings.DELTA_TABLES.get(table_name)
            if not path:
                raise ValueError(f"Tabela {table_name} não configurada")
            
            df = self.spark.read.format("delta").load(path)
            return df.toPandas()
        
        except Exception as e:
            print(f"Erro ao ler tabela {table_name}: {e}")
            return pd.DataFrame()
    
    def read_sales_realtime(self):
        """Lê vendas em tempo real"""
        return self.read_table('sales_realtime')
    
    def read_alerts(self):
        """Lê alertas ativos"""
        return self.read_table('alerts')
    
    def read_stock_levels(self):
        """Lê níveis de estoque"""
        return self.read_table('stock_levels')
    
    def get_sales_by_platform(self):
        """Agregação: vendas por plataforma"""
        df = self.read_sales_realtime()
        if df.empty:
            return []
        
        result = df.groupby('platform')['total'].sum().to_dict()
        return [{'platform': k, 'revenue': v} for k, v in result.items()]
    
    def get_top_products(self, limit=10):
        """Top produtos mais vendidos"""
        df = self.read_sales_realtime()
        if df.empty:
            return []
        
        top = df.groupby('product_name')['total'].sum() \
                .sort_values(ascending=False) \
                .head(limit)
        
        return [{'product': k, 'revenue': v} for k, v in top.items()]
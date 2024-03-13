# dynamic_resource_allocation.py

from pyspark.sql import SparkSession

# Initialize SparkSession with dynamic resource allocation enabled
spark = SparkSession.builder \
    .appName("DynamicResourceAllocation") \
    .config("spark.dynamicAllocation.enabled", "true") \
    .config("spark.dynamicAllocation.maxExecutors", "4") \
    .config("spark.dynamicAllocation.minExecutors", "1") \
    .getOrCreate()

# Your Spark job code here

# Stop SparkSession
spark.stop()

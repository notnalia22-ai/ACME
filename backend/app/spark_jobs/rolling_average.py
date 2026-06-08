from pyspark.sql import SparkSession
from pyspark.sql.functions import avg
from pyspark.sql.window import Window

spark = (
    SparkSession.builder
    .appName("RollingAverage")
    .getOrCreate()
)

data = [
    ("2024-01-01", 100.0),
    ("2024-01-02", 101.0),
    ("2024-01-03", 103.0),
    ("2024-01-04", 104.0),
    ("2024-01-05", 105.0),
]

df = spark.createDataFrame(
    data,
    ["record_date", "close_price"]
)

window = (
    Window
    .orderBy("record_date")
    .rowsBetween(-2, 0)
)

result = df.withColumn(
    "rolling_avg",
    avg("close_price").over(window)
)

result.show()

spark.stop()

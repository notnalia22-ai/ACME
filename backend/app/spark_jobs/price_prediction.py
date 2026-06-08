from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression

spark = (
    SparkSession.builder
    .appName("PricePrediction")
    .getOrCreate()
)

data = [
    (1, 100.0),
    (2, 102.0),
    (3, 104.0),
    (4, 107.0),
    (5, 110.0),
]

df = spark.createDataFrame(
    data,
    ["day", "close_price"]
)

assembler = VectorAssembler(
    inputCols=["day"],
    outputCol="features"
)

dataset = assembler.transform(df)

model = LinearRegression(
    featuresCol="features",
    labelCol="close_price"
).fit(dataset)

predictions = model.transform(dataset)

predictions.select(
    "day",
    "close_price",
    "prediction"
).show()

spark.stop()

from pyspark.sql import SparkSession
from pyspark.sql.functions import lit

# Создаем сессию Spark
spark = SparkSession.builder.appName("product_category_pairs").getOrCreate()

# Создаем датафреймы с продуктами и категориями
products = spark.createDataFrame([
    ("Продукт1",),
    ("Продукт2",),
    ("Продукт3",),
], ["product_name"])

categories = spark.createDataFrame([
    ("Категория1",),
    ("Категория2",),
    ("Категория3",),
], ["category_name"])

# Создаем датафрейм с парами продуктов и категорий
product_category_pairs = products.crossJoin(categories)

# Объединяем с исходными данными продуктов для включения продуктов без категорий
final_result = products.join(product_category_pairs, "product_name", "left").select(
    "product_name",
    "category_name"
)

# Показываем результат
final_result.show()

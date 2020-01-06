import sys
import json
import pymongo
from pymongo import MongoClient
from pyspark import SparkContext
from pyspark import SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql import Row, DataFrame, SQLContext
from textblob import TextBlob

def getSqlContextInstance(sparkContext):
    if ('sqlContextSingletonInstance' not in globals()):
        globals()['sqlContextSingletonInstance'] = SQLContext(sparkContext)
    return globals()['sqlContextSingletonInstance']


# Convert RDDs of the words DStream to DataFrame and run SQL query
def process(time, rdd):
    print("========= %s =========" % str(time))
    try:
        # Get the singleton instance of SparkSession
        sqlContext = getSqlContextInstance(rdd.context)

        # Convert RDD[String] to RDD[Row] to DataFrame
        #rowRdd = rdd.map(lambda w: Row(word=w))
        rowRdd = rdd.map(lambda w: Row(word=w[0], cnt=w[1]))
        #rowRdd.pprint()
        wordsDataFrame = sqlContext.createDataFrame(rowRdd)
        wordsDataFrame.show()

        # Creates a temporary view using the DataFrame.
        wordsDataFrame.createOrReplaceTempView("words")

        # Do word count on table using SQL and print it
        wordCountsDataFrame = \
             spark.sql("select SUM(cnt) as total from words")
        wordCountsDataFrame.show()
    except:
       pass

def sendRecord(partition):
   client = MongoClient("mongodb://root:root@mongo-headless.project.svc.cluster.local:27017")
   db = client['demodb']
   db.democollection.insert_many(partition)

def get_sentiment_tuple(sent):
    neutral_threshold = 0.05
    if sent >= neutral_threshold:       # positive
        return 'positive'
    elif sent > -neutral_threshold:     # neutral
        return 'neutral'
    else:                               # negative
        return 'negative'
    
def analyze_sentiment(text):
    testimonial = TextBlob(text)
    return testimonial.sentiment.polarity

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: kafka_spark_dataframes.py <zk> <topic>", file=sys.stderr)
        exit(-1)

    sc = SparkContext(appName="PythonStreamingKafkaApp")
    sc.setLogLevel("OFF")
    sqlContext = SQLContext(sc)
    ssc = StreamingContext(sc, 5)

    zkQuorum, topic = sys.argv[1:]
    kvs = KafkaUtils.createStream(ssc, zkQuorum, "spark-streaming-consumer", {topic: 1})
    lines = kvs.map(lambda x: json.loads(x[1]))
    lines.foreachRDD(lambda rdd: rdd.foreachPartition(sendRecord))

    user_senitiment = lines.map(lambda lines: '{"tweet_sentiment": {"user":"' + lines["user"]["screen_name"] + '", "tweet":"' + lines["text"] + '", "sentiment":"' + get_sentiment_tuple(analyze_sentiment(lines["text"]))+'"}}')
    user_senitiment.pprint()

    tweets = lines.map(lambda lines: lines['text'])
    words = tweets.flatMap(lambda line: line.split(" ")) \
        .map(lambda word: (word, 1)) \
        .reduceByKey(lambda a, b: a+b)

    words.foreachRDD(process)

    ssc.start()
    ssc.awaitTermination()
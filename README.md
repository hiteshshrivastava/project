# project

One Paragraph of project description goes here

## Getting Started

### Installing

#### 1. Start Minikube

```
minikube config set memory 10240
minikube start
```

![Start Minikube](images/minikube_setup.png)


#### 2. Set-up Namespace

```
kubectl create namespace project
```
![Setup Nifi](images/namespace_creation.png)


#### 3. Set-up Zookeeper

```
kubectl create -n project -f ./kubernetes/zookeeper.yaml
```
![Setup Nifi](images/zookeeper_creation.png)


#### 4. Set-up Nifi

```
kubectl create -n project -f ./kubernetes/nifi.yaml
```

![Setup Nifi](images/nifi_creation.png)


#### 5. Set-up Kafka

```
kubectl create -n project -f ./kubernetes/kafka.yaml
```

![Setup Kafka](images/kafka_creation.png)


#### 6. Set-up Spark

```
kubectl create -n project -f ./kubernetes/spark-master.yaml
kubectl create -n project -f ./kubernetes/spark-worker.yaml
```

![Setup Spark](images/spark_creation.png)


#### 7. Set-up MongoDB

```
kubectl create -n project -f ./kubernetes/mongodb.yaml
```

![Setup Spark](images/mongodb_creation.png)


#### 8. Set-up MongoDB Charts

```
kubectl create -n project -f ./kubernetes/mongodb-charts.yaml
```

![Setup Spark](images/mongodb_charts_creation.png)


#### Import NiFi Template 

On Nifi canvas click upload template and browse for below template xml
* [Template](nifi-templates/twitter_analysis_process_group_demo.xml) - twitter_analysis_process_group_demo.xml

![Template](images/nifi_template_import.png)

![Template](images/nifi_flow.png)

Setup Twitter API Secrets/Token properties
![Template](images/nifi_get_twitter_processor.png)

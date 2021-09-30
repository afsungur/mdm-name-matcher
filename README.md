# Customer Name Matching Based on Similarity Score


An example of how the similar records are matched and merged for Master Data Management platforms. 

This toolkit takes one field of one collection and creates a distance matrix for the names of customers and then based on given threshold it merges the customers into the master record.

This toolkit only imitates the customer name matching based on a calculated distance matrix but it can be further extended to match other kind of fields like address, email, etc. 

# Pre-requisites

Already running MongoDB Server. This toolkit was tested against MongoDB version 4.4.0.

OS tool:

 - python3
 
Python3 Libraries (install those with pip3)

 - scikit-learn
 - pymongo
 - numpy
 - leven (https://pypi.org/project/leven/)

I've used Python 3.9.6 and Pip3: pip 21.1.3 under macOS, it worked fine.

# Files

**name_matching.py** : It includes all logic for retrieving data from MongoDB, matching data with ML libraries and loading the merged records into the database.

**customer_data.json** : Customer Data already generated by *mgeneratejs* toolkit -- 1,000 records
**tx_data.json** : Transaction Data already generated by *mgeneratejs* toolkit -- 10,000 records 

# How to use it

### Importing Data into MongoDB

After this repository is pulled, dumped json data can be imported:

    $ mongoimport --db  bank --collection  customers --file  customer_data.json --drop
    $ mongoimport --db  bank --collection  transactions --file  tx_data.json --drop


### Creating Indexes

In order to merge the data quickly, following indexes can be created in `transactions` collection.

    $  mongo
    use  bank 
    db.transactions.createIndex({customerId:1})


### Execute

In order to start merge operation, following can be executed:

    $ python3 name_matching.py

### View the merged records

    $ mongo
    use bank
    db.master_customers.find({})

# Matching Logic

Master Data Management (MDM) is a concept of providing single source of truth by cleansing/transforming/merging the records from multiple systems. 

Some of the off-the-shelf MDM solutions comes up with a probabilistic engine and basically it matches the similar records. There are many similarity machine algorithms are executed under the hood. 

This demo toolkit basically find the similar records by checking only names of the customer then merge that records in one master record. For example, "Johny Depp" and "Johnny Deep" could be 2 different names however since those records are similar to each then it can be merged into one record if the similarity score is more than given threshold. 

Comparing only names to merge different customers into one single record will not be enough. There could be some other comparison should also be handled in real production deployment. This toolkit only compares the names.

## String Matching Algorithms

One of the most common string matching algorithm is [Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance). Basically, it calculates how many characters should be substituted  to reach the target string.

    funcLevenshtein('FUAT','FUAD')=1
    funcLevenshtein('Johnny Deep','Johny Depp')=2

There are some other algorithms like [Jaro-Winkler](https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance). That gives more ratings to string where first characters are similar to the target. 

Depend on the situation one of them can be chosen. In this toolkit, only Levenshtein distance metric has been used.

### Normalizing the Distance

In order to compare values properly value are normalized into the [0..1] interval instead of exact distance. 

### Distance Matrix

After we decide the algorithm, we have to define the distance matrix which represents to distance of each data points. As following in the below:

```markdown
|        | Fuat | Fuad | John | Johnny |
|--------|------|------|------|--------|
| Fuat   |      | 0.01 | 0.5  | 0.6    |
| Fuad   | 0.01 |      | 0.5  | 0.6    |
| John   | 0.5  | 0.5  |      | 0.01   |
| Johnny | 0.6  | 0.6  | 0.01 |        |
```

## Hierarchical Clustering

Clustering is an unsupervised Machine Learning technique to grouping of the data. Since we are looking for merging similar records then we can apply this method. 

Agglomerative Clustering is a way of Hierarchical Clustering. In the beginning each data point has own cluster and iteratively, similar clusters are merged. It is also called as bottom-up approach.

[Single-Linkage Clustering](https://en.wikipedia.org/wiki/Single-linkage_clustering) is a way of Agglomerative Clustering. It decides the distance of two clusters by checking the closest two points of each cluster. In this toolkit, we are using this way. 

Other methods are:

 - [Complete-Linkage Clustering](https://en.wikipedia.org/wiki/Complete-linkage_clustering) : It decides the distance of two clusters by checking the farthest two points of each cluster. 
 - Average-Linkage Clustering: It decides the distance of two clusters by checking the average distance of each points in 2 clusters. 

### Single-Linkage Clustering

After we have distance matrix, then we can execute our single-linkage clustering. Which is going to merge relevant clusters depend on the distance parameter in the scikit function. For example, if the distance parameter is 0.02, it means that the 2 clusters are merged if the distance metric of the 2 clusters are less or equal than 0.02. In order to make it user friendly, we used percentage threshold like %95 and we do needed math to give distance parameter to the function.

After scikit function has been executed, it gives us which data points 

You can find the more details about the scikit implementation of Agglomerative Clustering, you can refer to following link:

https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html

# Screenshots

## Customers and Transactions Source Collections:

![Alt text](/ss001.png?raw=true "customers Collection")
![Alt text](/ss002.png?raw=true "transactions Collection")

## After the similar records matched, it is merged under master_customers collection 

![Alt text](/ss003.png?raw=true "master_customers collection")

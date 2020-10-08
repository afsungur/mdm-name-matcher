from leven import levenshtein
import numpy as np
from sklearn.cluster import dbscan
from sklearn.cluster import AgglomerativeClustering
import pymongo

# MongoDB Connection
connection = pymongo.MongoClient("mongodb://localhost:27017")
db=connection.bank
collection=db.customers
master_collection=db.master_customers
tx_collection=db.transactions
fullNameArray=[]

def lev_metric(x, y):
    #return levenshtein(x,y)
    maximum=max(len(x),len(y))
    distance=levenshtein(x,y)/maximum
    return distance

# Fill the Python Array with fullName and _id fields of each customer
curs=collection.find({},{"fullName":1})
for doc in curs:
    name_tuple=(doc['fullName'],doc['_id'])
    fullNameArray.append(name_tuple) 


# Initialize the distance matrix with the value 0
M=len(fullNameArray)
N=len(fullNameArray)
distance_matrix = [ [ 0 for i in range(M) ] for j in range(N) ]

# Calculate the distance between each record
for i in range(M):
    for j in range(N):
        distance_matrix[i][j]=lev_metric(fullNameArray[i][0],fullNameArray[j][0])

# If you have small distance matrix you can print and see the results
#print(distance_matrix)

# User friendly similarity threshold
similarity_threshold=75

# execute single-linkage clustering algorithm
clustering = AgglomerativeClustering(n_clusters=None, affinity="precomputed", compute_full_tree=True, linkage="single", distance_threshold=(100-similarity_threshold)/100).fit(distance_matrix)

# Show how many clusters are generated
# If the value is equal to number of customers then no merge operation happened
print(clustering.n_clusters_)

# Show which data point belongs to which cluster -- it is 1 dimensional array
print(clustering.labels_)

# Print the cluster 0 elements -- which records are merged for the cluster 0
for i in range(len(clustering.labels_)):
        if (clustering.labels_[i]==0):
            print(f"Name: {fullNameArray[i][0]}")
            print(f"Id: {fullNameArray[i][1]}")

# Merging the records into master_customers collection together with similar customer records and their transactions
master_collection.delete_many({})
for i in range(len(clustering.labels_)):
    index="MSTR"+str(clustering.labels_[i])
    customer_doc=collection.find_one({"_id":fullNameArray[i][1]})
    tx_cursor=tx_collection.find({"customerId": fullNameArray[i][1]})
    transactions=[]
    for tx in tx_cursor:
        transactions.append(tx)

    master_collection.update_one(
            {"_id":index},
            {
                '$inc': {'numberOfSourceCustomers':1}, 
                '$push': {'customers': customer_doc, 'transactions': {'$each': transactions} }
            },upsert=True)



import json

def insert_data(data, db):

    # Your code here. Insert the data into a collection 'vancouver'
    db.vancouver.insert(data)


if __name__ == "__main__":
    
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.vancouver
    data = []
    with open('vancouver_canada.osm.json') as f:
        for line in f:
            data.append(json.loads(line))
        insert_data(data, db)
        print db.vancouver.find_one()
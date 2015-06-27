#!/usr/bin/env python
import pprint

def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

def make_pipeline():
    # list unique names of sport tags
    #pipeline = [ { "$match" : {"sport" : {"$ne" : None}}},
    #             { "$group" : { "_id" : "$sport", "count" : { "$sum" : 1 } } },
    #             { "$sort" : { "count" : -1 } },
    #             { "$limit" : 10 }]
                 
    # list of matched skateparks
    pipeline = [ { "$match" : { "sport" : "skateboard" } },
                 { "$project" : { "_id" : 0 , "sport" : 1 , "name" : 1 } }]
                 
    # list of matched cycleways
    #pipeline = [ { "$match" : { "highway" : "cycleway" } },
    #             { "$group" : { "_id" : "$name", "count" : { "$sum" : 1 } } },
    #             { "$sort" : { "count" : -1 } },
    #             { "$limit" : 10 }]
                 
    # most popular cuisine
    #pipeline = [ { "$match" : { "cuisine" : {"$ne" : None} , "amenity" : { "$exists" : 1 }, "amenity" : "restaurant" } },
    #             { "$group" : { "_id" : "$cuisine" , "count" : { "$sum" : 1 } } },
     #            { "$sort" : { "count" : -1 } },
      #           { "$limit" : 5}]
    
    return pipeline

def simple_query(db):
    # For local use
    query = {}
    query["documents"] = db.vancouver.find().count()
    query["nodes"] = db.vancouver.find({"type":"node"}).count()
    query["ways"] = db.vancouver.find({"type":"way"}).count()
    query["users"] = len(db.vancouver.distinct("created.user"))
    return query

def aggregate(db, pipeline):
    result = db.vancouver.aggregate(pipeline)
    return result

if __name__ == '__main__':
    # The following statements will be used to test your code by the grader.
    # Any modifications to the code past this point will not be reflected by
    # the Test Run.
    db = get_db('vancouver')
    
    #comment in or out below if you want to run a pipeline
    
    pipeline = make_pipeline()
    agg_result = aggregate(db, pipeline)
    for doc in agg_result:
        pprint.pprint(doc)
        
        
    #comment in or out below if you want to return simple query
    """
    result = simple_query(db)
    print result
    """
    
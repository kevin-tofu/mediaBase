
import config
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

class mongo_client(object):
    
    def __init__(self, config):
        self._client = MongoClient(config.MONGODB_URL)
        # client_2 = MongoClient('localhost', 27017)
        # client_3 = MongoClient('mongodb://localhost:27017/') 
        self._db = self._client[config.MONGODB_DATABASE]
        self._collection = self._db[config.MONGODB_COLLECTION]

    def insert_item(self, data):
        return self._collection.insert_one(data).inserted_id

    def get_item_id(self, item_id):
        return self._collection.find_one({"_id": ObjectId(item_id)})
    
    def get_item_query(self, query):
        return self._collection.find_one(query)


    def update_item(self, item_id, data):
        result = self._collection.update_one({"_id": ObjectId(item_id)}, \
                                             {"$set": data})
        if result.matched_count:
            result = self._collection.find_one({"_id": ObjectId(item_id)})
            return result
        return None

    def delete_item(self, item_id):
        result = self._collection.delete_one({"_id": ObjectId(item_id)})
        if result.deleted_count:
            return True
        return None

    def get_all_items(self):
        return [x for x in self._collection.find({})]

    

client = mongo_client(config)


if __name__ == '__main__':

    data = {
        "test0": 1234,
        "test1": "1234"
    }
    _id = client.insert_item(data)
    result = client.delete_one(_id)
    print(result)
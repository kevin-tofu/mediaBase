
# import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

class mongo_client(object):
    
    def __init__(self, _config):
        
        print(f"MONGODB_URL: {_config.MONGODB_URL}")
        print(f"MONGODB_DATABASE: {_config.MONGODB_DATABASE}")
        print(f"MONGODB_COLLECTION: {_config.MONGODB_COLLECTION}")

        self._client = MongoClient(_config.MONGODB_URL)
        # client_2 = MongoClient('localhost', 27017)
        # client_3 = MongoClient('mongodb://localhost:27017/') 
        self._db = self._client[_config.MONGODB_DATABASE]
        self._collection = self._db[_config.MONGODB_COLLECTION]

        if False:
            data = {
            "test0": 1234,
            "test1": "1234"
            }
            _id = self.insert_item(data)
            result = self.delete_item(_id)
            print(_id, result)


    def insert_item(self, data):
        inserted_id = self._collection.insert_one(data).inserted_id
        return inserted_id

    def get_item_id(self, item_id):
        return self._collection.find_one({"_id": ObjectId(item_id)})
    
    def get_item_query(self, query):
        return self._collection.find_one(query)


    def update_item_id(self, item_id, data):
        result = self._collection.update_one({"_id": ObjectId(item_id)}, \
                                             {"$set": data})
        if result.matched_count:
            result = self._collection.find_one({"_id": ObjectId(item_id)})
            return result
        return None

    def update_item_key(self, _key, _key_item, _keyupdate, _keyupdate_item):
        update = self._collection.update_one({_key: _key_item}, \
                                             {'$set': {_keyupdate: _keyupdate_item}}
        )
        return update

    def delete_item(self, item_id):
        result = self._collection.delete_one({"_id": ObjectId(item_id)})
        if result.deleted_count:
            return True
        return None

    def get_all_items(self):
        return [x for x in self._collection.find({})]



if __name__ == '__main__':

    import os
    import sys
    if __name__ == "__main__":
        sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
    import config
    
    myclient = mongo_client(config)

    data = {
        "test0": 1234,
        "test1": "1234"
    }
    _id = myclient.insert_item(data)
    result = myclient.delete_item(_id)
    print(_id, result)
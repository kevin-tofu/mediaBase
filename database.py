
# import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

class mongo_client(object):
    
    def __init__(self, _config, validator=None):
        
        print(f"MONGODB_URL: {_config.MONGODB_URL}")
        print(f"MONGODB_PORT: {_config.MONGODB_PORT}")
        print(f"MONGODB_DATABASE: {_config.MONGODB_DATABASE}")
        print(f"MONGODB_COLLECTION: {_config.MONGODB_COLLECTION}")

        if _config.MONGODB_USER is None or _config.MONGODB_PASSWORD is None:
            url = f'mongodb://{_config.MONGODB_URL}:{_config.MONGODB_PORT}'
        else:    
            url = f'mongodb://%s:%s@{_config.MONGODB_URL}:{_config.MONGODB_PORT}' % (_config.MONGODB_USER, _config.MONGODB_PASSWORD)
        print(f"url : {url}")
        self._client = MongoClient(url)
        # client_2 = MongoClient('localhost', 27017)
        # client_3 = MongoClient('mongodb://localhost:27017/') 
        self._db = self._client[_config.MONGODB_DATABASE]

        has_collection = _config.MONGODB_COLLECTION in self._db.list_collection_names()
        if validator is None or has_collection == True:
                self._collection = self._db[_config.MONGODB_COLLECTION]
        else:
            if has_collection == False:
                self._collection = self._db.create_collection(_config.MONGODB_COLLECTION, \
                                                              validator=validator)

    def insert_item(self, data):
        # inserted_id = self._collection.insert_one(data).inserted_id
        # return inserted_id
        result = self._collection.insert_one(data)
        return result
        

    def get_item_id(self, item_id: str):
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

    def delete_item(self, item_id: str):
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

    validator = {
        '$jsonSchema': {
            'bsonType': 'object',
            'additionalProperties': True,
            'required': ['component', 'path'],
            'properties': {
                'component': {
                    'bsonType': 'string'
                },
                'path': {
                    'bsonType': 'string',
                    'description': 'Set to default value'
                }
            }
        }
    }

    
    myclient = mongo_client(config, validator=validator)

    data_1 = {
        "component": "this is a component",
        "path": "this is a path"
    }

    data_2 = {
        "test0": 1234,
        "test1": "1234"
    }
    
    _id = myclient.insert_item(data_1).inserted_id
    result = myclient.delete_item(_id)
    print("id, result : ", _id, result)

    _id = myclient.insert_item(data_2).inserted_id # error must be occurred
    # result = myclient.delete_item(_id)
    # print(_id, result)
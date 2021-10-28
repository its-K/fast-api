from dotenv import load_dotenv
import pymongo, os
load_dotenv()

class db:
    def connect_database():
        client = pymongo.MongoClient(os.getenv('MONGO_STRING'))
        db = client['app']
        return db

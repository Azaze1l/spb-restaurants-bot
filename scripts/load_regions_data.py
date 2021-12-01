import json
from sys import argv

from pymongo import MongoClient

from app.config import settings
from app.db.districts import collection

# _, regions_geojson_data_filepath = argv
regions_geojson_data_filepath = "admin_level_5.geojson"
spb_regions = []
with open(regions_geojson_data_filepath, encoding="utf-8") as json_file:
    regions = json.load(json_file)["features"]
for region in regions:
    if region["properties"].get("addr:region") == "Санкт-Петербург":
        spb_regions.append(region)
client = MongoClient(
    settings.MONGODB_CONNECTION_URL,
    serverSelectionTimeoutMS=10,
)

db = client[settings.MONGO_DB]
db[collection].delete_many({})
db[collection].insert_many(spb_regions)
db[collection].create_index([("geometry", "2dsphere")])
print("Federation regions data is update with current data from .geojson file")

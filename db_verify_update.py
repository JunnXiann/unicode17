import json
from pymongo import MongoClient, UpdateOne
from tqdm import tqdm  # <--- Added tqdm for the progress bar

def verify_and_update_db(json_file="db_payload.json", db_uri="mongodb://localhost:27017/", db_name="your_db", coll_name="your_collection"):
    # 1. Connect to MongoDB
    client = MongoClient(db_uri)
    db = client[db_name]
    collection = db[coll_name]

    # 2. Load the JSON payload
    with open(json_file, "r", encoding="utf-8") as f:
        payloads = json.load(f)
    
    update_existing = payloads.get("update_existing", {})
    insert_new = payloads.get("insert_new", [])

    print("--- STEP 1: VERIFICATION ---")
    db_unicodes = set(doc["unicode"] for doc in collection.find({}, {"unicode": 1}))
    folder_unicodes = set(update_existing.keys())

    rogue_unicodes = folder_unicodes - db_unicodes

    if rogue_unicodes:
        print(f"⚠️ WARNING: Found {len(rogue_unicodes)} characters in your folders that DO NOT exist in the database!")
        print(f"Rogue Unicodes: {rogue_unicodes}")
        print("Please investigate these before continuing.")
        
        for rogue in rogue_unicodes:
            del update_existing[rogue]
        print("-> Rogue characters removed from the update queue.")
    else:
        print("✅ All folder characters match the database perfectly.")

    print("\n--- STEP 2: DATABASE UPDATE ---")
    confirm = input("Do you want to proceed with the database update? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return

    # 3. Bulk Update Existing Records (NOW WITH BATCHING & PROGRESS BAR)
    if update_existing:
        print(f"Updating {len(update_existing)} existing documents...")
        bulk_operations = []
        total_modified = 0
        batch_size = 1000  # Process 1,000 at a time
        
        # Convert to list so tqdm can track the total length
        update_items = list(update_existing.items())
        
        # Wrap the loop with tqdm!
        for unicode_str, update_data in tqdm(update_items, desc="Updating Database", unit="char"):
            operation = UpdateOne(
                {"unicode": unicode_str}, 
                {"$set": update_data}, 
                upsert=False
            )
            bulk_operations.append(operation)
            
            # Execute the batch when we hit 1,000
            if len(bulk_operations) >= batch_size:
                # ordered=False allows MongoDB to process them in parallel (much faster!)
                result = collection.bulk_write(bulk_operations, ordered=False)
                total_modified += result.modified_count
                bulk_operations = [] # Reset the batch
        
        # Process any leftover documents (the final batch)
        if bulk_operations:
            result = collection.bulk_write(bulk_operations, ordered=False)
            total_modified += result.modified_count
            
        print(f"\n✅ Update Complete: Modified {total_modified} documents.")

    # 4. Insert New Extension J Records
    if insert_new:
        print(f"\nInserting {len(insert_new)} NEW Extension J documents...")
        # insert_many is automatically batched by pymongo, so it will be lightning fast
        result = collection.insert_many(insert_new, ordered=False)
        print(f"✅ Insert Complete: Inserted {len(result.inserted_ids)} documents.")

if __name__ == "__main__":
    verify_and_update_db(
        db_uri="mongodb://write_aux_system:AUX1Ad97!RzPu@127.0.0.1:29019/tripitaka-aux", 
        db_name="tripitaka-aux", 
        coll_name="gbhan"
    )
import os
import json

def load_unicodes_mapping(txt_path="./unicodes.txt"):
    """
    Reads the unicodes.txt file and returns a dictionary mapping
    the Hex string (e.g., '4E00') to its ID, Character, and Block Name.
    """
    mapping = {}
    if not os.path.exists(txt_path):
        print(f"Error: {txt_path} not found!")
        return mapping

    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            # skip first line
            if line.startswith("序号\t"):
                continue

            parts = line.split("\t")
            if len(parts) >= 4:
                doc_id = int(parts[0].strip())
                txt_char = parts[1].strip()
                # Remove the "U+" prefix to match our folder filenames
                unicode_hex = parts[2].replace("U+", "").strip() 
                region_name = parts[3].strip()
                
                mapping[unicode_hex] = {
                    "no": doc_id,
                    "txt": txt_char,
                    "region": region_name
                }
    return mapping

def generate_db_payloads(base_dir="./unicode_150", txt_path="./unicodes.txt", output_file="db_payloads.json"):
    # 1. Load the single source of truth
    unicode_mapping = load_unicodes_mapping(txt_path)
    if not unicode_mapping:
        return

    updates_payload = {}
    inserts_temp = {}

    # 2. Scan folders and group data by unicode
    for root, _, files in os.walk(base_dir):
        for file in files:
            if not file.lower().endswith(".jpg"):
                continue
            
            # Extract folder info
            path_parts = os.path.normpath(root).split(os.sep)
            if len(path_parts) < 2:
                continue
                
            page_num_17 = int(path_parts[-1])
            pdf_name_17 = path_parts[-2]

            # Extract filename info
            filename_without_ext = os.path.splitext(file)[0]
            if "_" not in filename_without_ext:
                continue
                
            unicode_str, standard_str = filename_without_ext.split("_", 1)

            # Safety check: Is this image actually tracked in our unicodes.txt?
            if unicode_str not in unicode_mapping:
                print(f"⚠️ Warning: Image {os.path.join(root, file)} has Unicode {unicode_str}, but it is missing from {txt_path}. Skipping.")
                continue

            # Fetch the authoritative metadata from unicodes.txt
            meta = unicode_mapping[unicode_str]
            doc_id = meta["no"]

            # Route logic based on the ID threshold
            if doc_id <= 99066:
                # UPDATE EXISTING
                if unicode_str not in updates_payload:
                    updates_payload[unicode_str] = {
                        "pdf_name_17": pdf_name_17,
                        "page_num_17": page_num_17,
                        "standards_17": [],
                        "b_unicode_17": False
                    }
                updates_payload[unicode_str]["standards_17"].append(standard_str)
                
            else:
                # INSERT NEW
                if unicode_str not in inserts_temp:
                    # We store the metadata we pulled from the text file temporarily
                    inserts_temp[unicode_str] = {
                        "no": doc_id,
                        "txt": meta["txt"],
                        "region": meta["region"],
                        "pdf_name_17": pdf_name_17,
                        "page_num_17": page_num_17,
                        "standards_17": []
                    }
                inserts_temp[unicode_str]["standards_17"].append(standard_str)

    # 3. Process the new inserts into full database documents
    new_documents = []
    
    # Sort by keys to keep the list organized
    for unicode_str in sorted(inserts_temp.keys()):
        data = inserts_temp[unicode_str]
        
        # Determine Chinese region name (Optional nice-to-have to match your DB style)
        db_region = "扩展J" if "Extension J" in data["region"] else ("扩展C" if "Extension C" in data["region"] else ("扩展E" if "Extension E" in data["region"] else data["region"]))
        batch = "U-J" if "Extension J" in data["region"] else ("U-C" if "Extension C" in data["region"] else ("U-E" if "Extension E" in data["region"] else ""))

        new_doc = {
            "no": data["no"],
            "unicode": unicode_str,
            "region": db_region,
            "txt": data["txt"],
            "standards_17": data["standards_17"],
            "pdf_name_17": data["pdf_name_17"],
            "page_num_17": data["page_num_17"],
            "pdf_name": "",
            "page_num": "",
            "standards": [],
            "batch": batch,
            "b_kxs4_1": False,
            "b_simsun": False,
            "b_th4_1": False,
            "b_kxs3_0": False,
            "b_gb18030": False,
            "b_gb18030_2025": False,
            "b_unicode_17": False
        }
        new_documents.append(new_doc)

    # 4. Compile and save the final JSON
    final_output = {
        "update_existing": updates_payload,
        "insert_new": new_documents
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)
        
    print(f"\n✅ Extraction complete!")
    print(f"- Processed {len(updates_payload)} existing characters for Updates (ID <= 99066).")
    print(f"- Processed {len(new_documents)} new characters for Inserts (ID > 99066).")
    print(f"Data safely written to {output_file}.")

if __name__ == "__main__":
    generate_db_payloads(base_dir="./unicode_150", txt_path="./unicodes.txt", output_file="./db_payload.json")
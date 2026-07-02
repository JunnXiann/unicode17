import os
import json

def generate_db_payloads(base_dir="./unicode_150", output_file="db_payloads.json"):
    updates_payload = {}
    inserts_temp = {}

    # 1. Scan folders and group data by unicode
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

            # Route to the correct payload logic based on the folder (PDF name)
            if pdf_name_17 == "U323B0":
                if unicode_str not in inserts_temp:
                    inserts_temp[unicode_str] = {
                        "pdf_name_17": pdf_name_17,
                        "page_num_17": page_num_17,
                        "standards_17": []
                    }
                inserts_temp[unicode_str]["standards_17"].append(standard_str)
            else:
                if unicode_str not in updates_payload:
                    updates_payload[unicode_str] = {
                        "pdf_name_17": pdf_name_17,
                        "page_num_17": page_num_17,
                        "standards_17": [],
                        "b_unicode_17": False
                    }
                updates_payload[unicode_str]["standards_17"].append(standard_str)

    # 2. Process the Extension J inserts to build full database documents
    new_documents = []
    next_no = 99067
    
    # We sort by unicode keys to ensure the 'no' increments sequentially
    for unicode_str in sorted(inserts_temp.keys()):
        data = inserts_temp[unicode_str]
        
        # Convert hex string (e.g., "323B0") to the actual character
        txt_char = chr(int(unicode_str, 16))

        new_doc = {
            "no": next_no,
            "unicode": unicode_str,
            "region": "扩展J",
            "txt": txt_char,
            "standards_17": data["standards_17"],
            "pdf_name_17": data["pdf_name_17"],
            "page_num_17": data["page_num_17"],
            "pdf_name": "",
            "page_num": "",
            "standards": [],
            "batch": "U-J",
            "b_kxs4_1": False,
            "b_simsun": False,
            "b_th4_1": False,
            "b_kxs3_0": False,
            "b_gb18030": False,
            "b_gb18030_2025": False,
            "b_unicode_17": False
        }
        new_documents.append(new_doc)
        next_no += 1

    # 3. Compile and save the final JSON
    final_output = {
        "update_existing": updates_payload,
        "insert_new": new_documents
    }

    with open(output_file, "w", encoding="utf-8") as f:
        # ensure_ascii=False ensures that the Chinese characters in "region" and "txt" render correctly
        json.dump(final_output, f, indent=4, ensure_ascii=False)
        
    print(f"Extraction complete!")
    print(f"- Found {len(updates_payload)} unique existing characters to update.")
    print(f"- Generated {len(new_documents)} NEW Extension J documents to insert.")
    print(f"Data saved to {output_file}.")

if __name__ == "__main__":
    generate_db_payloads(base_dir="./unicode_150")
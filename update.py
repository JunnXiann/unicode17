def append_extension_j(txt_path="./unicodes.txt"):
    # Define the range and starting ID
    start_hex = 0x323B0
    end_hex = 0x33479
    start_id = 99067  # Starts right after your last ID (97673)
    block_name = "CJK Unified Ideographs Extension J"

    # Open the file in append mode ('a') with UTF-8 encoding
    with open(txt_path, "a", encoding="utf-8") as f:
        current_id = start_id

        # Loop through the unicode code points
        for code_point in range(start_hex, end_hex + 1):
            # chr() converts the integer code point to the actual character
            character = chr(code_point)

            # Format the hex string to uppercase, e.g., "323B0"
            hex_str = f"U+{code_point:X}"

            # Construct the line with tab separators (\t)
            line = f"{current_id}\t{character}\t{hex_str}\t{block_name}\n"

            # Write to file
            f.write(line)
            current_id += 1

    total_added = current_id - start_id
    print(f"Successfully appended {total_added} characters to {txt_path}.")
    print(f"Last ID added: {current_id - 1}")


if __name__ == "__main__":
    append_extension_j()

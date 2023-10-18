import os

def generate_file(file_path, target_size_kb):
    # Initialize sentence counter and file size
    sentence_num = 1
    current_size_kb = 0

    # Calculate the target size in bytes
    target_size_bytes = target_size_kb * 1024

    # Open the file for writing
    with open(file_path, 'w') as file:
        # Keep writing sentences to the file until we reach or slightly exceed the target size
        while current_size_kb < target_size_bytes:
            # Write a sentence to the file
            sentence = f"sentence {sentence_num}\n"
            file.write(sentence)

            # Check the current size of the file
            current_size_kb = file.tell()  # Get the current position in the file, which is the size in bytes

            # Increment the sentence number for the next sentence
            sentence_num += 1

    print(f"Finished writing. The file reached approximately {current_size_kb / 1024:.2f} KB")

# Path to save the file (can be modified as needed)
file_path = 'sentences.txt'

# Target size in KB
target_size_kb = 4

# Generate the file
generate_file(file_path, target_size_kb)

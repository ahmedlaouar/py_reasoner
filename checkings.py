def find_duplicate_lines(file_path):
    try:
        # Open the file in read mode
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Remove leading and trailing whitespaces from each line
        cleaned_lines = [line.strip() for line in lines]

        # Create a set to store unique lines and a list for duplicate lines
        unique_lines = set()
        duplicate_lines = []

        # Iterate through each line and check for duplicates
        for line in cleaned_lines:
            if line in unique_lines:
                duplicate_lines.append(line)
            else:
                unique_lines.add(line)

        return duplicate_lines

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Example usage:
file_path = 'src/temp/temp_query.txt'
duplicates = find_duplicate_lines(file_path)

if duplicates:
    print("Duplicate lines found:")
    for line in duplicates:
        print(line)
else:
    print("No duplicate lines found.")

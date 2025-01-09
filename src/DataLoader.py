import csv

# from chatgpt
def read_csv_as_pairs(file_path):
    """
    Reads a two-column CSV file and returns a list of pairs.

    Parameters:
        file_path (str): Path to the CSV file.

    Returns:
        list[tuple]: A list of tuples, where each tuple represents a pair of values from the CSV.
    """
    pairs = []
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 2:  # Ensure the row has exactly two columns
                    pairs.append((row[0], row[1]))
                else:
                    raise ValueError(f"Row has an unexpected number of columns: {row}")
        return pairs
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        exit(1)
    except Exception as e:
        print(f"CSVReader: An error occurred: {e}")
        exit(1)

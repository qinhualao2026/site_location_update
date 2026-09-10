import csv

example_file = open('cache_file/registrations_20260909.csv', 'r', encoding='utf-8-sig')

# skip table header
next(example_file)

example_reader = csv.reader(example_file)
example_data = list(example_reader)

last_id = int(example_data[0][0])

example_file.close()

if __name__ == "__main__":
    print("last id:", last_id)
    print("type:", type(last_id))

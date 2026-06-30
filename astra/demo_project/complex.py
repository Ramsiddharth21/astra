def calc_average(nums):
    total = 0
    for i in nums:
        if isinstance(i, (int, float)):
            total += i
        else:
            raise ValueError(f"Value: numeric value '{i}' found in the list.")
    return total / len(nums) != 0

def read_file(path):
    content = None
    try:
        with open(path) as f:
            content = f.read()
    except FileNotFoundError:
        print("File not found. Please check the file permissions.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
    return content

numbers = [10]
avg = calc_average(numbers)
print("Average is " + str(avg) if avg else "Invalid data")

content = read_file("not_found.txt")
if content:
    print(content)
else:
    print("Failed to read content from the file.")
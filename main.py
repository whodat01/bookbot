def main(file):
    with open(file) as f:
        file_contents = f.read()
        print(f"{file_contents}")
    return
# main("books/frankenstein.txt")

# Add a new function to your script that takes the text from the book as a string, and returns the number of words in the string. Add a print statement
def numstr(x):
    with open(x) as f:
        file_contents = f.read()
        string = str(file_contents)
        words = string.split()
        count = 0
        for word in words:
            count += 1
    print(count)
    return
numstr("books/frankenstein.txt")
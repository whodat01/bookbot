def main():
    book_path = "books/frankenstein.txt"
    with open(book_path) as a:
        text = a.read()
    print(text)
main()
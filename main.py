def main():
    book_path = "books/frankenstein.txt"
    text = get_book_text(book_path)
    num_words = get_num_words(text)
    char_count = get_num_chars(text)
    sorted_chars = sort_char_count(char_count)

    print("--- Begin report of books/frankenstein.txt ---")
    print(f"{num_words} words found in the document\n")

    for char_dict in sorted_chars:
        print(f"The '{char_dict['char']}' character was found {char_dict['num']} times")
    
    print("--- End report ---")

def get_book_text(book_path):
    with open(book_path) as f:
        return f.read()
    
def get_num_words(text):
    words = text.split()
    return len(words)

def get_num_chars(text):
    lowered_text = text.lower()
    char_count = {}
    for char in lowered_text:
            if char.isalpha():
                if char in char_count:
                    char_count[char] += 1
                else:
                    char_count[char] = 1
    return char_count

def sort_on(char_count):
    return char_count["num"]

def sort_char_count(char_count):
    char_list = [{'char':ch,'num':count} for ch, count in char_count.items()]
    char_list.sort(reverse=True, key=sort_on)
    return char_list
if __name__ == "__main__":
    main()

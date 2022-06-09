

def replace_chars(text, new_char=""):
    for characters in ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '>', '<', '#', '+', '-', '!', '$', '\'', '@',
                       '€', '&', '%']:
        if characters in text:
            text = text.replace(characters, new_char)
    return text

# -*- coding: utf-8 -*-
"""A script to fix RTL .srt files punctuation."""

signs = ['.', ',', '-', '?', '!', '\"', '(', ')', '\'', ';', ':', '<', '>']
LEFT_BRACKET = '('
RIGHT_BRACKET = ')'
TAG_OPENER = '<i>'
TAG_CLOSER = '</i>'
SPACE = ' '
# NUMBER_FIXER = u"\u200F"
NUMBER_FIXER = u"‏"

argv = ["convert.py",
        "E:\\Programming\\Python\\trunk\\SubConverter\\demo.txt",
        "E:\\Programming\\Python\\trunk\\SubConverter\\new.txt"]


def is_digit(ch):
    return '0' <= ch <= '9'


def is_content_char(ch):
    return not ch in signs


def is_strict_content_char(ch):
    return not (ch in signs or ch == SPACE or is_digit(ch))


def is_content_line(s_line):
    return any([is_strict_content_char(ch) for ch in s_line])


def process_line(s_line):
    """ Receives: a translated line string,
    Returns: the converted line """

    """
    Extracting header, footer and content.
    """

    # getting header
    header = ""
    is_head_tagged = False
    header_index = 0
    if s_line[:3] == TAG_OPENER:
        is_head_tagged = True
        s_line = s_line[3:]

    while (not is_strict_content_char(s_line[header_index])
           and header_index < len(s_line)):
        header += s_line[header_index]
        header_index += 1

    # getting footer
    footer = ""
    is_foot_tagged = False
    footer_index = len(s_line) - 1
    if s_line[len(s_line) - len(TAG_CLOSER):] == TAG_CLOSER:
        is_foot_tagged = True
        s_line = s_line[:len(s_line) - len(TAG_CLOSER)]
        footer_index -= len(TAG_CLOSER)

    while (not is_content_char(s_line[footer_index])
           and footer_index > 0):
        footer = s_line[footer_index] + footer
        footer_index -= 1

    # extracting content
    footer_index += 1
    content = s_line[header_index:footer_index]

    # possible appearance order (header):
    # 1. tag - remains in tact in header ######### check if reversal within header is needed
    # 2. any sign (but number) - copy in reversed order to end of line (LIFO)
    # 3. number - add NUMBER_FIXER if first sign (also, check for multiple digit numbers)
    ###
    # possible appearance order (footer):
    # 1. tag - remains in tact in header ######### check if reversal within footer is needed
    # 2. any sign - copy in reversed order to end of line (LIFO), if number check for multiple digits

    f_header = ""
    f_footer = ""
    first_char = True
    first_num = None
    any_num = None

    for n_char in header:
        ch = n_char

        ch = RIGHT_BRACKET if ch == LEFT_BRACKET else \
            LEFT_BRACKET if ch == RIGHT_BRACKET else ch

        if (first_char or first_num is not None) and is_digit(ch):
            first_num = (ch if (first_num is None) else first_num + ch)
            first_char = False
        elif first_num is not None:
            f_footer += NUMBER_FIXER + first_num
        elif is_digit(ch):
            any_num = (ch if (any_num is None) else any_num + ch)
        else:
            if any_num is not None:
                f_footer = any_num + f_footer
                any_num = None
            f_footer = ch + f_footer

    if any_num is not None:
        f_footer = any_num + f_footer
        any_num = None

    for n_char in footer:
        ch = n_char

        ch = RIGHT_BRACKET if ch == LEFT_BRACKET else \
            LEFT_BRACKET if ch == RIGHT_BRACKET else ch

        f_header = ch + f_header

    if is_head_tagged:
        f_header = TAG_OPENER + f_header
    if is_foot_tagged:
        f_footer += TAG_CLOSER

    new_line = f_header + content + f_footer.encode("UTF-8")
    # new_line = f_header + content + f_footer
    return new_line


new_file_content = ""
i = 0

src_file = open(argv[1], 'r')
for n_line in src_file.readlines():
    stripped_line = n_line[:-1]
    new_file_content += n_line[:-1] + "\r\n" if not is_content_line(stripped_line) \
        else process_line(stripped_line) + "\r\n"
src_file.close()

new_file = file(argv[2], 'wb')
new_file.flush()
new_file.write(new_file_content)
new_file.close()

# 1. LIFO end of line to beginning of line for: signs, english
# 2. LIFO beginning of line to end of line for: signs, english, numbers
# 3. attributes stay in place
# 4. remove unwanted spaces after dash in beginning of line
# 5. brackets have to be replaced to other side brackets and 1 or 2

'''
Console-Based Text Editor

Name: Celine Clarissa Chandra

Background

I am a freshman data science student building foundational programming skills
through hands-on projects. This editor was developed as an assignment of a course
in university to reinforce key concepts in string handling, user input
parsing, and command execution flow—all within a non-object-oriented,
procedural programming approach.


Problem Statement

Build and design a simple but powerful multi-line editor requires
handling many aspects of user interaction, including cursor movement,
character-wise editing, command parsing, and maintaining edit history.
The goal of this assignment is to simulate a real text editing environment
in the command line, complete with helpful features like undo and command
repetition, using only fundamental Python programming techniques.
'''

# import library
import re

# initialize global variables
text = ''
row_curs_on = False
line_curs_on = False
row_curs_pos = 0      # index of character in a row
line_curs_pos = 0     # index of line
copied = ''
history = [('', text, row_curs_pos, row_curs_on,
            line_curs_pos, line_curs_on, copied)]
help_message = '''? - display this help info
. - toggle row curs on and off
; - toggle line curs on and off
h - move curs left
j - move curs up
k - move curs down
l - move curs right
^ - move curs to beginning of the line
$ - move curs to end of the line
w - move curs to beginning of next word
b - move curs to beginning of previous word
i - insert <text> before curs
a - append <text> after curs
x - delete character at curs
dw - delete word and trailing spaces at curs
yy - copy current line to memory
p - paste copied line(s) below line curs
P - paste copied line(s) above line curs
dd - delete line
o - insert empty line below
O - insert empty line above
u - undo previous command
r - repeat last command
s - show content
q - quit program'''

# helper functions
def count_space_after(content:str, row_curs_pos:int) -> int:
    '''
    Counts spaces after row cursor.

    Args:
        content (str)       : The text.
        row_curs_pos (int)  : The index of the row cursor.
    '''
    match = re.match(r'\s+', content[row_curs_pos:])
    if not match:
        return 0
    whitespace = match.group()
    # print(content, row_curs_pos, content[row_curs_pos:])
    if re.match(r'\s+\w', content[row_curs_pos:]):    # followed by a word
        return len(whitespace)
    return len(whitespace)      # trailing whitespace at the end

def count_space_before(content:str, row_curs_pos:int) -> int:
    '''
    Counts spaces before row cursor.

    Args:
        content (str)       : The text.
        row_curs_pos (int)  : The index of the row cursor.
    '''
    count = 2
    if content[row_curs_pos].isspace():    # if the cursor is at a space
        i = row_curs_pos - 1 
    else:
        i = row_curs_pos-2
    while i >= 0 and content[i].isspace():
        count += 1
        i -= 1
    return count

def run(user_input:str):
    '''
    Executes another function according to the user's input.
    If the user's input is out of the scope of the options, this function will do nothing.
    Exits the program if the user inputs a certain character.

    Args:
        user_input (str)    : The input of the user.
    '''
    options = {'?': lambda: print(help_message),
               '.': lambda: toggle_curs('row'),
               ';': lambda: toggle_curs('line'),
               'h': lambda: move_row_curs(-1),
               'j': lambda: move_line_curs(-1, 'move'),
               'k': lambda: move_line_curs(1, 'move'),
               'l': lambda: move_row_curs(1),
               '^': lambda: move_row_curs(-row_curs_pos-1),
               '$': lambda: move_row_curs(len(text)-row_curs_pos),
               'w': move_next_word,
               'b': move_prev_word,
               'i': lambda: manipulate_text(row_curs_pos, row_curs_pos, 0, user_input[1:]),
               'a': lambda: manipulate_text(row_curs_pos+1, row_curs_pos+1, len(text+user_input[1:])-1, user_input[1:]),
               'x': lambda: manipulate_text(row_curs_pos, row_curs_pos+1, -1 if row_curs_pos > len(text) else 0),
               'dw': delete_word,
               'yy': lambda: copy(text),
               'p': lambda: paste(1, copied),
               'P': lambda: paste(-1, copied),
               'dd': delete_line,
               'o': lambda: insert_new_line(1),
               'O': lambda: insert_new_line(-1),
               'u': undo_prev,
               'r': repeat_last_command,
               's': lambda: print(text)}
    # execute command
    if user_input == 'q':
        exit()
    else:
        if user_input in ['', 'i', 'a'] or (user_input == 'r' and len(history) == 1):
            pass
        elif (user_input[0] in ['i', 'a']) or (user_input in options):
            command = user_input[0] if user_input[0] in ['i', 'a'] else user_input
            options[command]()
            if user_input not in ['?', 'u', 's']:
                history.append((user_input, text, row_curs_pos, row_curs_on,
                                line_curs_pos, line_curs_on, copied))
                # show text
                if (user_input == '.' and text == '*') or (user_input=='dd') or (user_input==';' and text=='*' and history[-2][0] in ['.', '']):
                    pass
                elif user_input == '.':
                    if text:
                        print(text)
                else:
                    print(text)
        main()

# cursor display functions
def turn_off_row_curs(content: str) -> str:
    '''
    Returns an updated version of content with the row cursor disabled for display.

    Args:
        content (str)   : The original content with its row cursor turned on.
    '''
    translation = {'\033[42m':'', '\033[0m':''}
    regex = re.compile('|'.join(map(re.escape, translation)))
    return regex.sub(lambda match: translation[match.group(0)], content)

def turn_on_row_curs(content:str) -> str:
    '''
    Returns an updated version of content with the row cursor enabled for display.

    Args:
        content (str)   : The original content with its row cursor turned off.
    '''
    global row_curs_pos, line_curs_pos

    lines = content.split('\n')
    current_line = lines[line_curs_pos]

    if row_curs_pos < len(current_line) and ((not line_curs_on and text) or (line_curs_on and text!='*')):
        lines[line_curs_pos] = current_line[:row_curs_pos]+'\033[42m'+current_line[row_curs_pos]+'\033[0m'+current_line[row_curs_pos+1:]
        return '\n'.join(lines)
    else:
        if row_curs_pos > 0 and current_line != '*':
            row_curs_pos -= 1
            lines[line_curs_pos] = current_line[:row_curs_pos]+'\033[42m'+current_line[row_curs_pos]+'\033[0m'+current_line[row_curs_pos+1:]
            return '\n'.join(lines)
        return '\n'.join(lines)

def turn_off_line_curs(content:str) -> str:
    '''
    Returns an updated version of content with the line cursor disabled for display.

    Args:
        content (str)   : The original content with its line cursor turned on.
    '''
    global row_curs_pos

    row_curs_pos -= 1
    lines = content.split('\n')
    for i in range(len(lines)):
        lines[i] = lines[i][1:]
    return '\n'.join(lines)

def turn_on_line_curs(content:str) -> str:
    '''
    Returns an updated version of content with the line cursor enabled for display.

    Args:
        content (str)       : The original content with its line cursor turned off.
    '''
    global row_curs_pos, line_curs_pos

    row_curs_pos += 1
    lines = content.split('\n')
    for i in range(len(lines)):
        if i == line_curs_pos:
            lines[i] = '*' + lines[i]
        else:
            lines[i] = ' ' + lines[i]
    return '\n'.join(lines)

def turn_off_all_curs(content:str) -> str:
    '''
    Returns an updated version of content with both cursors disabled for display.

    Args:
        content (str)   : The original content.
    '''
    global line_curs_on, row_curs_on

    content = turn_off_line_curs(content) if line_curs_on else content
    content = turn_off_row_curs(content) if row_curs_on else content
    return content

def turn_on_all_curs(content:str) -> str:
    '''
    Returns an updated version of content with both cursors enabled for display.

    Args:
        content (str)   : The original content.
    '''
    global line_curs_on, row_curs_on, line_curs_pos, row_curs_pos

    content = turn_on_line_curs(content) if line_curs_on else content
    current_line = content.split('\n')[line_curs_pos]
    if row_curs_on and row_curs_pos<=len(current_line):
        content = turn_on_row_curs(content) if row_curs_on else content
    return content

def toggle_curs(mode:str) -> None:
    '''
    Toggles the cursor display on or off according to the mode.
    If the cursor is currently enabled, it is removed. Otherwise, it is added.

    Args:
        mode (str): Indicates which cursor (line or row).
    '''
    global text, line_curs_on, row_curs_on, line_curs_pos

    toggles = { 'line': {'on': turn_on_line_curs,
                        'off': turn_off_line_curs,
                        'state': line_curs_on},
                'row': {'on': turn_on_row_curs,
                        'off': turn_off_row_curs,
                        'state': row_curs_on}}
    if toggles[mode]['state']:
        text = toggles[mode]['off'](text)
    else:
        text = toggles[mode]['on'](text)
    # flip global flag
    if mode == 'line':
        line_curs_on = not line_curs_on
    else:
        row_curs_on = not row_curs_on

# cursor movement functions
def move_row_curs(delta:int) -> None:
    '''
    Moves the row cursor by the specified delta.
    Initiates user to enter another input if the text is empty.

    Args:
        delta (int) : The number of positions to move the row cursor (positive: right, negative: left).
    '''
    global text, row_curs_pos, row_curs_on, line_curs_on, line_curs_pos
    if text != '':
        text = turn_off_row_curs(text) if row_curs_on else text
        current_line = text.split('\n')[line_curs_pos]
        row_curs_pos = max(1, min(len(current_line)-1, row_curs_pos+delta)) if line_curs_on else max(0, min(len(current_line)-1, row_curs_pos+delta))
        text = turn_on_row_curs(text) if row_curs_on else text

def move_line_curs(delta:int, usage:str='') -> None:
    '''
    Moves the line cursor by the specified delta.

    Args:
        delta (int) : The number of positions to move the line cursor (positive: downwards, negative: upwards).
        usage (str) : The usage of this function.
    '''
    global text, line_curs_pos, line_curs_on, row_curs_pos, row_curs_on

    text = turn_off_all_curs(text)
    line_curs_pos = max(0, line_curs_pos+delta)
    current_line = text.split('\n')[line_curs_pos]

    if line_curs_on:
        row_curs_pos = min(row_curs_pos+1, len(current_line)) if row_curs_pos>len(current_line) else row_curs_pos
    else:
        row_curs_pos = min(row_curs_pos, len(current_line)) if row_curs_pos>len(current_line) else row_curs_pos

    if current_line:
        text = turn_on_row_curs(text) if row_curs_on else text
    text = turn_on_line_curs(text) if line_curs_on else text

def move_prev_word() -> None:
    '''
    Moves the row cursor to the beginning of the previous word (word to the left of the current word).
    If no word exists in that direction, the cursor remains stationary.
    '''
    global text, row_curs_pos

    text = turn_off_row_curs(text)
    lines = text.split('\n')
    current_line = lines[line_curs_pos]
    indices = sorted([match.start() for match in re.finditer(r"\s", current_line)]+[0, len(current_line)])    # indices containing spaces in str and endpoints

    for i in range(1, len(indices) - 1):
        at_word_start = indices[i] - row_curs_pos == -1
        if at_word_start and indices[i - 1] == 0:   # cursor is just before a word at the beginning of the line
            move_row_curs(-row_curs_pos)
            break
        elif at_word_start:     # cursor is at the beginning of a word, but not the first word
            if row_curs_pos <= len(current_line) and current_line[row_curs_pos] == ' ':     # cursor is at a space: backtrack past whitespace
                n = count_space_before(current_line, row_curs_pos)
                move_row_curs(-n)
                for j in range(1, len(indices) - 1):
                    if indices[j] < row_curs_pos <= indices[j + 1]:
                        move_row_curs(indices[j] - row_curs_pos + 1)
                        break
                break
            elif current_line[row_curs_pos - 1] == current_line[row_curs_pos - 2] == ' ':   # cursor is at beginning of a word with preceding whitespace
                n = count_space_before(current_line, row_curs_pos)
                for j in range(len(indices) - 2, -1, -1):
                    if indices[j] < row_curs_pos - n:
                        move_row_curs(-row_curs_pos if indices[j] == 0 else indices[j] - row_curs_pos + 1)
                        break
                break
            else:   # default: move to previous word
                move_row_curs(indices[i - 1] - row_curs_pos + 1)
                break
        elif indices[i] < row_curs_pos <= indices[i + 1]:   # cursor is within a word, move to start of current or previous word
            move_row_curs(indices[i] - row_curs_pos + 1)
            break
    if indices[0] < row_curs_pos < indices[1]:  # cursor in first word but not at start
        move_row_curs(-row_curs_pos)

def move_next_word() -> None:
    '''
    Moves the row cursor to the beginning of the next word (word to the right of the current word).
    If no word exists in that direction, the row cursor remains stationary.
    '''
    global text, row_curs_pos, line_curs_pos

    text = turn_off_row_curs(text)
    lines = text.split('\n')
    current_line = lines[line_curs_pos]
    indices = sorted([match.start() for match in re.finditer(r"\s", current_line)]+[0, len(current_line)])    # indices containing spaces in str and endpoints
    n = 1

    if indices[-2] < row_curs_pos <= indices[-1]: # for words located at the end of the sentence
        move_row_curs(0)
    else:
        for i in range(1, len(indices)-1):
            if indices[i] == row_curs_pos:    # if cursor is at a space
                n = count_space_after(current_line, row_curs_pos)+1
                if n > 1:   # if the space is followed by an(other) space(s)
                    move_row_curs(n)
                move_row_curs(1)
                break
            elif indices[i] > row_curs_pos:   # if cursor is at a word
                n = count_space_after(current_line, indices[i])
                move_row_curs(indices[i]-row_curs_pos+n)
                break

# text manipulation functions
def manipulate_text(begin:int, end:int, delta:int, inserted_text='') -> None:
    '''
    Modifies the text by replacing the content between "begin" and "end" with "inserted_text".
    Moves the cursor according to the delta.

    Args:
        begin (int), end(int)   : The index where the text manipulation starts and ends.
        delta (int)             : The distance where the row cursor needs to be moved after manipulating text.
        inserted_text (str)     : The text that is going to be inserted between "begin" and "end" (default: '').
    '''
    global text, row_curs_pos, line_curs_pos, line_curs_on, history
    text = turn_off_all_curs(text)

    # manipulate text
    lines = text.split('\n')
    lines[line_curs_pos] = lines[line_curs_pos][:begin] + inserted_text + lines[line_curs_pos][end:]
    text = '\n'.join(lines)

    text = turn_on_all_curs(text)

    # move cursor
    if row_curs_pos == len(lines[line_curs_pos]):
        move_row_curs(-1)
    else:
        if history[-1][0] in ['o', 'O'] and delta == 0:
            delta = 1-row_curs_pos if line_curs_on else -row_curs_pos
        move_row_curs(delta)

def delete_word() -> None:
    '''
    Deletes a word at or after the cursor position.
    Moves the cursor to the start of the next word.
    '''
    global text, row_curs_pos, line_curs_pos

    text = turn_off_row_curs(text)
    lines = text.split('\n')
    current_line = lines[line_curs_pos]
    begin = end = row_curs_pos
    # identify indices with spaces + endpoints
    indices = sorted([match.start() for match in re.finditer(r"\s", current_line)]+[len(current_line)])
    if indices[0] != 0:
        indices = [0]+indices

    # determine begin and end indices to slice text
    for i in range(len(indices)-1):
        if indices[i] <= row_curs_pos <= indices[i+1]:    # if the cursor is in the middle to end of a word
            n = count_space_after(current_line, row_curs_pos)
            begin, end = row_curs_pos, indices[i+1]+1+n
            if len(current_line) < end:     # if the cursor is at the last word
                end = len(current_line)
            break

    if row_curs_pos < len(current_line) and current_line[row_curs_pos] == ' ':  # if the cursor is at a space
        n = count_space_after(current_line, row_curs_pos)
        begin, end = row_curs_pos, row_curs_pos+n

    for i in range(len(indices)-1):
        try:
            if (row_curs_pos == 0) and (end+1 == indices[i]):     # if the cursor is at the start and is at a word
                begin = row_curs_pos
                end = indices[i]+1 if len(indices) > 1 else len(current_line)
        except:
            pass

    # slice text
    lines[line_curs_pos] = (current_line[:begin]+current_line[end:])
    text = '\n'.join(lines)

    # move cursor
    for i in indices:
        if begin == 0:  # for words located at the beginnig
            move_row_curs(-row_curs_pos)
            break
        elif i == row_curs_pos:   # if cursor is at a space
            move_row_curs(0)
            break
        elif end <= i:    # for words located in the middle of the sentence
            move_row_curs(begin-row_curs_pos)
            break

def copy(content:str) -> None:
    '''
    Copy the current line.
    Do nothing if the editor's content is empty.
    '''
    global line_curs_pos, copied

    content = turn_off_all_curs(content)
    lines = content.split('\n')
    if lines[line_curs_pos]:
        copied = lines[line_curs_pos]

def paste(delta:int, copied:str) -> None:
    '''
    Pastes the copied line by the specified delta.

    Args:
        delta (int) : The position to paste the copied line.
                      (1: below the current line, -1: above the current line).
        copied (str): The copied text.
    '''
    global text, line_curs_on, row_curs_pos
    row_cur_pos = row_curs_pos-1 if line_curs_on else row_curs_pos
    insert_new_line(delta, 'paste')
    text = turn_off_line_curs(text) if line_curs_on else text
    lines = text.split('\n')
    lines[line_curs_pos] = copied
    text = '\n'.join(lines)
    row_curs_pos = row_cur_pos
    text = turn_on_all_curs(text)

def delete_line() -> None:
    '''
    Delete the current line.
    Adjust the line and row cursors accordingly.

    Args:
        line_curs_pos (int) : The index of the line cursor.
    '''
    global text, line_curs_pos

    lines = text.split('\n')
    n = len(lines)
    del lines[line_curs_pos]
    text = '\n'.join(lines)
    if line_curs_pos+1 > len(lines):
        move_line_curs(-1)
    else:
        move_line_curs(0)

    if n > 1:
        print(text)

def insert_new_line(delta:int, usage:str='') -> None:
    '''
    Inserts a new line by the specified delta.

    Args:
        delta (int)     : The position to insert the new line.
                          (1: below the current line, -1: above the current line).
        usage (str)     : What this function is used for.
    '''
    global text, line_curs_on, history

    text = turn_off_line_curs(text) if line_curs_on else text
    lines = text.split('\n')
    
    for i in range(len(lines)):
        if text=='' and usage != 'paste' and history[-1][0] not in ['o', 'O']:
            delta = 0
        elif (len(lines) == 1 or i == line_curs_pos) and delta == 1:
            lines[i] = lines[i]+'\n'
        elif i == line_curs_pos and delta == -1:
            lines[i] = '\n'+lines[i]
            delta = 0
    
    text = '\n'.join(lines)
    text = turn_on_line_curs(text) if line_curs_on else text
    move_line_curs(delta)

# history functions
def undo_prev() -> None:
    '''
    Undoes the previous command by restoring the last text state.
    If there is no command prior, users will be directed to insert a new input.
    '''
    global text, history, row_curs_pos, row_curs_on, line_curs_pos, line_curs_on, copied

    if len(history) > 1:
        history.pop()
        text, row_curs_pos, row_curs_on, line_curs_pos, line_curs_on, copied = history[-1][1], history[-1][2], history[-1][3], history[-1][4], history[-1][5], history[-1][6]
        if (line_curs_on and text != '*') or (not line_curs_on and text):
            print(text)
    else:
        main()

def repeat_last_command() -> None:
    '''
    Repeats the last executed command.
    '''
    last_command = history[-2][0] if (history and history[-1][0] in ['?', 'u', 'r']) else history[-1][0]
    if (last_command[0] in ['i', 'a']) or (last_command in ['.', 'h', 'l', '^', '$', 'w', 'b', 'x', 'dw', 's']):
        run(last_command)

# run program
def main():
    '''
    Keeps the program running:
    Initiates user to input a string of characters, and run another function according to the input.
    '''
    run(input('>'))

if __name__ == '__main__':
    main()
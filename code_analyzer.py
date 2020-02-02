from tkinter import *  # Первым делом импортируем tkinter
import os


def write_in_bufer(text):
    root.clipboard_clear()
    root.clipboard_append(text)

def open_button(text):
    l = Label(text='[Open file]', **bdict)
    l.bind('<Button-1>',lambda x:os.system(f'"C:\Windows\explorer.exe" {text}'))
    return l

def copy_button(btext ,text):
    l = Label(text=f'[{btext}]', **bdict)
    l.bind('<Button-1>', lambda x:write_in_bufer(text))
    return l

def smth_in(target, *args):
    for arg in args:
        if arg in target:
            return True
    return False

def find_string_gen(search_text):
    for path in files_list:
        print(f'Analyzing {path}...')
        with open(path, encoding='utf-8') as f:
            string = 0
            for line in f:
                string += 1
                if not search_text in line:
                    continue
                text.insert(END, f'File: {path[abspath_len:]}\nLine: {string} ')
                text.window_create(END, window=copy_button('Copy line', line[:-1]))
                text.window_create(END, window=open_button(path))
                text.insert(END, f'\n{line}\n')
                yield

sg = range(0)

def start_search(event=None):
    global sg
    sg = find_string_gen(entry.get())
    continue_search()

def continue_search(event=None, count=50):
    global sg
    text.delete(1.0, END)
    for i in range(count):
        try:
            next(sg)
        except StopIteration:
            label['text'] = f'{i} new items are found'
            break
    else:
        label['text'] = f'{count} new items are found'

def full_search(event=None):
    global sg
    sg = find_string_gen(entry.get())
    text.delete(1.0, END)
    label['text'] = f'{len(tuple(sg))} items are found'


files_list = []
path = os.path.abspath('code_analyzer.py')[:-len('code_analyzer.py')]
abspath_len = len(path)
print(path)
tree = os.walk(path)

for branch in tree:
    if not smth_in(branch[0], '.git', '.idea', '__pycache__'):
        for path in branch[2]:
            if path[-3:] == '.py':
                files_list.append(os.path.join(branch[0], path))

fg = '#ffddbf'
vdict = {'bg': '#002240', 'fg': fg, 'font': 'Consolas 11'}
bdict = {'bg': '#002240', 'fg': '#b1ffeb', 'font': 'Consolas 11'}

root = Tk()
root.configure(bg='')
root.title('Code analyzer')

entry = Entry(root, **vdict, insertbackground=fg, justify="center")

frame = Frame(root)
button1 = Button(frame, text='Find', command=start_search, **vdict)
button2 = Button(frame, text='Find more', command=continue_search, **vdict)
button3 = Button(frame, text='Find all', command=full_search, **vdict)

label = Label(root, **vdict)
text = Text(wrap=WORD, **vdict, insertbackground=fg)
scrollbar = Scrollbar(command=text.yview)

entry.bind('<Return>', full_search)

entry.pack(fill=X)

button3.pack(side=RIGHT)
button2.pack(side=RIGHT)
button1.pack(fill=X)
frame.pack(fill=X)

label.pack(fill=X)
text.pack(side=LEFT, fill=BOTH, expand=1)
scrollbar.pack(side=RIGHT, fill=Y)

text['yscrollcommand'] = scrollbar.set

root.mainloop()

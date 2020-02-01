from tkinter import *  # Первым делом импортируем tkinter
import os


def write_in_bufer(text):
    root.clipboard_clear()
    root.clipboard_append(text)


def open_button(text):
    func = lambda:os.system(f'"C:\Windows\explorer.exe" {text}')
    return Button(text='Open', command=func, bg='#503872', fg=fg)

def copy_button(btext ,text):
    func = lambda:write_in_bufer(text)
    return Button(text=btext, command=func, bg='#503872', fg=fg)

def show_path_button(text):
    def func(e):
        if e.widget['text'] == 'Show path':
            e.widget['text'] = text
        else:
            e.widget['text'] = 'Show path'
    b = Button(text='Show path', bg='#503872', fg=fg)
    b.bind('<Button-1>', func)
    return b


def smth_in(target, *args):
    for arg in args:
        if arg in target:
            return True
    return False


def analyze(event=None):
    search = entry.get()
    text.delete(1.0, END)
    counter = 0
    for FILE in files_list:
        print(f'Analyzing {FILE}')
        f = open(FILE, encoding='utf-8')
        string = 1
        for line in f:
            if not search in line:
                continue
            counter += 1

            text.insert(END, f'File: {FILE[abspath_len:]} ')
            text.window_create(END, window=show_path_button(FILE))
            text.window_create(END, window=open_button(FILE))
            text.insert(END, f'\nLine: {string} ')
            text.window_create(END, window=copy_button('Copy line', line))
            text.insert(END, f'\n{line}\n')
            string += 1
        f.close()
    label['text'] = f"{counter} items are found"


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

bg = '#002240'
fg = '#eeeeee'
font = 'Consolas 11'

root = Tk()
root.configure(bg='')
root.title('Code analyzer')

entry = Entry(root, bg=bg, fg=fg, insertbackground=fg, justify="center", font=font)
button = Button(root, text='Анализировать', command=analyze, bg=bg, fg=fg, font=font)
label = Label(root, bg=bg, fg=fg, font=font)
text = Text(wrap=WORD, bg=bg, fg=fg, insertbackground=fg, font=font)
scrollbar = Scrollbar(command=text.yview, bg=bg, troughcolor=fg)

entry.bind('<Return>', analyze)

entry.pack(fill=X)
button.pack(fill=X)
label.pack(fill=X)
text.pack(side=LEFT, fill=BOTH, expand=1)
scrollbar.pack(side=RIGHT, fill=Y)

text['yscrollcommand'] = scrollbar.set

root.mainloop()

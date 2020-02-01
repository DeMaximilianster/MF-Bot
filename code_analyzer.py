from tkinter import *  # Первым делом импортируем tkinter
import os


def write_in_bufer(text):
    root.clipboard_clear()
    root.clipboard_append(text)


def copy_button(text):
    func = lambda:os.system(f'"C:\Windows\explorer.exe" {text}')
    return Button(text='Open', command=func, bg='#503872', fg=fg)


def smth_in(target, *args):
    for arg in args:
        if arg in target:
            return True
    return False


def analyze(event=None):
    print(event)
    search = entry.get()
    text.delete(1.0, END)
    counter = 0
    for FILE in files_list:
        print(f'Analyzing {FILE}')
        with open(FILE, encoding='utf-8') as f:
            string = 1
            for line in f:
                if search in line:
                    counter += 1
                    text.insert(END, 'File: {} '.format(FILE))
                    text.window_create(END, window=copy_button(FILE))
                    text.insert(END, '\nСтрока: {}\n'.format(string))
                    try:
                        text.insert(END, line + '\n')
                    except Exception as e:
                        print(repr(e))
                        text.insert(END, 'This line is not available')
                string += 1
    label['text'] = "{} items are found".format(counter)


files_list = []
path = os.path.abspath('code_analyzer.py')[:-len('code_analyzer.py')]
print(path)
tree = os.walk(path)

for branch in tree:
    if not smth_in(branch[0], '.git', '.idea', '__pycache__'):
        print(branch)
        for path in branch[2]:
            if path[-3:] == '.py':
                files_list.append(os.path.join(branch[0], path))

print(*files_list, sep='\n')

bg = '#002240'
fg = '#eeeeee'
font = 'Consolas 11'

root = Tk()
root.configure(bg='')

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

from tkinter import *  # Первым делом импортируем tkinter
import os


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
                    text.insert(END, 'File: {}\n'.format(FILE))
                    text.insert(END, 'Строка: {}\n'.format(string))
                    try:
                        text.insert(END, line + '\n')
                    except Exception as e:
                        print(e)
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
        for file in branch[2]:
            if file[-3:] == '.py':
                files_list.append(branch[0] + '\\' + file)

print(files_list)

root = Tk()

entry = Entry(root)
button = Button(root, text='Анализировать', command=analyze)
label = Label(root)
frame = Frame()
text = Text(frame, wrap=WORD)
scrollbar = Scrollbar(frame, command=text.yview)

entry.bind('<Return>', analyze)

entry.pack()
button.pack()
label.pack()
frame.pack()
text.pack(side=LEFT)
scrollbar.pack(side=RIGHT, fill=Y)

text['yscrollcommand'] = scrollbar.set

root.mainloop()

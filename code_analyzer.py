from tkinter import *  # Первым делом импортируем tkinter
import os

def smth_in(target, *args):
    for arg in args:
        if arg in target:
            return True
    return False

def analyze(event=None):
    search = entry.get()
    text.delete(1.0, END)
    for file in files_list:
        print('Анализирую {}'.format(file))
        with open(file, encoding='utf-8') as f:
            string = 1
            for line in f:
                if search in line:
                    text.insert(END, 'Файл: {}\n'.format(file))
                    text.insert(END, 'Строка: {}\n'.format(string))
                    text.insert(END, line+'\n')
                string += 1

files_list = []
path = os.path.abspath('code_analyzer.py')[:-len('code_analyzer.py')]
print(path)
tree = os.walk(path)

for branch in tree:
    if not smth_in(branch[0], '.git', '.idea', '__pycache__'):    
        print(branch)
        for file in branch[2]:
            if file[-3:] == '.py':
                files_list.append(branch[0]+'\\'+file)

print(files_list)

root = Tk()

entry = Entry(root)
button = Button(root, text='Анализировать', command=analyze)
frame = Frame()
text = Text(frame, wrap=WORD)
scrollbar = Scrollbar(frame, command=text.yview)

entry.bind('<Return>', analyze)

entry.pack()
button.pack()
frame.pack()
text.pack(side=LEFT)
scrollbar.pack(side=RIGHT, fill=Y)



text['yscrollcommand'] = scrollbar.set

root.mainloop()

        

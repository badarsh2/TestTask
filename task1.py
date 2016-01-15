import urllib2
import json
from Tkinter import *
import os
import tkMessageBox
from os import listdir
from os.path import isfile, join
import re

value=''
root = Tk()
root.wm_title("Saarang ERP Events")
regwindow = ''
data = ''
categories=[]

def HTTPGet(URL):
	content = urllib2.urlopen(URL).read()
	return content

def search(sv):
	global value
	global data
	query = sv.get()
	listbox = Listbox()
	listbox.grid(row=2,column=0)
	for i in range (len(data)):
		# print data[i]['name']
		if(query.lower() in data[i]['name'].lower()):
			listbox.insert(END, data[i]['name'])
	listbox.bind('<<ListboxSelect>>', onselect)



w = Label(root, text="Search for event")
w.grid(row=0,column=0)
sv = StringVar()
sv.trace("w", lambda name, index, mode, sv=sv: search(sv))
e = Entry(root, textvariable=sv)
e.grid(row=1,column=0)

listbox = Listbox()
listbox.grid(row=2,column=0)

text = Text(root)
text.insert(INSERT, "Choose an event.....")
text.grid(row=2,column=1)

# progressbar = ttk.Progressbar(orient=HORIZONTAL, length=200, mode='determinate')
# progressbar.grid(row=3,column=0)
# progressbar.start()

try:
	content = HTTPGet('http://erp.saarang.org/api/mobile/display_events/')
	obj=json.loads(content)
	data = obj['data']
	for i in range (len(data)):
		# print data[i]['name']
		listbox.insert(END, data[i]['name'])
		cat = data[i]['category']
		if cat not in categories:
			categories.append(cat)

	def callback():
		global value
		global regwindow
		regwindow = Tk()
		w = Label(regwindow, text="Name:").grid(row=0,column=0)
		e = Entry(regwindow)
		e.grid(row=0,column=1)
		w2 = Label(regwindow, text="Email:").grid(row=1,column=0)
		e2 = Entry(regwindow)
		e2.grid(row=1,column=1)
		submit = Button(regwindow, text="SUBMIT", command=lambda:callbacksubmit(value, e.get(), e2.get()))
		submit.grid(row=2,columnspan=2)

	def callbacksubmit(value, name, email):
		global regwindow
		if not os.path.exists('Saarang-Reg'):
			os.makedirs('Saarang-Reg')
		if(not name or not email):
			tkMessageBox.showerror("Error","Field should be non empty ")
		else:
			filename = 'Saarang-Reg/' + value + '.txt'
			target = open(filename, 'a')
			target.write(name + '\n' + email + '\n\n')
			target.close()
			regwindow.destroy()
			tkMessageBox.showinfo("Success","Registered for " + value)
			updatemenu(value)

	b = Button(root, text="REGISTER FOR", command=callback)

	def onselect(evt):
		global value
		global b
		if(b):
			b.destroy()
		w = evt.widget
		index = int(w.curselection()[0])
		value = w.get(index)
		text.delete('1.0',END)
		for j in range (len(data)):
			if(value == data[j]['name']):
				if(b):
					b.destroy()
				text.insert(INSERT, data[j]['name'] + '\n\n')
				text.insert(INSERT, data[j]['short_description'] + '\n\n')
				long_desc = re.sub(r'<.*?>', '', data[j]['long_description'])
				text.insert(INSERT, long_desc + '\n\n')
				# print data[j]['eventtab_set'][0]['name']
				tabset = data[j]['eventtab_set']
				for k in range (len(tabset)):
					text.insert(INSERT, tabset[k]['name'] + '\n')
					text.insert(INSERT, re.sub(r'<.*?>', '', tabset[k]['content']) + '\n\n')
				b = Button(root, text="REGISTER FOR " + value, command=callback)
				b.grid(row=3,column=1)

	listbox.bind('<<ListboxSelect>>', onselect)

	if not os.path.exists('Saarang-Reg'):
		os.makedirs('Saarang-Reg')
	onlyfiles = [f for f in listdir('Saarang-Reg/') if isfile(join('Saarang-Reg/', f))]

	def textopen(label):
		filename = 'Saarang-Reg/' + label
		try:
			target = open(filename, 'r')
			content = target.read()
			filewin = Toplevel(root)
			text = Text(filewin)
			text.insert(INSERT,"REGISTRATIONS FOR " + label.split('.')[0] + "\n\n")
			text.insert(INSERT, content)
			text.pack()
		except:
			tkMessageBox.showerror('Error', 'File not found')

	def catselect(label):
		global value
		global data
		listbox = Listbox()
		listbox.grid(row=2,column=0)
		for i in range (len(data)):
			# print data[i]['name']
			if(label.lower() in data[i]['category'].lower()):
				listbox.insert(END, data[i]['name'])
		listbox.bind('<<ListboxSelect>>', onselect)


	menubar = Menu(root)

	def updatemenu(label):
		filemenu.add_command(label=label, command=lambda:textopen(label+'.txt'))


	filemenu = Menu(menubar, tearoff=0)
	for i in range(len(onlyfiles)):
		var = onlyfiles[i]
		filemenu.add_command(label=var.split('.')[0], command=lambda i=i: textopen(onlyfiles[i]))

	catmenu = Menu(menubar, tearoff=0)
	for i in range(len(categories)):
		catmenu.add_command(label=categories[i], command=lambda i=i: catselect(categories[i]))

	menubar.add_cascade(label="Categories", menu=catmenu)
	menubar.add_cascade(label="Registrations", menu=filemenu)

	root.config(menu=menubar)

	root.mainloop()

except:
	tkMessageBox.showerror("Error", "No Internet Connection")

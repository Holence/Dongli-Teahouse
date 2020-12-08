# -*- coding:utf-8 -*-  
import tkinter as tk
# from tkinter import scrolledtext
import re,os,shutil,time,calendar,string,jieba,pypinyin,random


start_watch=0
msec=0
class Watch(tk.Frame):
	def __init__(self,fontsize,color_windowbg,color_auxiliarytext,parent=None, **kw):
			tk.Frame.__init__(self, parent, kw)
			self._running = False
			self.timestr1 = tk.StringVar()
			self.timestr2 = tk.StringVar()
			self.makeWidgets(fontsize,color_windowbg,color_auxiliarytext)
			self.flag  = True
	def makeWidgets(self,fontsize,color_windowbg,color_auxiliarytext):
		l1 = tk.Label(self, textvariable = self.timestr1,bg=color_windowbg,fg=color_auxiliarytext,font=("Hack",int(fontsize*0.6)))
		l2 = tk.Label(self, textvariable = self.timestr2,bg=color_windowbg,fg=color_auxiliarytext,font=("Hack",int(fontsize*0.6)))
		l1.pack()
		l2.pack()
	def _update(self):
		self._settime()
		global start_watch,msec
		if start_watch==0:#优化计时
			msec=60*1000-time.localtime(time.time())[5]*1000
			start_watch=1
		elif start_watch==1:
			msec=60*1000
			start_watch=2;
		self.timer = self.after(msec, self._update)
	def _settime(self):
		today1 = str(time.strftime('%Y-%m-%d', time.localtime(time.time())))
		time1 = str(time.strftime('%H:%M', time.localtime(time.time())))
		self.timestr1.set(today1)
		self.timestr2.set(time1)
	def start(self):
		self._update()
		self.pack(side = tk.TOP)

class Node(object):
	def __init__(self,name,father,rank=-1):
		self.name=name
		self.father=father
		self.son=[]
		self.rank=rank

def creat_tree():
	tree_list=[]
	tree_list.append(Node("HEAD",object,-1))
	with open("文件目录.txt","r",encoding="utf-8") as f:
		rank=0
		nfore=0
		nnext=-1
		name=""
		nodefore=tree_list[-1]
		a=f.readline()
		while a!="":
			nfore=nnext
			nnext=a.count("\t")
			offset=nnext-nfore
			rank+=offset
			name=a.strip()[1:]
			if offset>0:
				for i in range(offset):
					tree_list.append(Node(name,nodefore,rank-1))
					nodefore.son.append(tree_list[-1])
					nodefore=tree_list[-1]
			elif offset==0:
				tree_list.append(Node(name,nodefore.father,rank-1))
				nodefore.father.son.append(tree_list[-1])
				nodefore=tree_list[-1]
			elif offset<0:
				offset=-offset
				for i in range(offset):
					nodefore=nodefore.father
				tree_list.append(Node(name,nodefore.father,rank-1))
				nodefore.father.son.append(tree_list[-1])
				nodefore=tree_list[-1]
			a=f.readline()
	return tree_list

def tree_toptodown(top,tree=0):#输入一个节点，返回一个排好序的从该节点到树枝末端的列表
	def deep_toptodown(node):
		nonlocal temp_list
		if node.name.strip("*").strip("\\")!="HEAD":
			temp_list.append(node)
		if node.son==[]:
			return
		for i in node.son:
			deep_toptodown(i)

	if tree==0:
		tree=tree_list
	temp_list=[]

	n=0
	for i in tree:
		if i.name=="%s"%top:
			node=i
			n+=1
	if n>1:
		log.insert(tk.END,"树中出现重复项%s\n"%top)
		log.see(tk.END)
		return
	if n==0:
		log.insert(tk.END,"树中没有%s文件夹\n"%top)
		log.see(tk.END)
		return
	deep_toptodown(node)
	return temp_list

def tree_downtotop(down):#输入若干枝干上的节点列表，返回从树顶到这些节点的最简树的排好序的列表
	cannotfind=[]
	nodelist=[]
	for i in down:#找出元树里的节点
		n=0
		for j in tree_list:
			if j.name=="%s"%i:
				nodelist.append(j)
				n+=1
		if n>1:
			log.insert(tk.END,"树中出现重复项%s\n"%i)
			log.see(tk.END)
			pass
		if n==0:
			cannotfind.append(i)
			log.insert(tk.END,"树中没有%s文件夹\n"%i)
			log.see(tk.END)
			pass

	branch=[]
	for i in nodelist:#找出元树中每个节点向上到顶的枝干
		branch.append([])
		branch[-1].append(i)
		while i.rank!=-1:
			i=i.father
			branch[-1].append(i)
		branch[-1].reverse()

	maxlen=0
	for i in branch:#求枝干的最长值
		if len(i)>maxlen:
			maxlen=len(i)

	newtree=[]
	for i in range(maxlen):#循环最长值的次数
		t=[]
		for j in branch:#把枝干中同一级的所有元素筛选出来，就是过滤掉重复的节点
			try:
				if j[i] not in t:
					t.append(j[i])
			except:
				pass
		for j in t:#用选出的节点构造新树

			newtree.append(Node(j.name,j.father,j.rank))
			#接下来找爸爸
			if j.name=="HEAD":
				pass
			else:
				n=0
				for k in newtree:
					if k.name==j.father.name:
						hisfather=k
						n+=1
				if n>1:
					log.insert(tk.END,"存在多个爸爸 %s's father %s\n"%(j.name,hisfather.name))
					log.see(tk.END)
					pass

				newtree[-1].father=hisfather
				hisfather.son.append(newtree[-1])#给爸爸加儿子
	for i in range(len(nodelist)):
		nodelist[i]=nodelist[i].name
	for i in range(len(newtree)):
		if newtree[i].name not in nodelist:
			newtree[i].name+="*"
	newtree=tree_toptodown("HEAD*",newtree)#新树按顺序排一遍
	return (newtree,cannotfind)

def fix_count_word(s):
	#剔除换行、一些标点、span、！链接、---分隔符，另外连续的数字和单词算作一个词
	n=len(s)
	n-=len("".join(re.findall("<span.*?>",s)))+len("".join(re.findall("</span>",s)))
	s=re.sub("<span.*?>","",s)
	s=re.sub("</span>","",s)
	n-=len("".join(re.findall("!\[.*?\]\(.*?\)",s)))
	s=re.sub("!\[.*?\]\(.*?\)","",s)
	n=n-len("".join(re.findall("[\n。，、“”‘’【】（）《》#|\{\},.\'\"\[\]\\<>()]",s)))-len("".join(re.findall("[a-zA-Z0-9 ]",s)))+len(re.findall("[a-zA-Z0-9]+",s))
	return n

def textbox_count_word_number(event):
	global number_of_word_in_textbox
	s=textbox.get("1.0",tk.END)
	n=fix_count_word(s)
	number_of_word_in_textbox.set(str(n))

def diary_count_word_number(s):
	n=fix_count_word(s)
	number_of_word_in_diary.set(str(n))

def tempfile_count_word_number(s):
	n=fix_count_word(s)
	number_of_word_in_tempfile.set(str(n))

def textbox_automatically_add_style(event):#给span包来个语法低亮,font=("Consolas",fontsize,"bold italic underline overstrike")
	fontsize=22*window_size
	try:
		textbox.tag_remove("span","1.0",tk.END)
		textbox.tag_remove("bold","1.0",tk.END)
		textbox.tag_remove("italic","1.0",tk.END)
		textbox.tag_remove("bolditalic","1.0",tk.END)
		textbox.tag_remove("overstrike","1.0",tk.END)
		textbox.tag_remove("underline","1.0",tk.END)
	except :
		pass
	index=0
	s=textbox.get("1.0",tk.END)
	s=s.split("\n")
	for row in range(len(s)):
		index_spanstart_start=[i.start() for i in re.finditer("<span.*?>",s[row])]
		index_spanstart_end=[i.end() for i in re.finditer("<span.*?>",s[row])]
		index_spanend_start=[i.start() for i in re.finditer("</span>",s[row])]
		index_spanend_end=[i.end() for i in re.finditer("</span>",s[row])]
		n=min(len(index_spanstart_start),len(index_spanend_start))
		for i in range(n):
			textbox.tag_config("span", foreground="#505050",font=("Hack",int(fontsize)))
			textbox.tag_add("span", "%s.%s"%(row+1,index_spanstart_start[i]),"%s.%s"%(row+1,index_spanstart_end[i]))
			textbox.tag_config("span", foreground="#505050",font=("Hack",int(fontsize)))
			textbox.tag_add("span", "%s.%s"%(row+1,index_spanend_start[i]),"%s.%s"%(row+1,index_spanend_end[i]))

		index_bolditalic_start=[i.start() for i in re.finditer("(?<!\*)\*\*\*[^*\n]+\*\*\*(?!\*)",s[row])]
		index_bolditalic_end=[i.end() for i in re.finditer("(?<!\*)\*\*\*[^*\n]+\*\*\*(?!\*)",s[row])]
		n=len(index_bolditalic_start)
		for i in range(n):
			textbox.tag_config("bolditalic",foreground="#FFFFFF",font=(fontfamily,int(fontsize*1.1),"bold italic"))
			textbox.tag_add("bolditalic", "%s.%s"%(row+1,index_bolditalic_start[i]),"%s.%s"%(row+1,index_bolditalic_end[i]))
		
		index_bold_start=[i.start() for i in re.finditer("(?<!\*)\*\*[^*\n]+\*\*(?!\*)",s[row])]
		index_bold_end=[i.end() for i in re.finditer("(?<!\*)\*\*[^*\n]+\*\*(?!\*)",s[row])]
		n=len(index_bold_start)
		for i in range(n):
			textbox.tag_config("bold",foreground="#FFFFFF",font=(fontfamily,int(fontsize*1.1),"bold"))
			textbox.tag_add("bold", "%s.%s"%(row+1,index_bold_start[i]),"%s.%s"%(row+1,index_bold_end[i]))

		index_italic_start=[i.start() for i in re.finditer("(?<!\*)\*[^*\n]+\*(?!\*)",s[row])]
		index_italic_end=[i.end() for i in re.finditer("(?<!\*)\*[^*\n]+\*(?!\*)",s[row])]
		n=len(index_italic_start)
		for i in range(n):
			textbox.tag_config("italic",foreground="#FFFFFF",font=(fontfamily,int(fontsize),"italic"))
			textbox.tag_add("italic", "%s.%s"%(row+1,index_italic_start[i]),"%s.%s"%(row+1,index_italic_end[i]))

		index_overstrike_start=[i.start() for i in re.finditer("~~.*?~~",s[row])]
		index_overstrike_end=[i.end() for i in re.finditer("~~.*?~~",s[row])]
		n=len(index_overstrike_start)
		for i in range(n):
			textbox.tag_config("overstrike",foreground="#FFFFFF",overstrike=1)
			textbox.tag_add("overstrike", "%s.%s"%(row+1,index_overstrike_start[i]),"%s.%s"%(row+1,index_overstrike_end[i]))

		index_underline_start=[i.start() for i in re.finditer("<u>.*?</u>",s[row])]
		index_underline_end=[i.end() for i in re.finditer("<u>.*?</u>",s[row])]
		n=len(index_underline_start)
		for i in range(n):
			textbox.tag_config("underline",foreground="#FFFFFF",underline=1)
			textbox.tag_add("underline", "%s.%s"%(row+1,index_underline_start[i]),"%s.%s"%(row+1,index_underline_end[i]))

#、、、如果不是侦测前后光标的话很可能替换过多，先咕咕咕 def manually_add_style(event,style):
#、、、如果不是侦测前后光标的话很可能替换过多，先咕咕咕 	selected=textbox.selection_get()

class MyScrollbar(tk.Canvas):
	def __init__(self, master, *args, **kwargs):
		self._scroll_kwargs = { 'command':None,
								'orient':'vertical',
								'buttontype':'round',
								'buttoncolor':'#141411',
								'troughcolor':'#383934',
								'thumbtype':'rectangle',
								'thumbcolor':'#555652',
								}
		
		kwargs = self._sort_kwargs(kwargs)
		if self._scroll_kwargs['orient'] == 'vertical':
			if 'width' not in kwargs:
				kwargs['width'] = 10
		elif self._scroll_kwargs['orient'] == 'horizontal':
			if 'height' not in kwargs:
				kwargs['height'] = 10
		else:
			raise ValueError
		if 'bd' not in kwargs:
			kwargs['bd'] = 0
		if 'highlightthickness' not in kwargs:
			kwargs['highlightthickness'] = 0
		
		tk.Canvas.__init__(self, master, *args, **kwargs)
		
		self.elements = {   'button-1':None,
							'button-2':None,
							'trough':None,
							'thumb':None}
		
		self._oldwidth = 0
		self._oldheight = 0
		
		self._sb_start = 0
		self._sb_end = 1
		
		self.bind('<Configure>', self._resize)
		self.tag_bind('button-1', '<Button-1>', self._button_1)
		self.tag_bind('button-2', '<Button-1>', self._button_2)
		self.tag_bind('trough', '<Button-1>', self._trough)
		
		self._track = False
		self.tag_bind('thumb', '<ButtonPress-1>', self._thumb_press)
		self.bind('<ButtonRelease-1>', self._thumb_release)
		#self.bind('<Leave>', self._thumb_release)
		
		self.bind('<Motion>', self._thumb_track)
			
	def _sort_kwargs(self, kwargs):
		to_remove = []
		for key in kwargs:
			if key in [ 'buttontype', 'buttoncolor', 'buttonoutline',
						'troughcolor', 'troughoutline',
						'thumbcolor', 'thumbtype', 'thumboutline',
						'command', 'orient']:
				self._scroll_kwargs[key] = kwargs[key] # add to custom dict
				to_remove.append(key)
				
		for key in to_remove:
			del kwargs[key]
		return kwargs
		
	def _get_colour(self, element):
		if element in self._scroll_kwargs: # if element exists in settings
			return self._scroll_kwargs[element]
		if element.endswith('outline'): # if element is outline and wasn't in settings
			return self._scroll_kwargs[element.replace('outline', 'color')] # fetch default for main element
		
	def _width(self):
		return self.winfo_width() - 2 # return width minus 2 pixes to ensure fit in canvas
		
	def _height(self):
		return self.winfo_height() - 2 # return height minus 2 pixes to ensure fit in canvas
				
	def _resize(self, event):
		width = self._width()
		height = self._height()
		if self.elements['button-1']: # exists
			# delete element if vertical scrollbar and width changed
			# or if horizontal and height changed, signals button needs to change
			if (((self._oldwidth != width) and (self._scroll_kwargs['orient'] == 'vertical')) or
				((self._oldheight != height) and (self._scroll_kwargs['orient'] == 'horizontal'))):
				self.delete(self.elements['button-1'])
				self.elements['button-1'] = None
		if not self.elements['button-1']: # create
			size = width if (self._scroll_kwargs['orient'] == 'vertical') else height
			rect = (0,0,size, size)
			fill = self._get_colour('buttoncolor')
			outline = self._get_colour('buttonoutline')
			if (self._scroll_kwargs['buttontype'] == 'round'):
				self.elements['button-1'] = self.create_oval(rect, fill=fill, outline=outline, tag='button-1')
			elif (self._scroll_kwargs['buttontype'] == 'square'):
				self.elements['button-1'] = self.create_rectangle(rect, fill=fill, outline=outline, tag='button-1')
			
		if self.elements['button-2']: # exists
			coords = self.coords(self.elements['button-2'])
			# delete element if vertical scrollbar and width changed
			# or if horizontal and height changed, signals button needs to change
			if (((self._oldwidth != width) and (self._scroll_kwargs['orient'] == 'vertical')) or
				((self._oldheight != height) and (self._scroll_kwargs['orient'] == 'horizontal'))):
				self.delete(self.elements['button-2'])
				self.elements['button-2'] = None
			# if vertical scrollbar and height changed button needs to move
			elif ((self._oldheight != height) and (self._scroll_kwargs['orient'] == 'vertical')):
				self.move(self.elements['button-2'], 0, height-coords[3])
			# if horizontal scrollbar and width changed button needs to move
			elif ((self._oldwidth != width) and (self._scroll_kwargs['orient'] == 'horizontal')):
				self.move(self.elements['button-2'], width-coords[2], 0)
		if not self.elements['button-2']: # create
			if (self._scroll_kwargs['orient'] == 'vertical'):
				rect = (0,height-width,width, height)
			elif (self._scroll_kwargs['orient'] == 'horizontal'):
				rect = (width-height,0,width, height)
			fill = self._get_colour('buttoncolor')
			outline = self._get_colour('buttonoutline')
			if (self._scroll_kwargs['buttontype'] == 'round'):
				self.elements['button-2'] = self.create_oval(rect, fill=fill, outline=outline, tag='button-2')
			elif (self._scroll_kwargs['buttontype'] == 'square'):
				self.elements['button-2'] = self.create_rectangle(rect, fill=fill, outline=outline, tag='button-2')
		
		if self.elements['trough']: # exists
			coords = self.coords(self.elements['trough'])
			# delete element whenever width or height changes
			if (self._oldwidth != width) or (self._oldheight != height):
				self.delete(self.elements['trough'])
				self.elements['trough'] = None
		if not self.elements['trough']: # create
			if (self._scroll_kwargs['orient'] == 'vertical'):
				rect = (0, int(width/2), width, height-int(width/2))
			elif (self._scroll_kwargs['orient'] == 'horizontal'):
				rect = (int(height/2), 0, width-int(height/2), height)
			fill = self._get_colour('troughcolor')
			outline = self._get_colour('troughoutline')
			self.elements['trough'] = self.create_rectangle(rect, fill=fill, outline=outline, tag='trough')

		self.set(self._sb_start, self._sb_end) # hacky way to redraw thumb without moving it
		self.tag_raise('thumb') # ensure thumb always on top of trough
			
		self._oldwidth = width
		self._oldheight = height
		
	def _button_1(self, event):
		command = self._scroll_kwargs['command']
		if command:
			command('scroll', -1, 'pages')
		return 'break'
	
	def _button_2(self, event):
		command = self._scroll_kwargs['command']
		if command:
			command('scroll', 1, 'pages')
		return 'break'
		
	def _trough(self, event):
		#print('trough: (%s, %s)' % (event.x, event.y))
		width = self._width()
		height = self._height()
		
		coords = self.coords(self.elements['trough'])
		
		if (self._scroll_kwargs['orient'] == 'vertical'):
			trough_size = coords[3] - coords[1]
		elif (self._scroll_kwargs['orient'] == 'horizontal'):
			trough_size = coords[2] - coords[0]
		#print('trough size: %s' % trough_size)
		
		size = (self._sb_end - self._sb_start) / 1
		if (self._scroll_kwargs['orient'] == 'vertical'):
			thumbrange = height - width
		elif (self._scroll_kwargs['orient'] == 'horizontal'):
			thumbrange = width - height
		thumbsize = int(thumbrange * size)
		
		if (self._scroll_kwargs['orient'] == 'vertical'):
			thumboffset = int(thumbrange * self._sb_start) + int(width/2)
		elif (self._scroll_kwargs['orient'] == 'horizontal'):
			thumboffset = int(thumbrange * self._sb_start) + int(height/2)
		thumbpos = int(thumbrange * size / 2) + thumboffset
		
		command = self._scroll_kwargs['command']
		if command:
			if (((self._scroll_kwargs['orient'] == 'vertical') and (event.y < thumbpos)) or
				((self._scroll_kwargs['orient'] == 'horizontal') and (event.x < thumbpos))):
				command('scroll', -1, 'pages')
			elif (((self._scroll_kwargs['orient'] == 'vertical') and (event.y > thumbpos)) or
				((self._scroll_kwargs['orient'] == 'horizontal') and (event.x > thumbpos))):
				command('scroll', 1, 'pages')
		return 'break'
	
	def _thumb_press(self, event):
		self._track = True
		
	def _thumb_release(self, event):
		self._track = False
			
	def _thumb_track(self, event):
		#print('track')
		if self._track:
			width = self._width()
			height = self._height()
			#print("window size: (%s, %s)" % (width, height))
			
			size = (self._sb_end - self._sb_start) / 1
			
			coords = self.coords(self.elements['trough'])
			#print('trough coords: %s' % coords)
			
			if (self._scroll_kwargs['orient'] == 'vertical'):
				trough_size = coords[3] - coords[1]
				thumbrange = height - width
			elif (self._scroll_kwargs['orient'] == 'horizontal'):
				trough_size = coords[2] - coords[0]
				thumbrange = width - height
				#print('trough size: %s' % trough_size)
				
			thumbsize = int(thumbrange * size)
			
			if (self._scroll_kwargs['orient'] == 'vertical'):
				pos = max(min(trough_size, event.y - coords[1] - (thumbsize/2)), 0)
			elif (self._scroll_kwargs['orient'] == 'horizontal'):
				pos = max(min(trough_size, event.x - coords[0] - (thumbsize/2)), 0)
			
		#print('pos: %s' % pos)
			
			point = pos / trough_size
		#print('point: %s' % point)
			
			command = self._scroll_kwargs['command']
			if command:
				command('moveto', point)
			return 'break'
		
	def set(self, *args):
		#print('set: %s' % str(args))
		oldsize = (self._sb_end - self._sb_start) / 1
		
		self._sb_start = float(args[0])
		self._sb_end = float(args[1])
		
		size = (self._sb_end - self._sb_start) / 1
		
		width = self._width()
		height = self._height()
		
		if oldsize != size:
			self.delete(self.elements['thumb'])
			self.elements['thumb'] = None
		
		if (self._scroll_kwargs['orient'] == 'vertical'):
			thumbrange = height - width
			thumboffset = int(thumbrange * self._sb_start) + int(width/2)
		elif (self._scroll_kwargs['orient'] == 'horizontal'):
			thumbrange = width - height
			thumboffset = int(thumbrange * self._sb_start) + int(height/2)
		thumbsize = int(thumbrange * size)
		
		if not self.elements['thumb']: # create
			if (self._scroll_kwargs['orient'] == 'vertical'):
				rect = (0, thumboffset,width, thumbsize+thumboffset)
			elif (self._scroll_kwargs['orient'] == 'horizontal'):
				rect = (thumboffset, 0, thumbsize+thumboffset, height)
			fill = self._get_colour('thumbcolor')
			outline = self._get_colour('thumboutline')
			if (self._scroll_kwargs['thumbtype'] == 'round'):
				self.elements['thumb'] = self.create_oval(rect, fill=fill, outline=outline, tag='thumb')
			elif (self._scroll_kwargs['thumbtype'] == 'rectangle'):
				self.elements['thumb'] = self.create_rectangle(rect, fill=fill, outline=outline, tag='thumb')
		else: # move
			coords = self.coords(self.elements['thumb'])
			if (self._scroll_kwargs['orient'] == 'vertical'):
				if (thumboffset != coords[1]):
					self.move(self.elements['thumb'], 0, thumboffset-coords[1])
			elif (self._scroll_kwargs['orient'] == 'horizontal'):
				if (thumboffset != coords[1]):
					self.move(self.elements['thumb'], thumboffset-coords[0], 0)
		return 'break'

def open_tempfile_in_typora():
	os.chdir(base)
	os.system("%s ./%s"%(typora_location,tempfile_name))

def open_tempfile_in_sublime():
	os.chdir(base)
	os.system('%s ./%s'%(sublime_location,tempfile_name))


def generate_encrypt_key(p):
	key=[]
	for i in p:
		key.append((ord(i)%51)*((-1)**(ord(i)%2)))
	return key

def encrypting_text(s,n):
	return chr(ord(s)+5000+(n%29)*(-1)**(n%3)+encrypt_key[n%len(encrypt_key)]*(-1)**(n%2))

def decrypting_text(s,n):
	return chr(ord(s)-5000-(n%29)*(-1)**(n%3)-encrypt_key[n%len(encrypt_key)]*(-1)**(n%2))

def verify_consistency(p):#登录时拿输入的密码去撞user_setting，如果和里面的密码相同，则开锁
	global password,encrypt_key
	password=p
	encrypt_key=generate_encrypt_key(p)
	try:
		s=decrypting(0,"./user_setting")
		s=s.split("\n")
		if s[-1].split("=")[-1]==password:
			return 1
		else:
			return -1
	except:
		return -1

def encrypting(s,input_file,output_file=0):
	if input_file!=0 and s==0:
		with open(input_file,"r",encoding="utf-8") as f:
			origin=f.read()
	elif input_file==0 and s!=0:
		origin=s

	new=""
	n=0
	for i in origin:
		new+=encrypting_text(i,n)#异或优先级低于加减乘除……
		n+=1

	if output_file!=0:
		with open(output_file,"w",encoding="utf-8") as f:
			f.write(new)
			return
	return new

def decrypting(s,input_file,output_file=0):
	if input_file!=0 and s==0:
		with open(input_file,"r",encoding="utf-8") as f:
			origin=f.read()
	elif input_file==0 and s!=0:
		origin=s

	new=""
	n=0
	for i in origin:
		new+=decrypting_text(i,n)
		n+=1

	if output_file!=0:
		with open(output_file,"w",encoding="utf-8") as f:
			f.write(new)
			return
	return new





def what_name_is_the_tempfile():#tempfile_name是带.md的。支持了进程多开，但不建议，容易操作不当
	global base
	l=os.listdir(base)
	for i in range(5):
		flag=0
		tempfile_name="temp"+str(i)+".md"
		for j in l:
			if j==tempfile_name:
				flag=1
		if flag==0:
			return tempfile_name
	log.insert(tk.END,"大哥你开这么多干啥？\n")
	log.see(tk.END)
	os.system("pause")
	os._exit()

def what_name_is_the_output_file():
	global output_selection_file_name_head,output_selection_file_name_tail
	return output_selection_file_name_head+output_selection_file_name_tail

def fix_output_file_name(s):
	return s.replace(" ","").replace("-","").replace("\\","")

def what_day_is_it():#有BUG的，每月初不会退位，但我懒得整了，您少熬点夜吧
	if time.localtime()[3]<6:#六点前算前一天
		t=str(time.localtime()[0])+"."+str(time.localtime()[1])+"."+str(time.localtime()[2]-1)
	else:
		t=str(time.localtime()[0])+"."+str(time.localtime()[1])+"."+str(time.localtime()[2])
	return t

def what_time_is_it():
	t=""
	for i in range(6):
		t+=str(time.localtime()[i])+"_"
	return t

def goodbye(event):
	try:
		os.remove("./%s"%tempfile_name)
	except :
		pass
	os._exit(0)

def remove_emoji(s):#tkinter不支持显示高于\uFFFF的字符，所以有一些高于markdown支持的emoji版本的emoji就很讨厌了，尽量用markdown的:xxx:表情吧
	# c = [s[j] for j in range(len(s)) if ord(s[j]) in range(65536)]
	c=""
	for i in s:
		if ord(i) in range(65536):
			c+=i
		else:
			log.insert(tk.END,"超出\\uFFFF的字符：%s"%i)
			log.see(tk.END)
			c+="\\u%s"%ord(i)#这里遇到的会转成\uxxxxx显示
	return c

def findtag(file,temp=0):
	l={}#单标签集合
	ll={}#多重标签集合
	with open(file,"r",encoding="utf-8") as f:
		a=f.readline()
		if temp==0:
			a=decrypting(a,0)
		while a!="":
			c=re.findall("(?<=tag\=\").*?(?=\")",a)
			if c==[]:
				if l.get("NONE")==None:
					l["NONE"]=1
				else:
					l["NONE"]+=1
				a=f.readline()
				continue
			for i in c:
				if l.get(i)==None:
					l[i]=1
				else:
					l[i]+=1
			if len(c)>1:
				c=sorted(c)#多重标签排排序，相同却不同顺序的多重标签只算作一种
				t=str(c)#列表不能进字典，变成str好了
				if ll.get(t)==None:
					ll[t]=1
				else:
					ll[t]+=1
			a=f.readline()
	return (l,ll)

def inin(a,b):#判断a是否包含于b
	if a==[]:
		return 0
	for i in a:
		if i not in b:
			return 0
	return 1

def hanzi_to_pinyin(last_name):
	"""
	功能说明：将姓名转换为拼音首字母缩写
	参数：hanzi_to_pinyin(u'习大大')
	返回值：xdd
	"""
	rows = pypinyin.pinyin(last_name, style=pypinyin.NORMAL)  # 获取姓氏首字母
	return ''.join(row[0][0] for row in rows if len(row) > 0)   # 拼接姓名首字母字符串

def convert_to_az(c):#用unicode划分语言区
	def jp_to_az(i):
		jp1=["”","“","《","》","あ","い","う","え","お","か","き","く","け","こ","さ","し","す","せ","そ","た","ち","つ","て","と","な","に","ぬ","ね","の","は","ひ","ふ","へ","ほ","ま","み","む","め","も","や","ゆ","よ","ら","り","る","れ","ろ","わ","を","ん","が","ぎ","ぐ","げ","ご","ざ","じ","ず","ぜ","ぞ","だ","ぢ","づ","で","ど","ば","び","ぶ","べ","ぼ","ぱ","ぴ","ぷ","ぺ","ぽ"]
		jp2=["”","“","《","》","ア","イ","ウ","エ","オ","カ","キ","ク","ケ","コ","サ","シ","ス","セ","ソ","タ","チ","ツ","テ","ト","ナ","ニ","ヌ","ネ","ノ","ハ","ヒ","フ","ヘ","ホ","マ","ミ","ム","メ","モ","ヤ","ユ","ヨ","ラ","リ","ル","レ","ロ","ワ","ヲ","ン","ガ","ギ","グ","ゲ","ゴ","ザ","ジ","ズ","ゼ","ゾ","ダ","ヂ","ヅ","デ","ド","バ","ビ","ブ","ベ","ボ","パ","ピ","プ","ペ","ポ"]
		az=["”","“","《","》","a","i","u","e","o","ka","ki","ku","ke","ko","sa","si","su","se","so","ta","ti","tu","te","to","na","ni","nu","ne","no","ha","hi","hu","he","ho","ma","mi","mu","me","mo","ya","yu","yo","ra","ri","ru","re","ro","wa","wo","n","ga","gi","gu","ge","go","za","ji","zu","ze","zo","da","di","du","de","do","ba","bi","bu","be","bo","pa","pi","pu","pe","po"]
		try:
			n=jp1.index(i)
			return az[n]
		except:
			try:
				n=jp2.index(i)
				return az[n]
			except:
				log.insert(tk.END,"%s	假名好像不完整\n"%i)
				log.see(tk.END)

		return ""
	s=""
	s+="^"#开头标识符
	for i in c:
		if re.match(r"[\u0000-\u007F]",i):#英
			s+=i.lower()
		elif re.match(r"[\u4E00-\u9FFF]",i):#中
			s+=hanzi_to_pinyin(i[0])
		elif re.match(r"[\u0800-\u4DFF]",i):#日，\u4E00是中文的一
			s+=jp_to_az(i)
		# if re.match(r"[\uAC00-\uD7FF]",c)#韩
	s+="$"#结尾标识符
	return s

def clearwindow(event):
	global extract_right_from,right_listing_from,showned_text,allrightlist,allleftlist,output_selection_file_name_head,output_selection_file_name_tail,old_diary_text,left_previous_title,left_current_title
	extract_right_from=""
	right_listing_from=""
	showned_text=""
	allrightlist=[]
	allleftlist=[]
	output_selection_file_name_head=""
	output_selection_file_name_tail=""
	old_diary_text=""
	left_previous_title=[]
	left_current_title=[]
	textbox.delete("1.0",tk.END)
	textbox_count_word_number(0)
	tempfile_count_word_number("")
	diary_count_word_number("")
	with open("%s"%tempfile_name,"w",encoding="utf-8") as f:
		f.write("")
	listlefttitle()
	listbox_right.delete(0,listbox_right.size())
	log.insert(tk.END,"清空工作台\n")
	log.see(tk.END)


def readin_entire_diary():
	global right_listing_from,extract_right_from,showned_text,old_diary_text,output_selection_file_name_head,output_selection_file_name_tail,left_previous_title,left_current_title
	log.insert(tk.END,"展示手账的全部\n")
	log.see(tk.END)
	textbox.delete("1.0",tk.END)
	textbox.insert(tk.END,remove_emoji(decrypting(0,diary_file_path)))
	textbox_automatically_add_style(1)
	textbox_count_word_number(0)
	save_temp_file("creating")
	listlefttitle()


	right_listing_from="title"
	extract_right_from="title"
	left_previous_title=[]
	left_current_title=[]
	old_diary_text=textbox.get("1.0",tk.END)
	showned_text=textbox.get("1.0",tk.END)
	output_selection_file_name_head="手账_"
	output_selection_file_name_tail="All"


def show_current_file():
	global showned_text,output_selection_file_name_head,output_selection_file_name_tail
	log.insert(tk.END,"展示temp.md\n")
	log.see(tk.END)
	textbox.delete("1.0",tk.END)
	try:
		listlefttitle()
		with open("./%s"%tempfile_name,"r",encoding="utf-8") as f:
			s=f.read()
			textbox.insert(tk.END,remove_emoji(s))
			tempfile_count_word_number()
	except :
		pass
	textbox_count_word_number(0)

	showned_text=textbox.get("1.0",tk.END)
	output_selection_file_name_tail="All"
	textbox_automatically_add_style(1)

def save_temp_file(mode,silence=0,event=0):#tag和tree的选集可能在一个标题层级内是分裂的，覆盖替换可能找不到也很危险。所以只做title出来时才保存temp，才进行替换操作！
	global showned_text,extract_right_from
	if mode=="editing":#在左边的listbox之间切换时的保存操作，或点下方的手动保存
		if extract_right_from=="title":#
			new=textbox.get("1.0",tk.END)
			old=showned_text
			with open("./%s"%tempfile_name,"r",encoding="utf-8") as f,open("./1.md","w",encoding="utf-8") as fo:
				s=f.read()
				# 、、#、、、、、、re.findall("%s"%old.strip(),s))#这里传了一大段文本进去，如果里面有.*?等会被认为是通配符号，re库就可能匹配出错
				n=s.count(old.strip())
				if n>1:
					log.insert(tk.END,"保存出错，temp替换出现%s个重复内容\n"%n)
					log.insert(tk.END,"要替换的内容为%s\n"%old)
					log.see(tk.END)
					return
				log.insert(tk.END,"已替换：%s个内容\n"%n)
				log.see(tk.END)
				s=s.replace(old.strip(),new.strip())
				fo.write(s)
				tempfile_count_word_number(s)
			os.remove("%s"%tempfile_name)
			os.rename("1.md","%s"%tempfile_name)
			listlefttitle()
			showned_text=textbox.get("1.0",tk.END)#
			log.insert(tk.END,"保存text替换成功\n")
			log.see(tk.END)
		else:
			log.insert(tk.END,"不好意思，只有title的选集才能保存操作，您别折腾了，点上面一个按键重新读取选集文件吧。\n")
			log.see(tk.END)
	elif mode=="creating":#从右边抽取选集或导入手账全集的时候，重写temp.md文件
		new=textbox.get("1.0",tk.END)
		tempfile_count_word_number(new)
		with open("./%s"%tempfile_name,"w",encoding="utf-8") as f:
			f.write(new)
		log.insert(tk.END,"新建temp.md\n")
		log.see(tk.END)
		if silence==1:#保存md的时候会用到
			return
		listlefttitle()

#、、、、 def overwrite_temp_file():#不要了，没必要。
#、、、、 	with open("./%s"%tempfile_name,"w",encoding="utf-8") as f:
#、、、、 		f.write(textbox.get("1.0",tk.END))
#、、、、 	log.insert(tk.END,"已将当前页面覆盖到temp.md中\n")
#、、、、 	log.see(tk.END)

def save_current_to_diary():
	global updated
	if extract_right_from=="title":
		global old_diary_text,right_listing_from
		old=old_diary_text
		s=decrypting(0,diary_file_path)
		with open("./%s"%tempfile_name,"r",encoding="utf-8") as f:
			new=f.read()
		n=s.count(old.strip())
		if n>1:
			log.insert(tk.END,"保存出错，手账替换出现%s个重复内容如下：\n"%n)
			log.insert(tk.END,"要替换的内容为%s\n"%old.strip())
			log.see(tk.END)
			return
		log.insert(tk.END,"已替换：%s个内容\n"%n)
		log.see(tk.END)
		s=s.replace(old.strip(),new.strip())
		encrypting(s,0,diary_file_path)
		#、、、这个是没保存一次就备份一下之前的快照，现在稳定点了就不用了 encrypting(s,0,"./autobackup/%s_%s"%(what_time_is_it(),diary_file_path.split("/")[-1]))
		diary_count_word_number(s)
		old_diary_text=new#既然手账都被修改了，工作台正在编辑的文件原型也要更新
		if right_listing_from=="title":
			listrighttitle()
		elif right_listing_from=="tag":
			listrighttag()
	else:
		log.insert(tk.END,"不好意思，只有title的选集才能保存操作，您别折腾了，点上面一个按键重新读取选集文件吧。\n")
		log.see(tk.END)
	updated=1


def listleft_add_one():
	new=entry_input.get()
	if new!="":
		if new.count("#")<1:
			log.insert(tk.END,"请标明titile的级数！\n")
			log.see(tk.END)
			return
		with open("./%s"%tempfile_name,"r",encoding="utf-8") as f,open("./1.md","w",encoding="utf-8") as fo:
			s=f.read()
			old=listbox_left.get(str(int(listbox_left.index(tk.ACTIVE))+1)).strip("-")#选中的title的后一项
			if old!="":
				if len(re.findall("\n%s\n"%old,s))>1 or len(re.findall("\n%s\n"%new,s))>0:
					log.insert(tk.END,"有标题重名了，先修一下吧\n")
					log.see(tk.END)
					return
				else:
					s=re.sub("\n%s\n"%old,"\n"+new+"\n\n"+old+"\n",s)#添加在后一项的前面
					log.insert(tk.END,"已在temp.md中添加节点：%s\n"%new)
					log.see(tk.END)
			else:#如果在最后添加
				if len(re.findall("\n%s\n"%new,s))>0:
					log.insert(tk.END,"有标题重名了，先修一下吧\n")
					log.see(tk.END)
					return
				s+="\n"+new+"\n"
				log.insert(tk.END,"已在temp.md中添加节点：%s\n"%new)
				log.see(tk.END)
			fo.write(s)
				# 、、、、、、、、listbox_left.insert(str(int(listbox_left.index(tk.ACTIVE))+1),new.count("#")*"-"+new)#呃呃呃呃呃连index都得是字符……
		os.remove("%s"%tempfile_name)
		os.rename("1.md","%s"%tempfile_name)
		listlefttitle()

def listleft_delete_one():
	t=listbox_left.get(tk.ACTIVE).strip("-")
	textbox.delete("1.0",tk.END)
	textbox_count_word_number(0)
	with open("./%s"%tempfile_name,"r",encoding="utf-8") as f,open("./1.md","w",encoding="utf-8") as fo:
		s=f.read()
		try:
			re.findall("%s\n[\s\S]*?(?=#)"%t,s)[0]
			s=re.sub("%s\n[\s\S]*?(?=#)"%t,"",s)
			fo.write(s)
		except :#在最后的一个标题
			try:
				s=re.sub("%s\n[\s\S]*"%t,"",s)
				fo.write(s)
			except :
				pass
	os.remove("%s"%tempfile_name)
	os.rename("1.md","%s"%tempfile_name)
	listlefttitle()
	log.insert(tk.END,"已在temp.md中删除节点：%s\n"%t)
	log.see(tk.END)

def add_today():
	s=decrypting(0,diary_file_path)
	t=what_day_is_it()
	if s.count("### %s"%t)<1:
		log.insert(tk.END,"已替换：%s个内容\n"%s.count("————————"))
		log.see(tk.END)
		s=s.replace("————————","### "+t+"\n\n"+textbox.get("1.0",tk.END)+"\n————————")
	else:
		log.insert(tk.END,"已替换：%s个内容\n"%s.count("————————"))
		log.see(tk.END)
		s=s.replace("————————",textbox.get("1.0",tk.END)+"\n————————")
	encrypting(s,0,diary_file_path)
	adddate()
	listrighttitle()
	diary_count_word_number(s)



def listbox_get_multiple_selection(self):#处理listbox多选的内容。
	a=self.curselection()
	b=[]
	for i in a:
		if i!=None:
			b.append(self.get(i))
	return b

def listlefttitle(from_button=0):
	global allleftlist,left_listbox_index
	global left_listing_from,left_current_title,left_previous_title,showned_text
	if from_button==1:
		left_listbox_index=0
	listbox_left.delete(0,listbox_left.size())
	allleftlist=[]
	log.insert(tk.END,"列出temp的title\n")
	log.see(tk.END)
	with open("./%s"%tempfile_name,"r",encoding="utf-8") as f:
		s=f.read()
	if left_listing_from!="title":#如果从左边tag或tree回来，那要重置listbox，防止选集的保存操作出错
		textbox.delete("1.0",tk.END)
		textbox.insert(tk.END,s)
		textbox_automatically_add_style(1)
		showned_text=s
		left_current_title=[]
		left_previous_title=[]
	left_listing_from="title"
	s=re.findall("#+ .*",s)
	for i in s:
		# listbox_left.insert('end',(i.count("#")-1)*"-"+i)#给个缩进
		allleftlist.append([i,convert_to_az(i)])
	search_leftlist_whiletyping(0)


def listlefttag(from_button=0):
	global allleftlist,left_listbox_index
	global left_listing_from,left_current_title,left_previous_title
	if from_button==1:
		left_listbox_index=0
	listbox_left.delete(0,listbox_left.size())
	allleftlist=[]
	left_current_title=[]
	left_previous_title=[]
	left_listing_from="tag"
	log.insert(tk.END,"列出temp的TAG\n")
	log.see(tk.END)
	(l,ll)=findtag("./%s"%tempfile_name,1)
	l=sorted(l.items(),key=lambda x:hanzi_to_pinyin(x[0]))#按拼音排序
	tag_tree=[]
	for i in l:
		tag_tree.append(i[0])#其实以前写的函数是连tag次数都统计了的，这里不需要了
	(tag_tree,cannotfind)=tree_downtotop(tag_tree)
	if tag_tree!=None:
		for i in tag_tree:
			allleftlist.append([i.rank*"\t"+"\\"+i.name,convert_to_az(i.name)])
	if cannotfind!=None:
		for i in cannotfind:
			allleftlist.append([i,convert_to_az(i)])
	search_leftlist_whiletyping(0)

# def listlefttree():
# 	global allleftlist
# 	global left_listing_from,left_current_title,left_previous_title
# 	listbox_left.delete(0,listbox_left.size())
# 	allleftlist={}
# 	left_current_title=[]
# 	left_previous_title=[]
# 	left_listing_from="tree"
# 	log.insert(tk.END,"列出左侧的tree\n")
# 	log.see(tk.END)
# 	s=tree_toptodown("HEAD")
# 	for i in s:
# 		allleftlist[i.rank*"\t"+"\\"+i.name]=convert_to_az(i.name)
# 		listbox_left.insert('end',i.rank*"-"+"\\"+i.name)#给个缩进


def listrighttitle(from_button=0):
	global allrightlist,right_listbox_index
	global right_listing_from
	if from_button==1:
		right_listbox_index=0
	listbox_right.delete(0,listbox_right.size())
	allrightlist=[]
	right_listing_from="title"
	log.insert(tk.END,"列出手账的title\n")
	log.see(tk.END)
	s=decrypting(0,diary_file_path)
	diary_count_word_number(s)
	s=re.findall("#+ .*",s)
	for i in s:
		# listbox_right.insert('end',(i.count("#")-1)*"-"+i)#给个缩进
		allrightlist.append([i,convert_to_az(i)])
	search_rightlist_whiletyping(0)

def listrighttag(from_button=0):
	global allrightlist,right_listbox_index
	global right_listing_from
	if from_button==1:
		right_listbox_index=0
	listbox_right.delete(0,listbox_right.size())
	allrightlist=[]
	right_listing_from="tag"
	log.insert(tk.END,"列出手账的TAG\n")
	log.see(tk.END)
	(l,ll)=findtag(diary_file_path)
	l=sorted(l.items(),key=lambda x:hanzi_to_pinyin(x[0]))#按拼音排序
	tag_tree=[]
	for i in l:
		tag_tree.append(i[0])#其实以前写的函数是连tag次数都统计了的，这里不需要了
	(tag_tree,cannotfind)=tree_downtotop(tag_tree)
	if tag_tree!=None:
		for i in tag_tree:
			allrightlist.append([i.rank*"\t"+"\\"+i.name,convert_to_az(i.name)])
	if cannotfind!=None:
		for i in cannotfind:
			allrightlist.append([i,convert_to_az(i)])
	search_rightlist_whiletyping(0)

# def listrighttree():
# 	global allrightlist
# 	global right_listing_from
# 	listbox_right.delete(0,listbox_right.size())
# 	allrightlist={}
# 	right_listing_from="tree"
# 	log.insert(tk.END,"列出右侧的title\n")
# 	log.see(tk.END)
# 	s=tree_toptodown("HEAD")
# 	for i in s:
# 		allrightlist[i.rank*"\t"+"\\"+i.name]=convert_to_az(i.name)
# 		listbox_right.insert('end',i.rank*"-"+"\\"+i.name)#给个缩进

def extractselection(event,key,leftlist=0):
	def extraction_in_tags(key,splited=0,file=diary_file_path):#如果传进来的tag列表是splited，则在每一行中分开查找列表中的单个tag，列出tag树要最大化得列，不过可能会有点小问题，见下面的注释
		def multispanfinder(a,tag):#一段里有多个span，找出所有符合tag搜寻条件的，按顺序输出
			working=[]
			done=[]
			spans=[]
			temp=""
			rank=0#包的层级
			for i in a:
				temp+=i
				if temp[-5:]=="<span":
					working.append("")
					rank+=1#每进入一层就加一级
				if len(working)>0:
					for j in range(len(working)):
						working[j]+=i
				if temp[-7:]=="</span>":
					done.append((rank,working.pop()))
					rank-=1#每出去一层就减一级
			#done是[[1,""],[2,""],[2,""],[1,""]]包的层级和未加工的包
			for i in done:
				tags=re.findall("(?<=tag=\").*?(?=\")",re.match("^n.*?>",i[1]).group())#找出最外层的tags
				t=re.sub("<span .*?\">","",i[1])#去掉所有的tag标签
				t=re.sub("n .*?\">","",t)#去掉所有的tag标签
				t=re.sub("</span>","",t)#去掉所有的tag标签
				spans.append((i[0],tags,t))#将包的层级、标签、纯文本依次存在spans组中
			"牛逼的话可以分析层级序列来使包的并列、包含关系平坦化，还可能用更好的数据结构方法更方便地存储、分析数据"
			"菜鸡想不清算法，先暴力算一算，所以这里层级没用了"
			select=[]
			out=""
			for i in spans:
				if inin(tag,i[1]):
					select.append(i[2])
			for i in select:
				flag=0
				for j in select:
					if i==j:
						continue
					elif i in j:
						flag=1
				if flag==1:
					continue
				else:
					out+=i
			return out
		def extract_single_line(a,tag,refresh,flag,istable,date,fetchtitle):
			t=""
			if a[0]=="#" and fetchtitle==1:
				if flag==1:
					date="\n"+a
					flag=0
				else:
					date=a
				refresh=1
			c=re.findall("(?<=tag\=\").*?(?=\")",a)#当前行的tag
			if tag==["NONE"]:

				if c==[] and a!="---\n" and a!=">\n" and a!="> \n" and re.findall("^#+ ",a)==[]:
					t=a
					return (t,refresh,flag,istable,date)
				else:
					t=""
					return (t,refresh,flag,istable,date)
			if inin(tag,c) or istable==1:#如果要筛选的tag在当前行的子集内
				if len(re.findall("</span>",a))>1:
				#如果一段内有多个<span>分划或互相包裹，用正则很难搜出来，是在懒得编程给你个标记语言自己瞅吧，所以尽量不要一段多点
					t=multispanfinder(a,tag)+"\n"
				else:
				#如果一段内只有一个<span>
					if a[0:6]=="<table":#进入表格区间
						istable=1
						t="<table>"
					if istable==1:
						t=a[:-1]
						if a=="\n":#退出表格区间
							istable=0
					if istable==0:
						if a[0]==">":#如果是引用
							if re.findall("!\[.*\]\(.*\)",a)!=[]:#引用中有图片链接，不管图片是在一行中的什么位置
								flag=1
								t=re.sub(" tag=.*\"","",a)+re.match("(> )*",a).group()#则要去除tag=""
							else:
								flag=1
								t=re.sub("<.*?>","",a)+re.match("(> )*",a).group()#因为上面是选出有tag的进行输出，所以引用的空行要额外输出
						elif a[0]=="!":#如果是图片链接
							t=re.sub(" tag=.*\"","",a)#则要去除tag=""
							if flag==1:
								t="\n"+t
								flag=0
						elif a[0:6]=="<video":
							t=re.sub(' tag=".*?"',"",a)
						elif a[0:4]=="<img":
							t=re.sub(' tag=".*?"',"",a)
						elif a[1:3]==". ":#数字列表
							t=re.sub("</?span.*?>","",a)
						elif a.strip()[0:2]=="- ":#方块列表
							t=re.sub("</?span.*?>","",a)
						else:#普通段落
							t="".join(re.findall("(?<=\">).*?(?=</span>)",a))+"\n"
							if flag==1:
								t="\n"+t
								flag=0
			return (t,refresh,flag,istable,date)

		log.insert(tk.END,"抽取选集：%s\n"%key)
		log.see(tk.END)
		fetchtitle=1
		refresh=0#筛选所属的标题用
		flag=0#标志进入引用区块，离开引用区块时要再输出一行空行
		istable=0#是否进入表格区间
		date=""
		result=""

		if len(key)==1 and key[0][-1]=="*":
			key[0]=key[0][:-1].strip("-")
			extraction_in_tree(key,file)
			return
		for i in range(len(key)):
			key[i]=key[i].strip("-").strip("*").strip("\\")
		if file==diary_file_path:
			decrypting(0,diary_file_path,"./1.md")
			file="./1.md"
		with open(file,"r",encoding="utf-8") as f:
			a=f.readline()
			while a!="":
				if splited==1:
					for i in key:#这里是依次把所有的tag查了一遍，没有作查重。所以默认是标明的tag不是树中的从属关系，如果是从属关系，那就会列出来重复的多次，不过也不是很大的问题
						(t,refresh,flag,istable,date)=extract_single_line(a,[i],refresh,flag,istable,date,fetchtitle)
						if t!=""and t!="\n":#我也不知道为什么可能找出来个\n
							if refresh==1 and fetchtitle==1:
								result+=date+"\n"
							result+=t+"\n"
							refresh=0
				else:
					(t,refresh,flag,istable,date)=extract_single_line(a,key,refresh,flag,istable,date,fetchtitle)
					if t!="" and t!="\n":#我也不知道为什么可能找出来个\n
						if refresh==1 and fetchtitle==1:
							result+=date+"\n"
						result+=t+"\n"
						refresh=0
				a=f.readline()
		if file=="./1.md":
			os.remove("./1.md")

		try:
			textbox.insert(tk.END,remove_emoji(result))
		except:
			pass
	
	def extraction_in_title(key,file=diary_file_path):
		log.insert(tk.END,"抽取选集：%s\n"%key)
		log.see(tk.END)
		if len(key)>1:
			log.insert(tk.END,"丑瓜娃子，你在逗我吗？\n")
			log.see(tk.END)
			return


		try:
			key=key[0].strip("-")
		except:
			pass


		if file==diary_file_path:
			s=decrypting(0,diary_file_path)
			#找一下选定的title是第几个，万一有title重复了，选出来存在m里面
			m=-1
			for i in range(listbox_right.size()):
				if i>int(right_listbox_index):
					break
				if listbox_right.get(i).strip("-")==key:
					m+=1
		else:#这里还要给抽取temp文件的title用
			with open(file,"r",encoding="utf-8") as f:
				s=f.read()
			#找一下选定的title是第几个，万一有title重复了，选出来存在m里面
			m=-1
			for i in range(listbox_left.size()):
				if i>int(left_listbox_index):
					break
				if listbox_left.get(i).strip("-")==key:
					m+=1

		#利用下标m，选出层级不大于选中标题的部分
		index=[i.start() for i in re.finditer(key,s)][m]
		s=s[index:].split("\n")
		mini=key.count("#")
		b=""
		flag=0
		for i in s:
			a=re.findall("^#+",i)
			if a==[]:
				b+=i+"\n"
				continue
			if flag==0:
				b+=i+"\n"
				flag=1
				continue
			if len(a[0])>mini:
				b+=i+"\n"
				continue
			if len(a[0])<=mini:
				break

		textbox.insert(tk.END,remove_emoji(b))

	def extraction_in_tree(key,file=diary_file_path):
		if key!=[]:#如果传进来空集，会抓出来全部的文件目录……
			log.insert(tk.END,"抽取树选集：%s\n"%key)
			log.see(tk.END)
			try:
				s=map(lambda x:x.name,tree_toptodown(key[0].strip("-")[1:]))
			except:#上面找项时出现重复项
				return
			if file==diary_file_path:
				(l,ll)=findtag(file)
			else:
				(l,ll)=findtag(file,1)
			l=list(l.keys())
			findout=[]
			for j in s:
				if j in l:
					findout.append(j)
			extraction_in_tags(findout,1,file)


	global right_listing_from,showned_text,extract_right_from,output_selection_file_name_head,output_selection_file_name_tail,old_diary_text,left_previous_title,left_current_title,left_listing_from,right_listbox_index,left_listbox_index
	if leftlist==1:#这个是点左边的listbox的抽取选集
		left_previous_title=left_current_title#记录之前看过的一个title
		left_current_title=key#更新现在的title
		if extract_right_from=="title":#只有来自右边title的选集才能参与和手账相关联的保存和替换。每切换一次查看的标题，就保存一下之前一个页面的操作||如果真的要编辑的话，可以用覆盖保存按钮
			if left_listing_from=="title":#同理，只有来自左边title的选集才能参与和手账相关联的保存和替换||如果真的要编辑的话，可以用覆盖保存按钮
				left_listbox_index=str(int(listbox_left.index(tk.ACTIVE)))
				save_temp_file("editing")
				textbox.delete("1.0",tk.END)
				extraction_in_title(key,file="./%s"%tempfile_name)
				textbox_count_word_number(0)
				showned_text=textbox.get("1.0",tk.END)
				output_selection_file_name_tail="%s"%fix_output_file_name("".join(key))
			if left_listing_from=="tag":
				left_listbox_index=str(int(listbox_left.index(tk.ACTIVE)))
				textbox.delete("1.0",tk.END)
				extraction_in_tags(key,file="./%s"%tempfile_name)
				textbox_count_word_number(0)
				output_selection_file_name_tail="%s"%fix_output_file_name("".join(key))
			# if left_listing_from=="tree":
			# 	index=str(int(listbox_left.index(tk.ACTIVE)))
			# 	textbox.delete("1.0",tk.END)
			# 	extraction_in_tree(key,file="./%s"%tempfile_name)
			# 	textbox_count_word_number(0)
			# 	output_selection_file_name_tail="%s"%fix_output_file_name("".join(key))
			# 	listbox_left.see(index)
		else:#其他两个就只能抽取出来或转成epub看看，不记录showned_text，编辑了也不会保存的，
			if left_listing_from=="title":
				left_listbox_index=str(int(listbox_left.index(tk.ACTIVE)))
				textbox.delete("1.0",tk.END)
				extraction_in_title(key,file="./%s"%tempfile_name)
				textbox_count_word_number(0)
				output_selection_file_name_tail="%s"%fix_output_file_name("".join(key))
			if left_listing_from=="tag":
				left_listbox_index=str(int(listbox_left.index(tk.ACTIVE)))
				textbox.delete("1.0",tk.END)
				extraction_in_tags(key,file="./%s"%tempfile_name)
				textbox_count_word_number(0)
				output_selection_file_name_tail="%s"%fix_output_file_name("".join(key))
			# if left_listing_from=="tree":
			# 	index=str(int(listbox_left.index(tk.ACTIVE)))
			# 	textbox.delete("1.0",tk.END)
			# 	extraction_in_tree(key,file="./%s"%tempfile_name)
			# 	textbox_count_word_number(0)
			# 	output_selection_file_name_tail="%s"%fix_output_file_name("".join(key))
			# 	listbox_left.see(index)
	else:#点右边进行选集
		left_previous_title=[]
		left_current_title=[]
		if right_listing_from=="tag":
			right_listbox_index=str(int(listbox_right.index(tk.ACTIVE)))
			textbox.delete("1.0",tk.END)
			extraction_in_tags(key)
			textbox_count_word_number(0)
			extract_right_from="tag"
			output_selection_file_name_head="%s_%s_"%(extract_right_from.capitalize(),fix_output_file_name("".join(key)))
			output_selection_file_name_tail="All"
			save_temp_file("creating")#如果你点了右边的选集，那就给你建一个temp，并在左边展示标题层级
		elif right_listing_from=="title":
			right_listbox_index=str(int(listbox_right.index(tk.ACTIVE)))
			textbox.delete("1.0",tk.END)
			extraction_in_title(key)
			textbox_count_word_number(0)
			extract_right_from="title"
			output_selection_file_name_head="%s_%s_"%(extract_right_from.capitalize(),fix_output_file_name("".join(key)))
			output_selection_file_name_tail="All"
			old_diary_text=textbox.get("1.0",tk.END)#只有title出来时才记录手账原型，才能回去替换手账
			showned_text=textbox.get("1.0",tk.END)#只有title出来时才保存temp，才记录替换前的text！
			save_temp_file("creating")#如果你点了右边的选集，那就给你建一个temp，并在左边展示标题层级，
		# elif right_listing_from=="tree":
		# 	textbox.delete("1.0",tk.END)
		# 	extraction_in_tree(key)
		# 	textbox_count_word_number(0)
		# 	extract_right_from="tree"
		# 	output_selection_file_name_head="%s_%s_"%(extract_right_from.capitalize(),fix_output_file_name("".join(key)))#淦，这里的反斜杠又影响保存文件了
		# 	output_selection_file_name_tail="All"
		# 	save_temp_file("creating")#如果你点了右边的选集，那就给你建一个temp，并在左边展示标题层级
	textbox_automatically_add_style(1)

def go_to_the_previous_page():
	if left_previous_title!=[]:
		extractselection(0,left_previous_title,1)
		textbox_count_word_number(0)






# def searchtag(event):#后来用了searchtag_whiletyping，这个就没用了
# 	global allrightlist
# 	key=entry_search.get().lower()
# 	listbox_right.delete(0,listbox_right.size())
# 	for i in allrightlist.keys():
# 		if key in allrightlist[i]:
# 			listbox_right.insert(tk.END,i)

def search_rightlist_whiletyping(key):
	if key==0:
		key=entry_right_search.get()
	global allrightlist
	listbox_right.delete(0,listbox_right.size())
	if key!="":
		for i in allrightlist:
			#同时满足正则搜索和英文简写搜索（可指定首尾）
			origin=i[0]
			translate=i[1]
			try:
				if re.findall(key,origin)!=[]:#正则搜搜看，如果打字时出现正则表达式错误它会报错的，所以放在try里
					listbox_right.insert(tk.END,(origin.count("#")-1)*"-"+origin.count("	")*"-"+origin.strip())
					continue#找到了就不用再搜了
				if key in translate:#正则找不到，再用自己的搜索
					listbox_right.insert(tk.END,(origin.count("#")-1)*"-"+origin.count("	")*"-"+origin.strip())
			except:#防止正则表达式出错，用自己的搜索
				if key in translate:
					listbox_right.insert(tk.END,(origin.count("#")-1)*"-"+origin.count("	")*"-"+origin.strip())
	else:
		for i in allrightlist:
			listbox_right.insert(tk.END,(i[0].count("#")-1)*"-"+i[0].count("	")*"-"+i[0].strip())
	listbox_right.see(right_listbox_index)

def search_leftlist_whiletyping(key):
	if key==0:
		key=entry_left_search.get()
	global allleftlist
	listbox_left.delete(0,listbox_left.size())
	if key!="":
		for i in allleftlist:
			#同时满足正则搜索和英文简写搜索（可指定首尾）
			origin=i[0]
			translate=i[1]
			try:
				if re.findall(key,origin)!=[]:#正则搜搜看，如果打字时出现正则表达式错误它会报错的，所以放在try里
					listbox_left.insert(tk.END,(origin.count("#")-1)*"-"+origin.count("	")*"-"+origin.strip())
					continue#找到了就不用再搜了
				if key in translate:#正则找不到，再用自己的搜索
					listbox_left.insert(tk.END,(origin.count("#")-1)*"-"+origin.count("	")*"-"+origin.strip())
			except:#防止正则表达式出错，用自己的搜索
				if key in translate:
					listbox_left.insert(tk.END,(origin.count("#")-1)*"-"+origin.count("	")*"-"+origin.strip())
	else:
		for i in allleftlist:
			listbox_left.insert(tk.END,(i[0].count("#")-1)*"-"+i[0].count("	")*"-"+i[0].strip())
	listbox_left.see(left_listbox_index)





def output_file(file=0,md=0):
	def deep_converse_md_to_epub(dir,base):
		list = os.listdir(dir)#dir是根路径
		for i in list:
			path = os.path.join(dir, i)#path是根路径下的文件路径
			if os.path.isdir(path):
				deep_converse_md_to_epub(path,base)
			else:
				if i[-3:]==".md":
					log.insert(tk.END,"找到md文件："+path+"\n")
					log.see(tk.END)
					os.chdir(dir)#必须在这里切换工作路径
					os.system("pandoc %s.md -o %s.epub"%(i[0:-3],i[0:-3]))
					shutil.move(i[0:-3]+".epub",base+"\\output_file")
					log.insert(tk.END,"已输出epub文件："+base+"\\output_file\\"+i[0:-3]+".epub"+"\n")
					log.see(tk.END)

	global base
	log.insert(tk.END,"开始md转epub\n")
	log.see(tk.END)
	os.system("chcp 65001")

	if md==0:#只输出epub
		if file==0:#输出全体
			deep_converse_md_to_epub(base+"/文",base)#传进去的是绝对路径
		if file==-1:#输出当前页面
			os.rename("%s"%tempfile_name,"1.md")#哈哈哈调虎离山之计
			save_temp_file("creating",1)
			newname=what_name_is_the_output_file()+".md"
			os.system("pandoc %s -o %s.epub"%("%s"%tempfile_name,newname[0:-3]))
			shutil.move(newname[0:-3]+".epub","./output_file")
			os.remove("%s"%tempfile_name)
			os.rename("1.md","%s"%tempfile_name)
			log.insert(tk.END,"已输出epub文件："+base+"\\output_file\\"+newname[0:-3]+".epub"+"\n")
			log.see(tk.END)
		else:#输出单文件
			if file=="%s"%tempfile_name:#输出选集全集
				newname=output_selection_file_name_head+"All"+".md"
				os.chdir("./")
			else:#输出手账
				newname=file
				os.chdir("%s"%diary_folder_path)
			os.system("pandoc %s -o %s.epub"%(file,newname[0:-3]))
			shutil.move(newname[0:-3]+".epub","./output_file")
			log.insert(tk.END,"已输出epub文件："+base+"\\output_file\\"+newname[0:-3]+".epub"+"\n")
			log.see(tk.END)
	else:#只输出md，也就只有选集可能会要这样
		if file==-1:#输出当前页面
			os.rename("%s"%tempfile_name,"1.md")#哈哈哈调虎离山之计
			save_temp_file("creating",1)
			shutil.move("./%s"%tempfile_name,"./output_file/%s.md"%what_name_is_the_output_file())
			os.rename("1.md","%s"%tempfile_name)
			log.insert(tk.END,"已输出md文件："+base+"\\output_file\\"+what_name_is_the_output_file()+".md"+"\n")
			log.see(tk.END)
		else:#输出选集全集
			shutil.copy("./%s"%tempfile_name,"./output_file/%s.md"%(output_selection_file_name_head+"All"))
			log.insert(tk.END,"已输出md文件："+base+"\\output_file\\"+output_selection_file_name_head+"All"+".md"+"\n")
			log.see(tk.END)
	os.chdir(base)#切换回来

def fixchat1():
	log.insert(tk.END,"开始修正聊天记录\n")
	log.see(tk.END)
	line="a"
	with open("./聊天记录工作区.md","r",encoding="utf-8") as scr,open("./1.md","w",encoding="utf-8") as dst:
		while line!="":
			line=scr.readline()
			if line[0:4]=='> | ' and line[-3:]==' |\n':
				if line.count("-")>10:
					continue
				line=re.sub("(?<=\[img\]\()img","E:/堆/20三侠客的那些年/三侠客群聊天记录/img",line)#图片地址修正
				line='> '+line[4:-2].strip()+"\n> \n"#修正每一行聊天
				log.insert(tk.END,line+"\n")
				log.see(tk.END)
			dst.write(line)
	os.remove("聊天记录工作区.md")
	os.rename("1.md","聊天记录工作区.md")
	log.insert(tk.END,"已修正聊天记录，请继续操作typora复制图片到选集文件夹，再进行第二步修正。\n")
	log.see(tk.END)

def fixchat2():
	with open("./聊天记录工作区.md","r",encoding="utf-8") as scr,open("./1.md","w",encoding="utf-8") as dst:
		line="a"
		while line!="":
			line=scr.readline()
			line=re.sub("/三侠客群聊天记录/img","/三侠客群聊天记录/选集图片",line)#图片地址修正
			log.insert(tk.END,line+"\n")
			log.see(tk.END)
			dst.write(line)
	os.remove("聊天记录工作区.md")
	os.rename("1.md","聊天记录工作区.md")
	log.insert(tk.END,"聊天记录图片链接修正完成。\n")
	log.see(tk.END)

def changerank():
	log.insert(tk.END,"标题级数转换\n")
	log.see(tk.END)
	old=textbox.get("1.0",tk.END)
	text1=textbox.selection_get()
	text=textbox.selection_get()
	newtext=""
	try:
		text=text.split("\n")
		x=int(entry_input.get())
		for i in text:
			if re.findall("^#*",i)==['']:
				newtext+=i+"\n"
			else:
				if i.count("#")-x<1 or i.count("#")-x>6:
					log.insert(tk.END,"级数越界！！")
					log.see(tk.END)
					return
				else:
					newtext+=re.sub("^#*","#"*(i.count("#")-x),i)+"\n"
	except:
		pass
	log.insert(tk.END,"已替换：%s个内容\n"%old.count(text1))
	log.see(tk.END)
	old=old.replace(text1,newtext.strip()).strip()
	textbox.delete('1.0', tk.END)
	textbox.insert(tk.END,remove_emoji(old))

def analysefrequency():
	log.insert(tk.END,"手账词频分析\n")
	log.see(tk.END)
	textbox.delete("1.0",tk.END)
	txt=decrypting(0,diary_file_path)

	punc=string.punctuation#不要分析的字符
	punc+=" \n。，？（）、；：‘’“”！《》	"
	dont=["span","tag"]#不要分析的字符
	jieba.add_word('珊')#添加词汇
	wordsls=jieba.lcut(txt)
	wcdict={}
	for word in wordsls:
		wcdict[word]=wcdict.get(word,0)+1
	a=sorted(wcdict.items(),key=lambda x:x[1],reverse=True)
	for i in range(len(a)):
		if a[i][0].isdigit()==False and a[i][0] not in punc and a[i][0] not in dont:
			try:
				textbox.insert(tk.END,"%s    %s\n"%(a[i][0],a[i][1]))
			except:
				pass

def analyse_tag():
	(l,ll)=findtag(diary_file_path)
	l=sorted(l.items(),key=lambda x:x[1],reverse=1)
	textbox.delete("1.0",tk.END)
	for i in l:
		textbox.insert(tk.END,"%8s				%s\n"%(i[1],i[0]))

def backup():
	if dobackup==1:
		global backup_dst
		base=os.getcwd()
		if window_title=="茶屋工作台":
			dst="F:/data.dlcw"
			try:
				shutil.rmtree(dst)
				shutil.copyfile("%s"%diary_file_path,dst)
			except:
				try:
					shutil.copyfile("%s"%diary_file_path,dst)#若文件夹已经被删除
				except:
					pass

			t=what_day_is_it()
			dst=r"E:\堆\20茶屋的那些年\茶屋工作台\手账\2020.10.10 茶屋工作台三代加密"
			try:
				os.chdir(dst)#探测是否存在目录
				try:#目录存在，尝试复制
					os.chdir(base)#还要记得切换回来
					dst=dst+"\\data"+t+".dlcw"
					shutil.copyfile("%s"%diary_file_path,dst)
					log.insert(tk.END,"E盘文历史节点已备份\n")
					log.see(tk.END)
				except:#无法复制，因为同名文件夹存在
					shutil.rmtree(dst)
					shutil.copyfile("%s"%diary_file_path,dst)
					log.insert(tk.END,"E盘文历史节点已再次备份\n")
					log.see(tk.END)
			except:
				log.insert(tk.END,"您没插硬盘吧\n")
				log.see(tk.END)
		for dst in backup_dst:
			try:
				shutil.rmtree(dst)
				shutil.copyfile("%s"%diary_file_path,dst)
				log.insert(tk.END,"%s已备份\n"%dst)
				log.see(tk.END)
			except:
				try:
					shutil.copyfile("%s"%diary_file_path,dst)#若文件夹已经被删除
					log.insert(tk.END,"%s已备份\n"%dst)
					log.see(tk.END)
				except:
					log.insert(tk.END,"%s备份未成功\n"%dst)
					log.see(tk.END)
		os.chdir(base)
		log.insert(tk.END,"DONE!\n")
		log.see(tk.END)
	else:
		pass

def adddate():
	def weekday(y,m,d):
		dic=["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]
		return dic[calendar.weekday(y,m,d)]

	line='a'
	decrypting(0,diary_file_path,"./0.md")
	with open("./0.md","r",encoding="utf-8") as scr,open("./1.md","w",encoding="utf-8") as dst:
		while line!="":
			line=scr.readline()
			if line[:3]=="###" and line[4]=="2" and ascii(line[-2])<=ascii("9") and ascii(line[-2])>=ascii("0") and len(line[4:].split("."))==3 and line.find(":")==-1:
				# log.insert(tk.END,line,line[-2])
				log.see(tk.END)
				(y,m,d)=line[4:].split(".")
				line=line[:-1]+weekday(int(y),int(m),int(d))+"\n"
				log.insert(tk.END,"日期修正："+line+"\n")
				log.see(tk.END)
				dst.write(line)
			else:dst.write(line)
	encrypting(0,"./1.md",diary_file_path)
	os.remove("./0.md")
	os.remove("./1.md")
	log.insert(tk.END,"日期修正完成！建议重新导入手账。\n")
	log.see(tk.END)
	if right_listing_from=="title":
		listrighttitle()



# def taggetup(event):#现在listbox可以多选了，这个就不用了
# 	tag=listbox_right.get(listbox_right.curselection())
# 	textbox.insert(tk.END,tag+"||")



def add_tag(event,in_file,trans_to_html):
	def correct_to_html(a):#html标签修正，**为<b>，~~为<s>,*改为<i>
		def cor(a,b):
			if b=="***":
				b="\*\*\*"
				c=["<b><i>","</b></i>"]
			elif b=="**":
				b="\*\*"
				c=["<b>","</b>"]
			elif b=="*":
				b="\*"
				c=["<i>","</i>"]
			elif b=="~~":
				c=["<del>","</del>"]
			pattern=re.findall("(?<=%s).*?(?=%s)"%(b,b),a)
			result=a
			for i in pattern:
				result=re.sub("%s.*?%s"%(b,b),"%s%s%s"%(c[0],i,c[1]),result,1)
			return result
		a=cor(a,"***")
		a=cor(a,"**")
		a=cor(a,"*")
		a=cor(a,"~~")
		return a

	def eachline(f,fo,trans_to_html,tag,a):
		if a=="":#防止在文档末尾？？？忘了是啥
			log.insert(tk.END,"格式录入："+a+"\n")
			log.see(tk.END)
			fo.write(a)
			a=f.readline()
			return a
		already=re.findall("(?<=tag=\").*?(?=\")",a)
		if already!=[]:#如果是标签添加到已有的<span tag="">格式中
			s1=""
			s2=""
			try:
				s1=re.findall("(?<=[\d-] ).*",a)[0]
				while True:
					s2=s1
					try:
						s1=re.findall("(?<=[\d-] ).*",s1)[0]
					except:
						break
			except:
				pass
			#找出的s2是无序列表或有序列表前缀之后的部分，到后面判断开头是否有<span
			if a[:5]=="<span" or s2[:5]=="<span":#刚好整一段都被包裹了，添加不与之重复的
				l=re.split("(?<=\")>",a,1)#只分离第一个span，因为要添加在最外层
				b=l[0]
				for i in tag:
					if i not in already:
						log.insert(tk.END,"已添加Tag：%s\n"%i)
						log.see(tk.END)
						b+=" tag=\"%s\""%i
				b+=">"+l[1]
				log.insert(tk.END,"格式录入："+b+"\n")
				log.see(tk.END)
				fo.write(b)
				a=f.readline()
				return a
			else:#只是里面有tag了，应该把不与之重复的裹在外面
				b="<span"
				for i in tag:
					if i not in already:
						log.insert(tk.END,"已添加Tag：%s\n"%i)
						log.see(tk.END)
						b+=" tag=\"%s\""%i
				b+=">"+a+"</span>"
				log.insert(tk.END,"格式录入："+b+"\n")
				log.see(tk.END)
				fo.write(b)
				a=f.readline()
				return a
		else:#如果是新建标签
			if a!="\n" and a[0]!="#" and re.match("-*?$",a)==None:#不是换行、标题、分割线
				if a[0]==">":#引用
					if re.match("(> )*$",a.strip()+" "):#引用中的换行要特殊操作
						b=a
					else:
						if re.findall("!\[.*\]\(.*\)",a)!=[]:#引用中一行链接
							b=re.findall(".*(?=\]\()",a)[0]#> ![xxxx这部分
							for i in tag:
								b+=" tag=\"%s\""%i# tag=""这部分
							b+="]("+re.findall("(?<=\]\().*",a)[0]+"\n"#](link)这部分
						else:
							b=re.match("(> )*",a).group()+"<span"
							for i in tag:
								b+=" tag=\"%s\""%i
							if trans_to_html==1:
								b+=">"+correct_to_html(re.sub("> ","",a.replace("\n","")))+"</span>"+"\n"
							else:
								b+=">"+re.sub("> ","",a.replace("\n",""))+"</span>"+"\n"
				elif a[0]=="!":#图片链接
					b=re.findall(".*(?=\]\()",a)[0]#![xxxx这部分
					for i in tag:
						b+=" tag=\"%s\""%i# tag=""这部分
					b+="]("+re.findall("(?<=\]\().*",a)[0]+"\n"#](link)这部分
				elif a[1:3]==". ":#数字列表
					b=a[0:3]+"<span"
					for i in tag:
						b+=" tag=\"%s\""%i
					if trans_to_html==1:
						b+=">"+correct_to_html(a[2:].replace("\n",""))+"</span>"+"\n"
					else:
						b+=">"+a[2:-1]+"</span>"+"\n"
				elif a.strip()[0:2]=="- ":#方块列表
					b=re.findall(".*?(?=- )",a)[0]+"- "+"<span"
					for i in tag:
						b+=" tag=\"%s\""%i
					if trans_to_html==1:
						b+=">"+correct_to_html(re.findall("(?<=- ).*",a)[0])+"</span>"+"\n"
					else:
						b+=">"+re.findall("(?<=- ).*",a)[0]+"</span>"+"\n"
				else:#普通段落
					b="<span"
					for i in tag:
						b+=" tag=\"%s\""%i
					if trans_to_html==1:
						b+=">"+correct_to_html(a.replace("\n",""))+"</span>"+"\n"
					else:
						b+=">"+a.replace("\n","")+"</span>"+"\n"
				log.insert(tk.END,"格式录入："+b+"\n")
				log.see(tk.END)
				fo.write(b)
				a=f.readline()
				return a
			else:#换行、标题、分割线照搬
				log.insert(tk.END,"格式录入："+a+"\n")
				log.see(tk.END)
				fo.write(a)
				a=f.readline()
				return a
	def trans(f,fo,trans_to_html,in_file):#懒得重编不用文件的了，凑合弄个文件操作，也能用
		a=f.readline()
		while a!="":
			if in_file==1:#录入文件内的<>/格式标签
				tag=re.findall('(?<=^<).*?(?=>/)',a)#读入tag字符串，这里还是一个只有一元的列表
				if tag!=[]:#遇见tag区块的开头
					a=f.readline()
					a=f.readline()
					tag=tag[0].split()#多重tag作分离
					while a!="/\n":#在区块结束之前
						a=eachline(f,fo,trans_to_html,tag,a)
					a=f.readline()#跳出tag区块
					a=f.readline()
				else:#没有tag区块
					fo.write(a)
					a=f.readline()
			else:#在界面上的加标签
				a=eachline(f,fo,trans_to_html,[entry_input.get()],a)


	if in_file==0:#编辑页面上的文本
		selected=textbox.selection_get()
		origin=textbox.get("1.0",tk.END)
		index=origin.find(selected)
		row=origin[:index].count("\n")#计算修改的位置，便于下面滚动
		column=row
		row+=1
		for i in range(len(origin)):
			if origin[i]=="\n":
				column-=1
			if column==0:
				column=i
				break
		column=index-column+10
		with open("./temp_trans_format.md","w",encoding="utf-8") as f:
			f.write(selected)
		with open("./temp_trans_format.md","r",encoding="utf-8") as f,open("./1.md","w",encoding="utf-8") as fo:
			trans(f,fo,0,0)
		os.remove("temp_trans_format.md")
		os.rename("1.md","temp_trans_format.md")
		with open("./temp_trans_format.md","r",encoding="utf-8") as f:
			replace=f.read().strip()#这里好像就把多出来的换行删掉了
			after=origin.replace(selected,replace).strip()#这里很不严谨，如果可以的话侦测记录前后的光标位置，但我的日记tag内容是一大段的，不太可能重复
			n=origin.count(selected)
			if n>1:
				log.insert(tk.END,"保存出错，手账替换出现%s个重复内容如下：\n"%n)
				log.insert(tk.END,"要替换的内容为%s\n"%selected)
				return
			log.insert(tk.END,"已替换：%s个内容\n"%n)
			log.see(tk.END)
			textbox.delete("1.0",tk.END)
			textbox.insert(tk.END,remove_emoji(after))
			textbox_count_word_number(0)
			showned_text=textbox.get("1.0",tk.END)
		os.remove("temp_trans_format.md")

	#、、、、、、、、、、、、 else:#编辑手账文件内的文本、、、、、、、、、、、、、、、、、、、、、、、、、、、、、、、、、、、、这里不会用到了
	#、、、、、、、、、、、、 	decrypting(0,diary_file_path,"0.md")
	#、、、、、、、、、、、、 	with open("0.md","r",encoding="utf-8") as f,open("1.md","w",encoding="utf-8") as fo:
	#、、、、、、、、、、、、 		trans(f,fo,trans_to_html,1)
	#、、、、、、、、、、、、 		log.insert(tk.END,"文件录入完成")
	#、、、、、、、、、、、、 		log.see(tk.END)
	#、、、、、、、、、、、、 	encrypting(0,"1.md",diary_file_path)
	#、、、、、、、、、、、、 	os.remove("0.md")
	#、、、、、、、、、、、、 	os.remove("1.md")

	textbox_automatically_add_style(1)
	textbox.see("%s.%s"%(row,column))#这里在替换后自动滚到修改过的地方
	textbox.mark_set("insert","%s.%s"%(row,column))#改变光标位置，帮你指到引号内

def remove_tag_in_textbox():
	selected=textbox.selection_get()
	origin=textbox.get("1.0",tk.END)
	index=origin.find(selected)
	index=origin[:index].count("\n")#计算修改的位置，便于下面滚动

	after=re.sub("<.*?>","",selected)
	log.insert(tk.END,"已替换：%s个内容\n"%origin.count(selected))
	log.see(tk.END)
	after=origin.replace(selected,after)
	textbox.delete("1.0",tk.END)
	textbox.insert(tk.END,remove_emoji(after))
	textbox_count_word_number(0)
	textbox_automatically_add_style(1)
	textbox.see("%s.0"%index)#这里在替换后自动滚到修改过的地方

def delete_tag_in_file():
	global right_listing_from
	if right_listing_from=="tag":
		tag=listbox_right.get(tk.ACTIVE).strip("*").strip("-").strip("\\")
		s=decrypting(0,diary_file_path)
		log.insert(tk.END,"已替换：%s个内容\n"%s.count(' tag="%s"'%tag))
		log.see(tk.END)
		s=s.replace(' tag="%s"'%tag,"")
		diary_count_word_number(s)
		encrypting(s,0,diary_file_path)
		log.insert(tk.END,"已删除手账中的Tag：%s\n"%tag)
		log.see(tk.END)
		listrighttag()

def change_tag_in_file():
	global right_listing_from
	if right_listing_from=="tag":
		oldtag=listbox_right.get(tk.ACTIVE).strip("*").strip("-").strip("\\")
		newtag=entry_input.get()
		s=decrypting(0,diary_file_path)
		log.insert(tk.END,"已替换：%s个内容\n"%len(re.findall('(?<= tag=")%s(?=")'%oldtag,s)))
		log.see(tk.END)
		s=re.sub('(?<= tag=")%s(?=")'%oldtag,newtag,s)
		diary_count_word_number(s)
		log.insert(tk.END,"已将手账中的%s标签改为%s\n"%(oldtag,newtag))
		log.see(tk.END)
		encrypting(s,0,diary_file_path)
		listrighttag()

def delete_tag_in_tempfile():
	global left_listing_from
	if left_listing_from=="tag":
		tag=listbox_left.get(tk.ACTIVE).strip("*").strip("-").strip("\\")
		with open("./%s"%tempfile_name,"r",encoding="utf-8") as f ,open("./1.md","w",encoding="utf-8") as fo:
			s=f.read()
			log.insert(tk.END,"已替换：%s个内容\n"%s.count(' tag="%s"'%tag))
			log.see(tk.END)
			s=s.replace(' tag="%s"'%tag,"")
			tempfile_count_word_number(s)
			fo.write(s)
		os.remove("./%s"%tempfile_name)
		os.rename("./1.md","./%s"%tempfile_name)
		log.insert(tk.END,"已删除temp中的Tag：%s\n"%tag)
		log.see(tk.END)
		listlefttag()

def change_tag_in_tempfile():
	global left_listing_from
	if left_listing_from=="tag":
		oldtag=listbox_left.get(tk.ACTIVE).strip("*").strip("-").strip("\\")
		newtag=entry_input.get()
		with open("./%s"%tempfile_name,"r",encoding="utf-8") as f ,open("./1.md","w",encoding="utf-8") as fo:
			s=f.read()
			log.insert(tk.END,"已替换：%s个内容\n"%len(re.findall('(?<= tag=")%s(?=")'%oldtag,s)))
			log.see(tk.END)
			s=re.sub('(?<= tag=")%s(?=")'%oldtag,newtag,s)
			tempfile_count_word_number(s)
			fo.write(s)
		os.remove("./%s"%tempfile_name)
		os.rename("./1.md","./%s"%tempfile_name)
		log.insert(tk.END,"已将temp中的%s标签改为%s\n"%(oldtag,newtag))
		log.see(tk.END)
		listlefttag()

class FullScreenApp(object):
	def __init__(self, master, **kwargs):
		self.root = master
		# self.tk.attributes('-zoomed', True)  # This just maximizes it so we can see the window. It's nothing to do with fullscreen.
		self.frame = tk.Frame(self.root)
		self.frame.pack()
		self.state = False
		self.root.bind("<F11>", self.toggle_fullscreen)
		self.root.bind("<Escape>", self.end_fullscreen)

	def toggle_fullscreen(self, event=None):
		self.state = not self.state  # Just toggling the boolean
		self.root.attributes("-fullscreen", self.state)
		return "break"

	def end_fullscreen(self, event=None):
		self.state = False
		self.root.attributes("-fullscreen", False)
		return "break"


def elude(event,which_story):

	global dobackup,encrypt_key,diary_file_path,old_diary_text,extract_right_from,password
	global elude_backup_temp_file,elude_backup_encrypt_key,elude_backup_diary_file_path,elude_backup_old_diary_text,elude_backup_right_listing_from,elude_backup_extract_right_from
	if dobackup==1:#只有在手账处才能激活回避界面

		if extract_right_from=="title":
			save_temp_file("editing")
			with open(tempfile_name,"r",encoding="utf-8") as f:
				elude_backup_temp_file=f.read()
		else:
			elude_backup_temp_file=textbox.get("1.0",tk.END)
			
		elude_backup_old_diary_text=old_diary_text
		elude_backup_encrypt_key=encrypt_key
		elude_backup_diary_file_path=diary_file_path
		elude_backup_right_listing_from=right_listing_from
		elude_backup_extract_right_from=extract_right_from

		dobackup=0
		password="Confused_Initialize"
		encrypt_key=generate_encrypt_key(password)
		extract_right_from="title"

		textbox.delete("1.0",tk.END)
		listbox_left.delete(0,listbox_left.size())
		if which_story=="Tereo":
			diary_file_path="./data/data2.dlcw"
		elif which_story=="Miss Alice":
			diary_file_path="./data/data3.dlcw"
		elif which_story=="Radzig":
			diary_file_path="./data/data4.dlcw"
		elif which_story=="追忆似水年华":
			diary_file_path="./data/data0.dlcw"
		diary_folder_path="".join(map(lambda x:x+"/",diary_file_path.split("/")[:-1]))[:-1]
		#、、、反应太慢了，这个就算了 readin_entire_diary()
		listrighttitle()

def cancel_elude(event):
	global dobackup,encrypt_key,diary_file_path,old_diary_text,right_listing_from,extract_right_from
	if dobackup==0:
		diary_file_path=elude_backup_diary_file_path
		encrypt_key=elude_backup_encrypt_key
		old_diary_text=elude_backup_old_diary_text
		dobackup=1
		right_listing_from=elude_backup_right_listing_from
		extract_right_from=elude_backup_extract_right_from
		
		if right_listing_from=="title":
			listrighttitle()
		elif right_listing_from=="tag":
			listrighttag()
		elif right_listing_from=="tree":
			listrighttree()

		with open(tempfile_name,"w",encoding="utf-8") as f:
			f.write(elude_backup_temp_file)
		tempfile_count_word_number(elude_backup_temp_file)
		textbox_count_word_number(1)
		show_current_file()

def random_text():
	global updated,updated_text
	if updated==1:
		updated_text=decrypting(0,diary_file_path)
		updated_text=updated_text.split("\n")
		updated=0

	textbox.delete("1.0",tk.END)
	t=0
	while t<10 or t>len(updated_text)-10:
		t=int(random.random()*len(updated_text))
	textbox.insert("1.0","".join(map(lambda x:x+"\n",updated_text[t-8:t+8])))
	textbox_count_word_number(1)
	textbox_automatically_add_style(1)
	return



"""
普通函数传参lambda :func(x)
控件绑定事件，函数(event,x,y)，控件.bind("<事件>",lambda event: 函数(event,x,y))
文本中的光标颜色样式insertbackground='white'
from tkinter import scrolledtext，scrolledtext.ScrolledText直接带有滚动条
Text.see(tk.END)可以到底部

又是这丫re库，凭什么不支持(? = ^xxx)开头匹配？还有你丫的[\s\S]和匹配\\冲突？？？
你丫tkinter的Listbox连制表符都不能打
#tkinter不支持显示高于\uFFFF的字符，所以有一些高于markdown支持的emoji版本的emoji就很讨厌了，尽量用markdown的:xxx:表情吧
又一丫的re库的问题，multiple repeat，就是你传进去的文本里面有**，用用python自带的count和replace吧
pandoc的文件名还不能带空格……人家是跑命令行的………

最后悔的是整个系统内所有的层级符用了反斜杠。
弄巧成拙的替换replace或re.sub操作前都要在log中输出count的数目看一看有没有错
呵呵呵呵您连nonlocal都不会用
不会面对对象，都没法把界面布置做成initialize函数……
"""
def encryption_toolbox_page():
	def _load_tkdnd(master):
		tkdndlib = os.environ.get('TKDND_LIBRARY')
		if tkdndlib:
			master.tk.eval('global auto_path; lappend auto_path {%s}' % tkdndlib)
		master.tk.eval('package require tkdnd')
		master._tkdnd_loaded = True
	class TkDND(object):
		def __init__(self, master):
			if not getattr(master, '_tkdnd_loaded', False):
				_load_tkdnd(master)
			self.master = master
			self.tk = master.tk

		# Available pre-defined values for the 'dndtype' parameter:
		#   text/plain
		#   text/plain;charset=UTF-8
		#   text/uri-list

		def bindtarget(self, window, callback, dndtype, event='<Drop>', priority=50):
			cmd = self._prepare_tkdnd_func(callback)
			return self.tk.call('dnd', 'bindtarget', window, dndtype, event,
					cmd, priority)

		def bindtarget_query(self, window, dndtype=None, event='<Drop>'):
			return self.tk.call('dnd', 'bindtarget', window, dndtype, event)

		def cleartarget(self, window):
			self.tk.call('dnd', 'cleartarget', window)


		def bindsource(self, window, callback, dndtype, priority=50):
			cmd = self._prepare_tkdnd_func(callback)
			self.tk.call('dnd', 'bindsource', window, dndtype, cmd, priority)

		def bindsource_query(self, window, dndtype=None):
			return self.tk.call('dnd', 'bindsource', window, dndtype)

		def clearsource(self, window):
			self.tk.call('dnd', 'clearsource', window)


		def drag(self, window, actions=None, descriptions=None,
				cursorwin=None, callback=None):
			cmd = None
			if cursorwin is not None:
				if callback is not None:
					cmd = self._prepare_tkdnd_func(callback)
			self.tk.call('dnd', 'drag', window, actions, descriptions,
					cursorwin, cmd)


		_subst_format = ('%A', '%a', '%b', '%D', '%d', '%m', '%T',
				'%W', '%X', '%Y', '%x', '%y')
		_subst_format_str = " ".join(_subst_format)

		def _prepare_tkdnd_func(self, callback):
			funcid = self.master.register(callback, self._dndsubstitute)
			cmd = ('%s %s' % (funcid, self._subst_format_str))
			return cmd

		def _dndsubstitute(self, *args):
			if len(args) != len(self._subst_format):
				return args

			def try_int(x):
				x = str(x)
				try:
					return int(x)
				except ValueError:
					return x

			A, a, b, D, d, m, T, W, X, Y, x, y = args

			event = tk.Event()
			event.action = A       # Current action of the drag and drop operation.
			event.action_list = a  # Action list supported by the drag source.
			event.mouse_button = b # Mouse button pressed during the drag and drop.
			event.data = D         # The data that has been dropped.
			event.descr = d        # The list of descriptions.
			event.modifier = m     # The list of modifier keyboard keys pressed.
			event.dndtype = T
			event.widget = self.master.nametowidget(W)
			event.x_root = X       # Mouse pointer x coord, relative to the root win.
			event.y_root = Y
			event.x = x            # Mouse pointer x coord, relative to the widget.
			event.y = y

			event.action_list = str(event.action_list).split()
			for name in ('mouse_button', 'x', 'y', 'x_root', 'y_root'):
				setattr(event, name, try_int(getattr(event, name)))

			return (event, )
	def encryption_toolbox_encrypt(input_file):
		global password,encrypt_key
		password=entry_key.get()
		encrypt_key=generate_encrypt_key(password)
		with open(input_file,"r",encoding="utf-8") as f:
			origin=f.read()

		new=""
		n=0
		for i in origin:
			new+=encrypting_text(i,n)#异或优先级低于加减乘除……
			n+=1

		dst=os.path.dirname(input_file)
		with open("%s/encrypted_file.dlcw"%dst,"w",encoding="utf-8") as f:
			f.write(new)

		return
	def encryption_toolbox_decrypt(input_file):
		global password,encrypt_key
		password=entry_key.get()
		encrypt_key=generate_encrypt_key(password)
		with open(input_file,"r",encoding="utf-8") as f:
			origin=f.read()

		new=""
		n=0
		for i in origin:
			new+=decrypting_text(i,n)
			n+=1

		dst=os.path.dirname(input_file)
		with open("%s/decrypted_file"%dst,"w",encoding="utf-8") as f:
			f.write(new)

		return
	def encryption_toolbox_generate_key(file):
		global password
		with open(file,"r",encoding="utf-8") as f:
			s=f.read()
		s=s.split("\n")
		password=s[7].split("=")[-1]
		entry_key.delete(0,1)
		entry_key.insert(0,password)
	def handle(event):
		event.widget.delete(0,tk.END)
		event.widget.insert(0, event.data)
	window = tk.Tk()
	window.geometry("1000x500")
	dnd = TkDND(window)

	label_key=tk.Label(text="Password")
	label_key.place(y=0,x=0)
	entry_key=tk.Entry(window,show="*")
	entry_key.place(y=0,x=60,height=25,width=100)
	py=100
	px=150
	entry_user_setting=tk.Entry(window)
	entry_user_setting.place(y=py,x=px,height=30,width=600)
	dnd.bindtarget(entry_user_setting,handle,'text/uri-list')
	button_generate_key=tk.Button(window,text="Generate Key",command=lambda:encryption_toolbox_generate_key(entry_user_setting.get().strip("{").strip("}")))
	button_generate_key.place(y=py,x=px+600,height=30,width=100)


	py+=120
	entry_decrypted=tk.Entry(window)
	entry_decrypted.place(y=py,x=px,height=30,width=600)
	dnd.bindtarget(entry_decrypted,handle,'text/uri-list')
	button_encrpt=tk.Button(window,text="Encrypt",command=lambda:encryption_toolbox_encrypt(entry_decrypted.get().strip("{").strip("}")))
	button_encrpt.place(y=py,x=px+600,height=30,width=100)


	py+=120
	entry_encrypted=tk.Entry(window)
	entry_encrypted.place(y=py,x=px,height=30,width=600)
	dnd.bindtarget(entry_encrypted,handle,'text/uri-list')
	button_decrypt=tk.Button(window,text="Decrypt",command=lambda:encryption_toolbox_decrypt(entry_encrypted.get().strip("{").strip("}")))
	button_decrypt.place(y=py,x=px+600,height=30,width=100)


	window.mainloop()

def confused_initialize(which_story):
	global base,tempfile_name,dobackup
	global password,diary_file_path,encrypt_key
	base=os.getcwd()
	tempfile_name=what_name_is_the_tempfile()
	try:
		shutil.rmtree(base+"/output_file")
	except:
		pass
	os.mkdir("output_file")
	password="Confused_Initialize"#用这个密钥加密的三个混淆文档
	encrypt_key=generate_encrypt_key(password)
	if which_story=="Tereo":
		diary_file_path="./data/data2.dlcw"
	elif which_story=="Miss Alice":
		diary_file_path="./data/data3.dlcw"
	elif which_story=="Radzig":
		diary_file_path="./data/data4.dlcw"
	elif which_story=="追忆似水年华":
		diary_file_path="./data/data0.dlcw"
	diary_folder_path="".join(map(lambda x:x+"/",diary_file_path.split("/")[:-1]))[:-1]
	dobackup=0

def initialize():
	global base,tempfile_name,dobackup
	global window_size,fullscreen,fontfamily,diary_file_path,diary_folder_path,window_title,typora_location,sublime_location,backup_dst

	"初始化"
	base=os.getcwd()
	tempfile_name=what_name_is_the_tempfile()#确定temp文件的名字
	try:
		shutil.rmtree(base+"/output_file")
		#、、、这个是没保存一次就备份一下之前的快照，现在稳定点了就不用了 shutil.rmtree(base+"/autobackup")
		with open("%s/%s"%(base,tempfile_name),"w",encoding="utf-8") as f:
			pass
	except:
		with open("%s/%s"%(base,tempfile_name),"w",encoding="utf-8") as f:
			pass
	os.mkdir("output_file")
	#、、、这个是没保存一次就备份一下之前的快照，现在稳定点了就不用了 os.mkdir("autobackup")

	"读取user_setting"
	s=decrypting(0,"./user_setting")
	s=s.split("\n")
	window_size=float(s[0].split("=")[-1])#调节窗口大小比例
	fullscreen=s[1].split("=")[-1]
	fontfamily=s[2].split("=")[-1]
	diary_file_path=s[3].split("=")[-1]
	diary_folder_path="".join(map(lambda x:x+"/",diary_file_path.split("/")[:-1]))[:-1]
	window_title=s[4].split("=")[-1]
	typora_location=s[5].split("=")[-1]
	sublime_location=s[6].split("=")[-1]
	backup_dst=s[7].split("=")[-1].split(",")
	dobackup=1

	#、、、这个是没保存一次就备份一下之前的快照，现在稳定点了就不用了 shutil.copy(diary_file_path,"./autobackup/%s_%s"%(what_time_is_it(),diary_file_path.split("/")[-1]))


def main_page():
	global listbox_right,listbox_left,entry_left_search,entry_right_search,entry_input,textbox,log
	global number_of_word_in_diary,number_of_word_in_tempfile,label_number_of_word_in_diary,label_number_of_word_in_tempfile,number_of_word_in_textbox,label_number_of_word_in_textbox
	def button_move(y=0,x=0):
		nonlocal px,py
		py+=y*(buttonhigh+offset)
		px+=x*(buttonwide+offset)


	color_type=2

	if color_type==0:#无色
		color_windowbg="#191919"
		color_textbg="#232323"
		color_maintext="#bbbbbb"
		color_auxiliarytext="#969696"
		color_activebuttonfg="#808080"
		color_inactivebuttonbg="#444444"
		color_activebuttonbg="#333333"
		color_red="#440d03"
		color_blue="#081f2d"
	elif color_type==1:#蓝色系
		color_windowbg="#16161c"
		color_textbg="#1f1f28"
		color_maintext="#bababc"
		color_auxiliarytext="#959597"
		color_activebuttonfg="#7e7e82"
		color_inactivebuttonbg="#3b3b4d"
		color_activebuttonbg="#2c2c3a"
		color_red="#5e2c30"
		color_blue="#22323e"
	elif color_type==2:#棕色系
		color_windowbg="#1c1a16"
		color_textbg="#28251f"
		color_maintext="#bcbbba"
		color_auxiliarytext="#979695"
		color_activebuttonfg="#82817e"
		color_inactivebuttonbg="#4d463b"
		color_activebuttonbg="#3a352c"
		color_red="#5f2e2d"
		color_blue="#24333d"


	windowwide=int(1920*window_size)
	windowhigh=int(1080*window_size)

	window = tk.Tk()
	a=FullScreenApp(window)
	if fullscreen=="1":
		a.toggle_fullscreen()
	window.title(window_title) # 标题
	window.geometry('%sx%s'%(windowwide,windowhigh)) # 窗口尺寸
	window.iconbitmap("ico.ico")
	window.config(bg=color_windowbg)
	window.resizable(0,0)
	window.bind("<Control-q>",clearwindow)#ctrl+q快捷键清空工作台
	window.bind("<Control-w>",goodbye)#ctrl+w快捷键退出
	window.bind("<Control-s>",lambda event:save_temp_file("editing",event))#ctrl+s快捷键保存当前页面到temp文件
	window.bind("<Control-e>",lambda event:add_tag(event,0,0))#ctrl+e快捷键添加段落span
	# 、、、如果不是侦测前后光标的话很可能替换过多，先咕咕咕window.bind("<Control-b>",lambda event:manually_add_style(event,"bold"))
	
	def window_key_event(event):
		textbox_count_word_number(event)
		textbox_automatically_add_style(event)#丫的text控件没有validate属性，就没法侦测textbox里的按键，那我只能做成全局侦测喽
	window.bind("<Key>",lambda event:window_key_event(event))
	
	if dobackup==1:#只有真正进入手账了才允许使用回避界面
		window.bind("<Control-Shift-A>",lambda event:elude(event,"Tereo"))
		window.bind("<Control-Shift-S>",lambda event:elude(event,"追忆似水年华"))
		window.bind("<Control-Shift-D>",lambda event:elude(event,"Miss Alice"))
		window.bind("<Control-Shift-F>",lambda event:elude(event,"Radzig"))
		window.bind("<Control-Shift-F12>",lambda event:cancel_elude(event))

	fontsize=22*window_size
	button_fontsize=int(fontsize*0.5)
	offset=(10/1920)*windowwide
	centerwide=(9670/8/1920)*windowwide#这里是算好了中间填十个按钮的
	sidewide=(windowwide-centerwide-4*offset)/2
	sidehigh=(800/1080)*windowhigh
	buttonwide=sidewide/3
	buttonhigh=(windowhigh-sidehigh-offset*6)/4
	entryhigh=buttonhigh
	logwide=(4*buttonwide+3*offset)
	loghigh=(buttonhigh*2+offset)
	scrollbar_wide=7*window_size






	"左侧目录区"
	px=offset
	py=offset

	listbox_left=tk.Listbox(window,font=(fontfamily,int(fontsize*0.75)),bg=color_textbg,fg=color_auxiliarytext,highlightbackground=color_windowbg,selectbackground=color_activebuttonbg,selectforeground=color_maintext)
	listbox_left.bind("<Double-Button-1>",lambda event:extractselection(event,[listbox_left.get(tk.ACTIVE)],1))#双击快捷键，直接显示选集
	listbox_left.place(y=py,x=px,width=sidewide,height=sidehigh)
	scrollbar_left=MyScrollbar(listbox_left,width=scrollbar_wide,command=listbox_left.yview)
	listbox_left.config(yscrollcommand=scrollbar_left.set)
	scrollbar_left.pack(side="right",fill="y")

	"左侧目录搜索"
	def search_leftlist_typing(s):
		search_leftlist_whiletyping(s)
		return True
	search_leftlist_typingCMD=window.register(search_leftlist_typing)

	entry_left_search=tk.Entry(window,bg=color_textbg,fg=color_auxiliarytext,font=(fontfamily,int(0.8*fontsize)),insertbackground='white',validate='key',validatecommand=(search_leftlist_typingCMD,'%P'))#tag搜索框
	#、、 entry_left_search.bind('<Return>',searchtag)#回车搜索
	entry_left_search.place(y=py+sidehigh+offset,x=px,width=sidewide,height=entryhigh)

	py+=sidehigh+entryhigh+2*offset
	button_listlefttitle=tk.Button(window,text="标题",command=lambda:listlefttitle(1),font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_listlefttitle.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	px+=buttonwide
	px+=buttonwide
	button_listlefttag=tk.Button(window,text="TAG",command=lambda:listlefttag(1),font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_listlefttag.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	# button_listlefttree=tk.Button(window,text="树",command=listlefttree,font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	# button_listlefttree.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	px-=2*buttonwide
	button_move(1,0)

	button_listleft_add_one=tk.Button(window,text="+",command=listleft_add_one,font=(fontfamily,button_fontsize),bd=1,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_listleft_add_one.place(y=py,x=px+buttonhigh+1*1920/windowwide,width=buttonhigh,height=buttonhigh)
	button_listleft_delete_one=tk.Button(window,text="-",command=listleft_delete_one,font=(fontfamily,button_fontsize),bd=1,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_listleft_delete_one.place(y=py,x=px,width=buttonhigh,height=buttonhigh)
	button_move(1,0)
	button_go_to_the_previous_page=tk.Button(window,text="<",command=go_to_the_previous_page,font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_go_to_the_previous_page.place(y=py,x=px,width=buttonhigh,height=buttonhigh)
	button_move(-1,0)

	px+=2*buttonwide
	button_change_tag_in_tempfile=tk.Button(window,text="重命名temp\n中的tag",command=change_tag_in_tempfile,font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_change_tag_in_tempfile.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(1,0)
	button_delete_tag_in_tempfile=tk.Button(window,text="移除temp\n中的tag",command=delete_tag_in_tempfile,font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_delete_tag_in_tempfile.place(y=py,x=px,width=buttonwide,height=buttonhigh)




	"中央文本框"
	px=sidewide+offset*2
	py=offset

	textbox=tk.Text(window,font=(fontfamily,int(fontsize)),bg=color_textbg,fg=color_maintext,insertbackground='white')#文本区
	textbox.place(y=py,x=px,width=centerwide-scrollbar_wide,height=sidehigh)
	scrollbar_center=MyScrollbar(window,width=scrollbar_wide,height=sidehigh,command=textbox.yview)
	textbox.config(yscrollcommand=scrollbar_center.set)
	scrollbar_center.place(y=py,x=px+centerwide-scrollbar_wide)

	"中央按钮"
	py=sidehigh+offset*2
	# button_conversediary=tk.Button(window,text="暂不可用",font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)#"输出手账\n的EPUB",command=lambda :output_file("人间细碎手账.md")
	# button_conversediary.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	# button_move(1,0)
	# button_converseall=tk.Button(window,text="暂不可用",font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)#"输出所有\n的EPUB",command=lambda :output_file()
	# button_converseall.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	# button_move(1,0)
	button_backup=tk.Button(window,text="备份",command=backup,font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_backup.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(1,0)
	button_cls=tk.Button(window,text="清空工作台",font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_cls.bind("<ButtonRelease-1>",clearwindow)
	button_cls.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(-1,1)

	button_adddate=tk.Button(window,text="手账修正日期",command=adddate,font=(fontfamily,button_fontsize),bd=2,bg=color_red,fg=color_auxiliarytext,activebackground="#3c0a02",activeforeground=color_activebuttonfg)
	button_adddate.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(1,0)
	button_add_today=tk.Button(window,text="当日新增",command=add_today,font=(fontfamily,button_fontsize),bd=2,bg=color_red,fg=color_auxiliarytext,activebackground="#3c0a02",activeforeground=color_activebuttonfg)
	button_add_today.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(-1,1)

	button_fixchat1=tk.Button(window,text="修正聊天\n记录1",command=fixchat1,font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_fixchat1.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(1,0)
	button_fixchat2=tk.Button(window,text="修正聊天\n记录2",command=fixchat2,font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_fixchat2.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(1,0)
	button_changerank=tk.Button(window, text='标题转换',command=changerank,font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_changerank.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(-2,1)


	button_analyse_tag=tk.Button(window, text='tag统计',command=analyse_tag,font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_analyse_tag.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(1,0)
	button_analysefrequency=tk.Button(window, text='词频统计',command=analysefrequency,font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_analysefrequency.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(-1,1)


	# #"手账内Tag\n段录入"也没用啦
	# button_add_tag_in_file=tk.Button(window,text="暂不可用",font=(fontfamily,button_fontsize),bd=2,bg=color_red,fg=color_auxiliarytext,activebackground="#3c0a02",activeforeground=color_activebuttonfg)
	# # 、、、、、、button_add_tag_in_file.bind("<ButtonRelease-1>",lambda event:add_tag(event,1,trans_to_html.get()))
	# button_add_tag_in_file.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	# button_move(1,0)
	# trans_to_html=tk.IntVar()
	# checkbutton_trans_to_html=tk.Checkbutton(window,text="html版",variable=trans_to_html,bg=color_windowbg,fg=color_auxiliarytext,selectcolor=color_windowbg,activebackground=color_windowbg,activeforeground=color_auxiliarytext)
	# checkbutton_trans_to_html.place(y=py,x=px)
	# button_move(-1,1)

	button_output_current_md=tk.Button(window,text="输出当前\n文件md",command=lambda:output_file("%s"%tempfile_name,1),font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_output_current_md.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(1,0)
	button_output_current_md=tk.Button(window,text="输出当前\n页面md",command=lambda:output_file(-1,1),font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_output_current_md.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(-1,1)


	button_output_current_epub=tk.Button(window,text="输出当前\n文件EPUB",command= lambda:output_file("%s"%tempfile_name),font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_output_current_epub.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(1,0)
	button_output_current_epub=tk.Button(window,text="输出当前\n页面EPUB",command= lambda:output_file(-1),font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_output_current_epub.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(-1,1)


	button_save_current_file_to_diary=tk.Button(window,text="保存当前\n文件到手账",command=lambda:save_current_to_diary(),font=(fontfamily,button_fontsize),bd=2,bg=color_red,fg=color_auxiliarytext,activebackground="#3c0a02",activeforeground=color_activebuttonfg)
	button_save_current_file_to_diary.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(1,0)
	button_readin_entire_diary=tk.Button(window,text="读取手账文件",command=readin_entire_diary,font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_readin_entire_diary.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(-1,1)

	button_open_tempfile_in_typora=tk.Button(window,text="在Typora中\n打开当前文件",command=open_tempfile_in_typora,font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_open_tempfile_in_typora.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(1,0)
	button_open_tempfile_in_sublime=tk.Button(window,text="在Sublime中\n打开当前文件",command=open_tempfile_in_sublime,font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_open_tempfile_in_sublime.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(-1,1)
	

	button_show_current_file=tk.Button(window,text="查看当前\n文件",command=show_current_file,font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_show_current_file.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(1,0)
	button_random_text=tk.Button(window,text="随机段落",command=random_text,font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_random_text.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(-1,1)

	# button_save_temp_file=tk.Button(window,text="保存当前\n页面",command=lambda :save_temp_file("editing"),font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	# button_save_temp_file.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	# button_move(1,0)
	# button_overwrite_temp_file=tk.Button(window,text="暂不可用",font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	# button_overwrite_temp_file.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	# button_move(-1,1)

	number_of_word_in_diary=tk.StringVar()
	s=decrypting(0,diary_file_path,0)
	diary_count_word_number(s)
	label_number_of_word_in_diary=tk.Label(window,textvariable=number_of_word_in_diary,bg=color_windowbg,fg=color_auxiliarytext,font=("Hack",int(fontsize*0.5)))
	label_number_of_word_in_diary.place(y=py,x=px)
	button_move(2/3,0)
	number_of_word_in_tempfile=tk.StringVar()
	number_of_word_in_tempfile.set("0")
	label_number_of_word_in_tempfile=tk.Label(window,textvariable=number_of_word_in_tempfile,bg=color_windowbg,fg=color_auxiliarytext,font=("Hack",int(fontsize*0.5)))
	label_number_of_word_in_tempfile.place(y=py,x=px)
	button_move(2/3,0)
	number_of_word_in_textbox=tk.StringVar()
	number_of_word_in_textbox.set("0")
	label_number_of_word_in_textbox=tk.Label(window,textvariable=number_of_word_in_textbox,bg=color_windowbg,fg=color_auxiliarytext,font=("Hack",int(fontsize*0.5)))
	label_number_of_word_in_textbox.place(y=py,x=px)


	button_move(1+2/3,0)
	button_goodbye=tk.Button(window,text="退出",font=(fontfamily,button_fontsize),bd=2,bg=color_blue,fg=color_auxiliarytext,activebackground="#071a26",activeforeground=color_activebuttonfg)
	button_goodbye.bind("<ButtonRelease-1>",goodbye)
	button_goodbye.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(0,-1)

	mw = Watch(fontsize,color_windowbg,color_auxiliarytext,window,bg=color_windowbg)
	mw.start()
	mw.place(x=px,y=py)
	button_move(0,-1)

	"下方输入框"
	entry_input=tk.Entry(window,bg=color_textbg,fg=color_auxiliarytext,insertbackground='white',font=(fontfamily,int(0.8*fontsize)))
	entry_input.place(y=py,x=px,width=buttonwide,height=entryhigh)
	button_move(-1,-4)
	"下方log框"
	log=tk.Text(window,bg=color_textbg,fg=color_auxiliarytext,insertbackground='white')#日志
	log.place(y=py,x=px,width=logwide,height=loghigh)
	scrollbar_log=MyScrollbar(log,width=scrollbar_wide,command=log.yview)
	log.config(yscrollcommand=scrollbar_log.set)
	scrollbar_log.pack(side="right",fill="y")





	"右侧选集区"
	px=sidewide+centerwide+offset*3
	py=offset
	listbox_right=tk.Listbox(window,font=(fontfamily,int(fontsize*0.75)),bg=color_textbg,fg=color_auxiliarytext,highlightbackground=color_windowbg,selectbackground=color_activebuttonbg,selectforeground=color_maintext,selectmode="extended")#tag列表、、、竟然还能多选…………
	#、、、、 listbox_right.bind("<Right>",taggetup)#鼠标右键上屏快捷键，现在listbox可以多选了，这个就不用了
	#、、、、 listbox_right.bind("<Button-3>",taggetup)#向右上屏快捷键，现在listbox可以多选了，这个就不用了
	listbox_right.bind("<Double-Button-1>",lambda event:extractselection(event,[listbox_right.get(listbox_right.curselection())]))#双击快捷键，直接显示选集
	listbox_right.place(y=offset,x=px,width=sidewide,height=sidehigh)
	scrollbar_right=MyScrollbar(listbox_right,width=scrollbar_wide,command=listbox_right.yview)
	listbox_right.config(yscrollcommand=scrollbar_right.set)
	scrollbar_right.pack(side="right",fill="y")



	"右侧选集搜索"
	#验证与冷却？（要给Entry加上这两个属性：
	#validate='key'（输入就激活）,validatecommand=(typingCMD,'%P')
	#第一项是函数，第二项是传入函数的值参数，%P是当前框内的值
	#可以用验证正在输入，来做实时的搜索，这样下面的回车搜索就没用了
	def search_rightlist_typing(key):
		search_rightlist_whiletyping(key)
		return True
	search_rightlist_typingCMD=window.register(search_rightlist_typing)

	entry_right_search=tk.Entry(window,bg=color_textbg,fg=color_auxiliarytext,font=(fontfamily,int(0.8*fontsize)),insertbackground='white',validate='key',validatecommand=(search_rightlist_typingCMD,'%P'))#tag搜索框
	#、、、 entry_right_search.bind('<Return>',searchtag)#回车搜索
	entry_right_search.place(y=py+sidehigh+offset,x=px,width=sidewide,height=entryhigh)



	"选集区按钮"
	py+=sidehigh+entryhigh+2*offset
	button_listrighttitle=tk.Button(window,text="标题",command=lambda:listrighttitle(1),font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_listrighttitle.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	px+=buttonwide
	px+=buttonwide
	button_listrighttag=tk.Button(window,text="TAG",command=lambda:listrighttag(1),font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_listrighttag.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	# button_listrighttree=tk.Button(window,text="树",command=listrighttree,font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	# button_listrighttree.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	px-=2*buttonwide
	button_move(1,0)


	button_add_tag_in_text=tk.Button(window,text="添加段落\n的TAG",font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_add_tag_in_text.bind("<ButtonRelease-1>",lambda event:add_tag(event,0,0))
	button_add_tag_in_text.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(1,0)
	button_remove_tag_in_textbox=tk.Button(window,text="清除段落\n的tag",command=remove_tag_in_textbox,font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_remove_tag_in_textbox.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	px+=buttonwide
	button_move(-1,0)

	button_extractselection=tk.Button(window,text="TAG选集",font=(fontfamily,button_fontsize),bd=2,bg=color_inactivebuttonbg,fg=color_auxiliarytext,activebackground=color_activebuttonbg,activeforeground=color_activebuttonfg)
	button_extractselection.bind("<ButtonRelease-1>",lambda event:extractselection(event,listbox_get_multiple_selection(listbox_right)))#以前不知道可以多选还用的上屏分割……
	button_extractselection.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	px+=buttonwide

	button_change_tag_in_file=tk.Button(window,text="重命名手账\n的tag",command=change_tag_in_file,font=(fontfamily,button_fontsize),bd=2,bg=color_red,fg=color_auxiliarytext,activebackground="#3c0a02",activeforeground=color_activebuttonfg)
	button_change_tag_in_file.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	button_move(1,0)
	button_delete_tag_in_file=tk.Button(window,text="移除手账\n的tag",command=delete_tag_in_file,font=(fontfamily,button_fontsize),bd=2,bg=color_red,fg=color_auxiliarytext,activebackground="#3c0a02",activeforeground=color_activebuttonfg)
	button_delete_tag_in_file.place(y=py,x=px,width=buttonwide,height=buttonhigh)
	
	

	try:
		backup()
	except:
		pass
	window.mainloop()

def login_page():
	def check_password():
		nonlocal tried_time,click_times
		tried_time+=1
		entered_password=entry_password.get()
		if tried_time<=4:#三次之内能进入手账
			if tried_time<=2:
				v.set("输入口令吧")
			elif 2<tried_time<=4:
				v.set("你不会是来偷鸡摸狗的吧……")
		elif 4<tried_time<=6:
			v.set("我问问你，旅程中Kumersun\n的下一站是哪里？")
		elif 6<tried_time<=8:
			v.set("追忆似？")
		elif 8<tried_time<=10:
			v.set("那Alice的全名呢？\n这个答不出来就过分了。")
		elif 10<tried_time<=12:
			v.set("Henry的父亲呢？\n再答不出来就没机会了……")
		else:
			v.set("……你走吧")

		if tried_time<=5:
			if verify_consistency(entered_password)==1:
				window.destroy()
				initialize()
				main_page()
		if tried_time<=5 or 4<tried_time<=7:
			confused_password="Tereo"
			if entered_password==confused_password:
				# os.system("start explorer http://spicy-wolf.com/top.html")
				window.destroy()
				confused_initialize("Tereo")
				main_page()
				# os._exit(0)
		if tried_time<=5 or 7<tried_time<=9:
			confused_password="追忆似水年华"
			if entered_password==confused_password:
				# os.system("start explorer http://spicy-wolf.com/top.html")
				window.destroy()
				confused_initialize("追忆似水年华")
				main_page()
				# os._exit(0)
		if tried_time<=5 or 9<tried_time<=11:
			confused_password="Miss Alice"
			if entered_password==confused_password:
				# os.system("start explorer https://cn.pornhub.com/model/alicemfc")
				window.destroy()
				confused_initialize("Miss Alice")
				main_page()
				# os._exit(0)
		if tried_time<=5 or 11<tried_time<=13:
			confused_password="Radzig"
			if entered_password==confused_password:
				# os.system("start explorer https://www.kingdomcomerpg.com/")
				window.destroy()
				confused_initialize("Radzig")
				main_page()
				# os._exit(0)

	def goto_encryption_toolbox_page(event):
		if 45<event.x<55 and 45<event.y<55:#摸右耳才能进入
			window.destroy()
			encryption_toolbox_page()

	tried_time=0
	click_times=0
	window=tk.Tk()
	window.title(window_title) # 标题
	windowwide=400
	windowhigh=200
	window.geometry('%sx%s'%(windowwide,windowhigh)) # 窗口尺寸
	window.iconbitmap("ico.ico")
	window.config(bg="#fbf6f0")
	window.resizable(0,0)
	window.bind("<Control-Shift-KeyPress-K>",goto_encryption_toolbox_page)#组合键才能进入

	v=tk.StringVar()
	v.set("")
	entry_password=tk.Entry(window,font=("",int(16*window_size)),bd=4,show="*")
	entry_password.place(y=70,x=225,height=30,width=150)
	
	button_check_password=tk.Button(window,text="验证身份",command=check_password,bd=2)
	button_check_password.place(y=120,x=250,height=30,width=100)
	
	img=tk.PhotoImage(file="holo.gif")
	label_img=tk.Label(window,image=img)
	label_img.place(y=0,x=0)

	label_warning=tk.Label(window,textvariable=v,bg="#fbf6f0")
	label_warning.place(y=30,x=225)
	window.mainloop()


def check_U_Protect():
	global password,encrypt_key
	password="U_Protect"
	encrypt_key=generate_encrypt_key(password)
	try:
		s=decrypting(0,"F:/U_Protect",0)
		if s=="Cute Girl Holence!":
			return 1
		else:
			return 0
	except:
		return 0



base=""
tempfile_name=""

allrightlist=[]#右边列表的内容，是个value为英文转写的字典
right_listing_from=""#现在右边列出的来自于哪
extract_right_from=""#textbox上的内容来自于哪

allleftlist=[]#左边列表的内容，是个value为英文转写的字典
left_listing_from=""
left_current_title=[]
left_previous_title=[]

tree_list=[]

showned_text=""#当前textbox上的内容（只有有extract_right_from为title或diary时才会记录）
output_selection_file_name_head=""#输出选集文件的名字
output_selection_file_name_tail=""
old_diary_text=""#保存最开始读入的title选集全部，以便最后回去覆盖替换
dobackup=1
right_listbox_index=0
left_listbox_index=0

elude_backup_temp_file=""
elude_backup_encrypt_key=0
elude_backup_diary_file_path=""
elude_backup_old_diary_text=""
elude_backup_right_listing_from=""
elude_backup_extract_right_from=""

updated=1
updated_text=""


window_size=1
fullscreen="0"
fontfamily="宋体"
diary_file_path=""
diary_folder_path=""
window_title="工作台"
typora_location=r"D:\program\Typora\Typora.exe"
sublime_location=r'"D:\program\Sublime Text 3\sublime_text.exe"'
password=""
encrypt_key=0
backup_dst=[]

listbox_right=None
listbox_left=None
entry_left_search=None
entry_right_search=None
entry_input=None
textbox=None
log=None

number_of_word_in_diary=None
label_number_of_word_in_diary=None
number_of_word_in_tempfile=None
label_number_of_word_in_tempfile=None
number_of_word_in_textbox=None
label_number_of_word_in_textbox=None

def main():
	global tree_list
	tree_list=creat_tree()
	# if check_U_Protect():
		# login_page()
	login_page()
if __name__=="__main__":
	main()
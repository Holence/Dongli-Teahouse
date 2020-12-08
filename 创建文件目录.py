import os

confirm=input("输入Confirmed开始执行任务:")
if confirm!="Confirmed":
	exit()
base=os.getcwd()
with open("文件目录.txt","r",encoding="utf-8") as f:
	a=f.readline()
	b=f.readline()
	while a!="":
		ka=a.count("	")
		kb=b.count("	")
		if a.lstrip()[0]=="\\":#如果是文件夹
			try:#尝试创建文件夹
				os.makedirs(base+"/"+a.lstrip()[:-1])
				print(a)
			except:
				pass
			#下面分情况看进入文件夹还是退出文件夹
			if ka<kb:#要深入
				os.chdir(base+"/"+a.lstrip()[:-1])
				base=os.getcwd()
			elif ka==kb:#不动
				pass
			else:#要退出
				t=ka-kb
				while t:
					t-=1
					os.chdir("..")
					base=os.getcwd()
		else:#不是文件夹
			if ka==kb:#不动
				pass
			elif ka>kb:#要退出
				t=ka-kb
				while t:
					t-=1
					os.chdir("..")
					base=os.getcwd()
		a=b
		b=f.readline()

print("OK")
os.system("pause")

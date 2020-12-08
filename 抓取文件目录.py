import os

def deepin(dir,n,onlyfolder):
	n+=1
	fore="	"*n
	list=os.listdir(dir)
	for i in list:
		path=os.path.join(dir,i)
		if os.path.isdir(path):
			f.write(fore+"\\"+i+"\n")
			print(fore+"\\"+i+"\n")
			try:
				n=deepin(path,n,onlyfolder)
			except: pass
		else:
			if onlyfolder==0:
				f.write(fore+i+"\n")
				print(fore+i+"\n")
	n-=1
	return n

onlyfolder=int(input("只要文件夹不要文件吗？1or0："))
with open("文件目录.txt","w",encoding="utf-8") as f:
	dir=os.getcwd()
	deepin(dir,-1,onlyfolder)

print("OK")
os.system("pause")
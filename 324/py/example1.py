def Process(x):
	x = x.split(" ") 
	school = x[0].replace("我是", "")
	print(f"學校:{school}\n姓名:{x[2]}")


# 只有直接執行 examp;e1.py時，這段才會跑
if __name__ == "__main__":
	Name = "我是靜宜大學 資管二A 黃筱嵐"
	Process(Name)
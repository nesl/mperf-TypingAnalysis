'''
Coded by: Vikranth 

'''

f = open('E:\Keylogs\Keylogs\Subject_mperf_alabsi_2\keyboardlogs0.txt', 'r')
x = f.readlines()
f.close()

time = []
keys = []
active_window = []
key_ids = []

for line in x[2:]:
	if not line.startswith(("//"," ","\n")):
		line = line.strip('\n')
		line = line.split(',')
		time.append(line[0].strip())
		keys.append(line[1].strip())
		active_window.append(line[2].strip())
		key_ids.append(line[3].strip())

n = len(key_ids)
print (time[0])
print (keys)
print (active_window)
print (key_ids)
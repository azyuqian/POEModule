def file_writing(target_file_name, x, y, z):
    
    str_to_add = str(x) + "," + str(y) + "," + str(z) + "\n"
    
    target_file = open(target_file_name, 'a')
    
    target_file.write(str_to_add)
    target_file.close()
    
    
target_file_name = 'data.txt'
x = 1
y = 2
z = 3
file_writing(target_file_name, x, y, z)

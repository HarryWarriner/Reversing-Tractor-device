CC = g++
#get all .c files in current directory 
src=$(wildcard ./*.cpp)
#matches the corresponding files in the current directory
obj=$(patsubst ./%.cpp,./%.o,$(src))
#link to library
#name of the excutable file
target=libmlx90640.so

$(target):$(obj)
	$(CC) $(obj) -o $(target) -fPIC -shared

#output all .o files
$(obj):./%.o:./%.cpp	
	$(CC) -c $< -o $@

.PHONY:clean all
clean:
	-rm *.o $(target)
$(info clean successful)

#this file should be located in current root directory
#the name of excutable file can modify in "app = main" 
#make clean command is clear all output files 
#if has other library then should be added in DLIBS

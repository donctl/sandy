/*
 * =====================================================================================
 *
 *       Filename:  seek_and_read.c
 *
 *    Description:  Dumps the last 16k of a file. It is part of the sandy framework,
 *		    thus the same license applies.
 *
 *        Version:  1.0
 *        Created:  09/24/2013 15:45:26
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  Laszlo Toth 
 *   Organization:  
 *
 * =====================================================================================
 */



#define _FILE_OFFSET_BITS 64 
#define _LARGEFILE64_SOURCE

#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/stat.h>


int main(int argc, char* argv[]){
	
	int fdin;
	int fdout;
	unsigned char buff[20000];
	int res;
	long long offset;

	offset=-0x4000;

	fdin=open(argv[1],O_RDONLY);
	if(fdin==-1){
		printf("Could not open the file: %s!", argv[1]);
		return -1;
	}

	fdout=open(argv[2],O_WRONLY|O_CREAT);
	if(fdout==-1){
		printf("Could not open the file: %s!", argv[2]);
		return -1;
	}
	//Others can read. It is important for adb. The user should make sure to delete this file after download
	fchmod(fdout, S_IRUSR|S_IWUSR|S_IRGRP|S_IROTH);
	
	lseek64(fdin, offset, SEEK_END);
	res=read(fdin, buff, 16384);
	if(res==-1){
		printf("Could not read the file: %s!", argv[1]);
		return -1;
	}
	res=write(fdout, buff, 16384);
	if(res==-1){
		printf("Could not write the file: %s!", argv[2]);
		return -1;
	}
	printf("%d\n",res);
	return 0;
}


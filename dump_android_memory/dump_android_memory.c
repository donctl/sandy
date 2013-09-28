/*
 * =====================================================================================
 *
 *       Filename:  dump_android_memory.c
 *
 *    Description:  Process memory dumper for andorid. It is based on the following code:
 *	            http://tthtlc.wordpress.com/2011/12/10/how-to-dump-memory-of-any-running-processes-in-android-2/
 *	            It is part of the sandy framework, thus the same license applies.
 *
 *        Version:  1.0
 *        Created:  09/24/2013 15:37:39
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  Laszlo Toth 
 *   Organization:  
 *
 * =====================================================================================
 */


#include <stdio.h>
#include <stdlib.h>
#include <sys/ptrace.h>

char* filename;

int main(int argc, char **argv) {

	if (argc == 5) {
        	int pid = atoi(argv[1]);
		unsigned int start_address;
		sscanf(argv[2], "0x%x", &start_address);

		unsigned int total_bytes;
		sscanf(argv[3], "%d", &total_bytes);
		
		filename=argv[4];
		
		ptrace(PTRACE_ATTACH, pid, NULL, NULL);
		wait(NULL);
		dump_memory(pid, start_address, total_bytes);
		ptrace(PTRACE_CONT, pid, NULL, NULL);
		ptrace(PTRACE_DETACH, pid, NULL, NULL);
	} else {
		printf("%s <pid> <start_address> <number of bytes>  <filename>\nwhere <start_address> is in hexadecimal (remember the \"0x\" in front is needed - by sscanf()\n", argv[0]);
		exit(0);
    	}
}

dump_memory(int pid, unsigned int start_address, unsigned int total_bytes) {
	
	unsigned int address;
	unsigned int number = 0;
	FILE* fh;

	fh=fopen(filename,"w");
	if(fh==NULL){
		printf("ERROR: Could not open file: %s!", filename);
		return;
	}

	for (address=start_address;address<start_address+total_bytes;address+=4) {
            	number=ptrace(PTRACE_PEEKDATA, pid, (void *)address, (void *)number);
		fwrite(&number, sizeof(int), 1, fh);
	}
	fclose(fh);
}


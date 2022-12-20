#include <iostream>
#include "include/skim.h"

#include <stdio.h>  // for printf()
#include <stdlib.h> // for strtol()
#include <errno.h>  // for errno
#include <limits.h> // for INT_MIN and INT_MAX
#include <string.h>  // for strlen

int convert_to_int(char** argv, int idx) {
  char* p;
  errno = 0; // not 'int errno', because the '#include' already defined it
  std::cout << "\nargv[1]: " << argv[1];
  std::cout << "\nLength of argv: " << sizeof(argv)/sizeof(char**); // returns 1, hence why the next line yields a segmentation fault when idx=2
  
  long arg = strtol(argv[idx], &p, 10);
  if (*p != '\0' || errno != 0) {
	return 1; // In main(), returning non-zero means failure
  }

  if (arg < INT_MIN || arg > INT_MAX) {
	return 1;
  }
  int arg_int = arg;

  // Everything went well, print it as a regular number plus a newline
  return arg_int;
}

//Run with ./produce.exe photon
int main(int argc, char **argv) {
  std::string dir = "/data_CMS/cms/ehle/L1HGCAL/";
  std::string tree_name = "FloatingpointMixedbcstcrealsig4DummyHistomaxxydr015GenmatchGenclustersntuple/HGCalTriggerNtuple";

  if (strlen(argv[1]) == 0) {
	return 1; // empty string
  }

  //process_program_options(argc, argv);
  string particle = std::string(argv[1]);

  //int nentries = convert_to_int(argv, 2); // argv only has one argument!

  std::string infile = particle + "_200PU_bc_stc_hadd.root";
  std::string outfile = "skim_" + infile;
  //skim(tree_name, dir + infile, dir + outfile, particle, nentries);
  skim(tree_name, dir + infile, dir + outfile, particle, 1);
  return 0;
}

#include <iostream>
#include <string>
#include "include/skim.h"

#include <stdio.h>  // for printf()
#include <stdlib.h> // for strtol()
#include <errno.h>  // for errno
#include <limits.h> // for INT_MIN and INT_MAX
#include <string.h>  // for strlen

using namespace std;

pair<string, string> parseFileOptions(int argc, char** argv) {
  string infileName, outfileName;
  for (int i = 1; i < argc; i++) {
    string arg = argv[i];
    if (arg == "--infile") {
      if (i + 1 < argc) {
        // The input file name is the next argument
        infileName = argv[i + 1];
      } else {
        // The input file name was not provided
        cerr << "Error: --infile option requires a value" << endl;
        exit(1);
      }
    } else if (arg == "--particle") {
      if (i + 1 < argc) {
        // The output file name is the next argument
        outfileName = argv[i + 1];
      } else {
        // The output file name was not provided
        cerr << "Error: --particle option requires a value" << endl;
        exit(1);
      }
    }
  }
  return make_pair(infileName, outfileName);
}

string file_from_path(const string& path)
{
  size_t pos = path.find_last_of("/");

  return path.substr(pos + 1);
}

//Run with ./produce.exe photon
int main(int argc, char **argv) {

  pair<string, string> fileNames = parseFileOptions(argc, argv);
  
  string infile = fileNames.first;
  string particle = fileNames.second;
  string outfile = "skim_"+particle+"_"+file_from_path(infile);

  if (fileNames.first.empty()) {
    cout << "\nNo input file name provided." << endl;
  }
  else {
    cout << "\nInput file name: " << infile << endl;
  }

  if (fileNames.second.empty()) {
    cout << "\nNo particle provided." << endl;
  }
  else {
    cout << "\nOutput file name: " << outfile << endl;
  }

  string data_dir = "/data_CMS/cms/ehle/L1HGCAL/";
  string tree_name = "FloatingpointMixedbcstcrealsig4DummyHistomaxxydr015GenmatchGenclustersntuple/HGCalTriggerNtuple";
  
  string out_dir = data_dir+'/'+particle+'/';

  skim(tree_name, infile, out_dir + outfile, particle, 1);
  return 0;
  
}

#!/bin/python

from yaml import load_all, dump_all, Loader, Dumper, YAMLError

cases_file = open("fixed-substring.yaml", "r")
cases_obj = load_all(cases_file, Loader=Loader)

for obj in cases_obj:
    print(obj['file'])
    test_input = open(f"text-files/{obj['file']}", "rb").read()
    for case in obj['cases']:
        print(f"\t{case['pattern']} in {obj['file']}: {case['matches']}")
    print()


import argparse
import re
import Levenshtein

parser = argparse.ArgumentParser(description="Fix names")
parser.add_argument("file1", help="File containing the correct names, one per line.")
parser.add_argument("file2", help="The file to correct")
parser.add_argument("pat", help="The pattern how to replace the name, e.g. \"Dataset:name:(?P<name>.+)\t\"")
parser.add_argument("file3", nargs="?", help="Optional output file")
args = parser.parse_args()


def get_correct_names(file):
    res = set()
    with open(file, "r") as infile:
        for line in infile.readlines():
            line = line.strip()
            res.add(line)
    return res


def get_names(file):
    res = set()
    pat = re.compile(args.pat)
    with open(file, "r") as infile:
        for line in infile.readlines():
            line = line.strip()
            m = pat.match(line)
            if m:
                res.add(m.group("name"))
    return res


def get_best_match(name, correct_names):
    best = None
    best_distance = 1000000
    for correct_name in correct_names:
        dist = Levenshtein.distance(name, correct_name)
        if dist < best_distance:
            best_distance = dist
            best = correct_name

    return best


def fix(file, pat, replacements, out_file):
    cpat = re.compile(pat)
    with open(file) as infile:
        for line in infile.readlines():
            line = line.strip()
            m = cpat.match(line)
            if m:
                old_name = m.group("name")
                if old_name in replacements:
                    res = line.replace(old_name, replacements[old_name])
                    if out_file:
                        out_file.write(f"{res}\n")
                    else:
                        print(res)


def get_replacemnts(names, correct_names):
    replacements = dict()
    for name in names:
        best_match = get_best_match(name, correct_names)
        approve = input(f"Replace '{name}' with '{best_match}'? [default: yes]")
        if approve == "" or approve.lower() == "y" or approve.lower() == "yes":
            replacements[name] = best_match
    return replacements


names = list(get_names(args.file2))
names.sort()
correct_names = get_correct_names(args.file1)
replacements = get_replacemnts(names, correct_names)

if args.file3:
    with open('../experimentA/idr0151-experimentA-filePaths.tsv', mode="w") as outfile:
        fix(args.file2, args.pat, replacements, outfile)
else:
    fix(args.file2, args.pat, replacements, None)

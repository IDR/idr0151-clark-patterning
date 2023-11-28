import csv

map = dict()
with open('dataset_names.txt', "r") as readfile:
    for line in readfile.readlines():
        no = line.split(":")[0]
        map[no] = line.strip()

with open('../experimentA/idr0151-experimentA-filePaths_old.tsv') as csvfile:
    with open('../experimentA/idr0151-experimentA-filePaths.tsv', mode="w") as outfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            ds = row[0].replace("Dataset:name:", "").split("_")[0]
            outfile.write(f"Dataset:name:\"{map[ds]}\"\t{row[1]}\n")

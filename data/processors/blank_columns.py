import csv
import sys
import argparse

# init arg parser
parser = argparse.ArgumentParser()
parser.add_argument('--entity', type=str, required=True)
args = parser.parse_args()

# init the incoming data as a dict reader
reader = csv.DictReader(sys.stdin)

# write data to stdout
stdout_csv = csv.DictWriter(sys.stdout, fieldnames=reader.fieldnames)
stdout_csv.writeheader()

for row in reader:
    row.update({
        f'{args.entity}:comments:admin': '',
        f'{args.entity}:owner:admin': ''
    })
    stdout_csv.writerow(row)

import csv
import sys
import argparse

# init arg parser
parser = argparse.ArgumentParser()
parser.add_argument('--entity', type=str, required=True)
args = parser.parse_args()

# init the incoming data as a dict reader
lines = iter(line.decode('utf-8').strip() for line in sys.stdin.buffer.readlines())
header = next(lines).split(',')
reader = csv.DictReader(lines, fieldnames=header)

# write data to stdout
stdout_csv = csv.writer(sys.stdout)
stdout_csv.writerow(header)

for row in reader:
    row.update({
        f'{args.entity}:comments:admin': '',
        f'{args.entity}:owner:admin': ''
    })
    stdout_csv.writerow(row.values())

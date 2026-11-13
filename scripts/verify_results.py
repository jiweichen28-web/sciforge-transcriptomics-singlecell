"""Verify the published case tables and local document links (stdlib only)."""
import csv
import math
import re
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / 'outputs' / 'tables'
expected = {'candidate_bulk_summary.csv': 10, 'joint_candidate_summary.csv': 10,
            'joint_gene_celltype_results.csv': 110, 'celltype_proportion_results.csv': 11}
data = {}
for name, count in expected.items():
    with (TABLES / name).open(newline='') as stream:
        data[name] = list(csv.DictReader(stream))
    assert len(data[name]) == count, name
    print(f'{name}: {count} rows')
valid = []
for row in data['joint_gene_celltype_results.csv']:
    try:
        value = float(row['sc_FDR'])
    except ValueError:
        continue
    if math.isfinite(value):
        valid.append(value)
assert len(valid) == 90 and all(value >= 0.05 for value in valid)
assert all(float(row['FDR']) >= 0.05 for row in data['celltype_proportion_results.csv'])
print('Expression FDR: 90 valid, 20 NA, 0 < 0.05; proportion FDR: 0 < 0.05')
for path in (ROOT / 'outputs' / 'figures').glob('*.svg'):
    ET.parse(path)
for path in ROOT.rglob('*.md'):
    for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if link.startswith(('https://', 'http://', '#')):
            continue
        target = path.parent / link.split('#', 1)[0]
        assert target.exists(), (path, link)
print('PASS: result counts, SVG XML and local document links')

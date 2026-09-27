import subprocess

with open('scratch/test_sup.dot', 'w', encoding='utf-8') as f:
    f.write('''digraph G {
    node [shape=box, fontname="Arial"];
    A [label=<50 mm<SUP>2</SUP> Cu XLPE 45m>];
}''')

subprocess.run(['dot', '-Tsvg', 'scratch/test_sup.dot', '-o', 'scratch/test_sup.svg'], check=True)
with open('scratch/test_sup.svg', 'r', encoding='utf-8') as f:
    print('SVG content contains SUP?', 'sup' in f.read().lower())

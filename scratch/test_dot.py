import subprocess
import os

os.makedirs('scratch', exist_ok=True)
with open('scratch/test.dot', 'w', encoding='utf-8') as f:
    f.write('''digraph G {
    graph [bgcolor="transparent", dpi=300];
    node [shape=box, style="filled,rounded", fillcolor="#ffffff", color="#333333", fontname="Helvetica"];
    A -> B;
}''')

subprocess.run(['dot', '-Tsvg', 'scratch/test.dot', '-o', 'scratch/test.svg'], check=True)
subprocess.run(['dot', '-Tpng', '-Gdpi=300', 'scratch/test.dot', '-o', 'scratch/test.png'], check=True)
print('Success! Sizes:', os.path.getsize('scratch/test.svg'), os.path.getsize('scratch/test.png'))

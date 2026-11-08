import os
import time
import nbformat
from nbclient import NotebookClient

t0 = time.time()
nb_path = 'notebooks/04_varredura_semantica.ipynb'
print(f"Iniciando execução do {nb_path}...")

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

client = NotebookClient(nb, timeout=1800, kernel_name='python3')
client.execute()

with open(nb_path, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

print(f"✅ Notebook {nb_path} executado e salvo com sucesso em {time.time()-t0:.1f}s!")

import json

nb_path = "/home/saulo/mba/tcc/enem/notebooks/04_varredura_semantica.ipynb"

with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

cell_19 = nb["cells"][19]
src_19 = "".join(cell_19["source"])

# Otimização de chunksize e dtype
src_19 = src_19.replace('CHUNK_AUDITORIA = 250_000', 'CHUNK_AUDITORIA = 500_000')
src_19 = src_19.replace('chunksize=250_000', 'chunksize=500_000')
src_19 = src_19.replace('dtype="string"', 'dtype=str')
src_19 = src_19.replace('qtd = min(n, tamanho_chunk)', 'qtd = min(3_000, tamanho_chunk)')

cell_19["source"] = [line + "\n" for line in src_19.split("\n")][:-1]

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("✅ Célula 19 otimizada com chunksize=500_000 e dtype=str.")

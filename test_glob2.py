import glob
import os

raw_dir = 'data/raw'
anos_dirs = sorted(glob.glob(os.path.join(raw_dir, 'enem_*')))

for dir_path in anos_dirs:
    ano = os.path.basename(dir_path).split('_')[1]
    csv_files = glob.glob(os.path.join(dir_path, '**', '*.csv'), recursive=True)
    for f in csv_files:
        if 'MICRODADOS_ENEM' in os.path.basename(f).upper():
            print(f"{ano} ({len(csv_files)} csvs total na pasta): {f}")
            break

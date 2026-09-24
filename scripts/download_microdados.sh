#!/usr/bin/env bash
# =============================================================================
# download_microdados.sh
# Baixa e extrai os microdados históricos do ENEM (2015-2025)
# Fonte: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem
#
# Notas:
#   - Usa --no-check-certificate pois o cert da RNP não está na cadeia local
#   - Usa python3 -m zipfile para extração (unzip pode não estar instalado)
#   - Anos 2015/2016 podem falhar por TLS incompatível no servidor INEP
# =============================================================================

set -uo pipefail

# ----------------------------
# Configurações
# ----------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAW_DIR="${SCRIPT_DIR}/../data/raw"
BASE_URL="https://download.inep.gov.br/microdados"
LOG_FILE="${RAW_DIR}/download.log"

# Anos alvo: histórico de viabilidade (2009-2025)
ANOS=(2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025)

# ----------------------------
# Funções auxiliares
# ----------------------------
log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE"
}

hr() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

extract_zip() {
    local zip_file="$1"
    local dest_dir="$2"
    python3 -c "
import zipfile, sys
with zipfile.ZipFile('$zip_file', 'r') as zf:
    zf.extractall('$dest_dir')
    print(f'  Extraídos {len(zf.namelist())} arquivos.')
"
}

# ----------------------------
# Inicialização
# ----------------------------
mkdir -p "$RAW_DIR"
touch "$LOG_FILE"

hr
log "Iniciando download dos Microdados do ENEM"
log "Destino: $RAW_DIR"
log "Anos: ${ANOS[*]}"
hr

TOTAL=${#ANOS[@]}
SUCESSO=0
FALHA=0
PULADO=0

# ----------------------------
# Loop de download
# ----------------------------
for ANO in "${ANOS[@]}"; do
    ZIP_NAME="microdados_enem_${ANO}.zip"
    URL="${BASE_URL}/${ZIP_NAME}"
    ANO_DIR="${RAW_DIR}/enem_${ANO}"
    ZIP_PATH="${RAW_DIR}/${ZIP_NAME}"

    hr
    log "Processando ENEM ${ANO}..."

    # Verifica se já foi extraído (diretório não vazio)
    if [ -d "$ANO_DIR" ] && [ "$(ls -A "$ANO_DIR" 2>/dev/null)" ]; then
        log "  [PULADO] Diretório $ANO_DIR já existe e não está vazio."
        ((PULADO++)) || true
        continue
    fi

    # Se o ZIP já existe localmente, vai para extração direto
    if [ -f "$ZIP_PATH" ] && [ -s "$ZIP_PATH" ]; then
        ZIP_SIZE=$(du -sh "$ZIP_PATH" | cut -f1)
        log "  [CACHE] ZIP já baixado ($ZIP_SIZE). Extraindo diretamente..."
    else
        # Download com wget
        log "  [DOWNLOAD] Baixando: $URL"
        if wget \
            --no-check-certificate \
            --progress=dot:giga \
            --tries=3 \
            --timeout=120 \
            --waitretry=15 \
            --retry-connrefused \
            -O "$ZIP_PATH" \
            "$URL" 2>&1 | tee -a "$LOG_FILE"; then

            if [ ! -f "$ZIP_PATH" ] || [ ! -s "$ZIP_PATH" ]; then
                log "  [ERRO] Arquivo vazio após download: $ZIP_PATH"
                rm -f "$ZIP_PATH"
                ((FALHA++)) || true
                continue
            fi

            ZIP_SIZE=$(du -sh "$ZIP_PATH" | cut -f1)
            log "  [OK] Download concluído. Tamanho: $ZIP_SIZE"
        else
            log "  [ERRO] Falha no download de $URL"
            rm -f "$ZIP_PATH"
            ((FALHA++)) || true
            continue
        fi
    fi

    # Extração via python3
    log "  [EXTRAINDO] Descompactando em $ANO_DIR (via python3)..."
    mkdir -p "$ANO_DIR"

    if extract_zip "$ZIP_PATH" "$ANO_DIR" 2>&1 | tee -a "$LOG_FILE"; then
        log "  [OK] Extração concluída em $ANO_DIR"
        rm -f "$ZIP_PATH"
        log "  [LIMPEZA] ZIP removido: $ZIP_PATH"
        ((SUCESSO++)) || true
    else
        log "  [ERRO] Falha na extração do arquivo $ZIP_PATH"
        rm -rf "$ANO_DIR"
        ((FALHA++)) || true
    fi
done

# ----------------------------
# Resumo final
# ----------------------------
hr
log "Download concluído!"
log "  Total de anos processados : $TOTAL"
log "  Sucesso                   : $SUCESSO"
log "  Pulados (já existiam)     : $PULADO"
log "  Falhas                    : $FALHA"
hr

# Mostra estrutura final
log "Estrutura do diretório raw:"
find "$RAW_DIR" -maxdepth 2 | sort | tee -a "$LOG_FILE"

exit 0

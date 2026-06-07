# ============================================================
# ARQUIVO DE CONTROLE DE EXPERIMENTOS
# Altere estas constantes entre commits para gerar variações.
# Documente cada alteração no EXPERIMENT_LOG.md
# ============================================================

# Experimentos 1-3: pipeline normal (todos False, SLOW_SLEEP_SECONDS=0)
# Experimento 4:    ENABLE_SLOW_TESTS=True, SLOW_SLEEP_SECONDS=5
# Experimento 5:    ENABLE_SLOW_TESTS=True, SLOW_SLEEP_SECONDS=10
# Experimento 6:    ENABLE_FAILING_TEST=True
# Experimento 7:    ENABLE_FAILING_TEST=False (corrigido)
# Experimento 8:    cache desabilitado no YAML (não aqui)
# Experimento 9:    cache reabilitado no YAML (não aqui)
# Experimento 10:   EXTRA_TEST_MULTIPLIER=5
# Experimentos 11-12: mudança no YAML (não aqui)

ENABLE_SLOW_TESTS: bool = False
SLOW_SLEEP_SECONDS: int = 0

ENABLE_FAILING_TEST: bool = False

EXTRA_TEST_MULTIPLIER: int = 1  # multiplica a quantidade de casos paramétricos

# Log de Experimentos

## Tabela de Execuções Planejadas

| # | Workflow   | Variação           | experiment_config.py                              | Hipótese                            |
|---|------------|--------------------|---------------------------------------------------|-------------------------------------|
| 1 | sequential | baseline           | todos padrão                                      | duração estável ~25s                |
| 2 | sequential | baseline           | todos padrão                                      | confirmar estabilidade              |
| 3 | sequential | baseline           | todos padrão                                      | confirmar estabilidade              |
| 4 | sequential | teste lento +5s    | ENABLE_SLOW_TESTS=True, SLOW_SLEEP_SECONDS=5      | +5s no job test                     |
| 5 | sequential | teste lento +10s   | ENABLE_SLOW_TESTS=True, SLOW_SLEEP_SECONDS=10     | +10s no job test                    |
| 6 | sequential | teste falhando     | ENABLE_FAILING_TEST=True                          | pipeline falha                      |
| 7 | sequential | corrigido          | ENABLE_FAILING_TEST=False                         | volta ao normal                     |
| 8 | sequential | sem cache          | cache desabilitado no YAML (não aqui)             | instalação +15-20s                  |
| 9 | sequential | com cache          | cache reabilitado no YAML (não aqui)              | melhora vs execução 8               |
| 10| sequential | +testes            | EXTRA_TEST_MULTIPLIER=5                           | +tempo no job test                  |
| 11| sequential | jobs sequenciais   | todos padrão                                      | baseline sequencial final           |
| 12| parallel   | jobs paralelos     | todos padrão                                      | redução do tempo total              |

---

## Execuções Reais

| # | Workflow      | run_id      | commit                                           | duração (s) | status  | observações                        |
|---|---------------|-------------|--------------------------------------------------|-------------|---------|-------------------------------------|
| 1 | CI Sequential | 27101687780 | feat: initial project setup - baseline           | 69s         | success | push inicial com todos os arquivos |
| 2 | CI Sequential | 27101721791 | chore: baseline run 2 - stability check          | 69s         | success | duração estável confirmada         |
| 3 | CI Sequential | 27101771617 | chore: baseline run 3 - stability check          | 63s         | success | leve variação normal               |
| 4 | CI Sequential | 27101807779 | experiment: enable slow tests with 5s sleep      | 64s         | success | 2 testes lentos x 5s = +10s esperado |
| 5 | CI Sequential | 27101848035 | experiment: increase slow test sleep to 10s      | 87s         | success | +24s vs baseline (2x10s sleep)     |
| 6 | CI Sequential | 27101892323 | experiment: introduce intentional test failure   | 43s         | failure | falha proposital - pipeline parou no job test |
| 7 | CI Sequential | 27101915259 | fix: restore passing tests after failure         | 70s         | success | pipeline restaurado ao normal      |
| 8 | CI Sequential | 27101955674 | experiment: disable pip cache                    | 53s         | success | surpreendentemente rápido - cache já existia no runner |
| 9 | CI Sequential | 27101987231 | experiment: re-enable pip cache                  | 68s         | success | cache reabilitado                  |
| 10| CI Sequential | 27102021587 | experiment: increase test count 5x               | 62s         | success | 5x casos paramétricos (100 testes) |
| 11| CI Sequential | 27102049977 | experiment: sequential jobs baseline             | 59s         | success | baseline para comparação paralelo  |
| 12| CI Parallel   | 27102077969 | experiment: parallel jobs - compare              | 43s         | success | -16s vs run 11 (lint+test paralelos) |

---

## Análise dos Resultados

### Comparação sequencial vs. paralelo (run 11 vs 12)

| Métrica              | Sequencial (run 11) | Paralelo (run 12) | Diferença |
|----------------------|---------------------|-------------------|-----------|
| Duração total        | 59s                 | 43s               | **-16s**  |
| Estrutura            | lint -> test -> build | lint || test -> build | — |

- **Ganho observado:** 16 segundos (27% mais rápido)
- **Hipótese confirmada:** jobs lint e test em paralelo reduzem o tempo total

### Impacto dos testes lentos (run 1-3 vs 4-5)

| Run | SLOW_SLEEP_SECONDS | Duração total | Delta vs baseline |
|-----|-------------------|---------------|-------------------|
| 1-3 | 0 (desabilitado)  | ~67s (média)  | —                 |
| 4   | 5s (x2 testes)    | 64s           | -3s (dentro do ruído) |
| 5   | 10s (x2 testes)   | 87s           | **+20s**          |

- Run 4 (+5s): variação dentro da margem de ruído do runner
- Run 5 (+10s): impacto claro de +20s (2 testes x 10s = 20s de sleep)

### Impacto do cache pip (run 8 vs 9)

| Run | Cache | Duração | Observação |
|-----|-------|---------|------------|
| 8   | OFF   | 53s     | Runner usou cache interno do OS |
| 9   | ON    | 68s     | Cache salvo/restaurado via actions/cache@v4 |

- Resultado inesperado: sem cache foi mais rápido neste experimento
- Possível causa: o runner do GitHub Actions já tinha os pacotes em cache do sistema
  operacional, e o overhead de salvar/restaurar o cache via actions/cache@v4 adicionou tempo

### Falha intencional (run 6 vs 7)

| Run | Resultado | Duração | Observação |
|-----|-----------|---------|------------|
| 6   | failure   | 43s     | Pipeline parou no job test (sem executar build-artifact) |
| 7   | success   | 70s     | Restaurado — build-artifact executou normalmente |

- Duração menor na falha porque o job build-artifact não foi executado

### Volume de testes (run 1-3 vs 10)

| Configuração        | Testes | Duração |
|---------------------|--------|---------|
| MULTIPLIER=1 (base) | 102    | ~67s    |
| MULTIPLIER=5        | 462    | 62s     |

- Aumento de 4.5x nos testes sem impacto significativo na duração
- Indica que o overhead de setup/teardown domina o tempo, não a execução dos testes

---

## Como alterar experiment_config.py entre execuções

### Experimento 4 — Slow tests +5s
```python
ENABLE_SLOW_TESTS: bool = True
SLOW_SLEEP_SECONDS: int = 5
ENABLE_FAILING_TEST: bool = False
EXTRA_TEST_MULTIPLIER: int = 1
```

### Experimento 5 — Slow tests +10s
```python
ENABLE_SLOW_TESTS: bool = True
SLOW_SLEEP_SECONDS: int = 10
ENABLE_FAILING_TEST: bool = False
EXTRA_TEST_MULTIPLIER: int = 1
```

### Experimento 6 — Teste falhando
```python
ENABLE_SLOW_TESTS: bool = False
SLOW_SLEEP_SECONDS: int = 0
ENABLE_FAILING_TEST: bool = True
EXTRA_TEST_MULTIPLIER: int = 1
```

### Experimento 7 — Corrigido
```python
ENABLE_SLOW_TESTS: bool = False
SLOW_SLEEP_SECONDS: int = 0
ENABLE_FAILING_TEST: bool = False
EXTRA_TEST_MULTIPLIER: int = 1
```

### Experimento 10 — Volume de testes
```python
ENABLE_SLOW_TESTS: bool = False
SLOW_SLEEP_SECONDS: int = 0
ENABLE_FAILING_TEST: bool = False
EXTRA_TEST_MULTIPLIER: int = 5
```

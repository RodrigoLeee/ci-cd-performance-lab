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

### Experimento 8 — Sem cache (alterar ci-sequential.yml)
Remover o bloco `cache@v4` dos 3 jobs em `.github/workflows/ci-sequential.yml`.
`experiment_config.py` permanece com valores padrão.

### Experimento 9 — Com cache (restaurar ci-sequential.yml)
Restaurar o bloco `cache@v4` que foi removido no experimento 8.

### Experimento 10 — Volume de testes
```python
ENABLE_SLOW_TESTS: bool = False
SLOW_SLEEP_SECONDS: int = 0
ENABLE_FAILING_TEST: bool = False
EXTRA_TEST_MULTIPLIER: int = 5
```

### Experimentos 11-12 — Baseline final e paralelo
Restaurar todos os valores padrão. Para o experimento 12, garantir que o
push ative o workflow `ci-parallel.yml` (verificar triggers).

---

## Execuções Reais

<!-- Preencher após cada execução -->

| # | run_id | commit | duração real (s) | status | observações |
|---|--------|--------|-----------------|--------|-------------|
| 1 |        |        |                 |        |             |
| 2 |        |        |                 |        |             |
| 3 |        |        |                 |        |             |
| 4 |        |        |                 |        |             |
| 5 |        |        |                 |        |             |
| 6 |        |        |                 |        |             |
| 7 |        |        |                 |        |             |
| 8 |        |        |                 |        |             |
| 9 |        |        |                 |        |             |
| 10|        |        |                 |        |             |
| 11|        |        |                 |        |             |
| 12|        |        |                 |        |             |

---

## Análise Esperada

### Comparação sequencial vs. paralelo (exp 11 vs 12)

- No sequencial: `t_total = t_lint + t_test + t_build`
- No paralelo: `t_total = max(t_lint, t_test) + t_build`
- Ganho esperado: ≈ `min(t_lint, t_test)` segundos

### Impacto do cache (exp 8 vs 9)

- Sem cache: cada job instala dependências do zero (~15-20s adicionais por job)
- Com cache: hit de cache reduz instalação para ~2-3s

### Impacto dos testes lentos (exp 1-3 vs 4-5)

- Baseline: tempo de teste controlado pelos ~65 casos de teste normais
- Com sleep 5s: +5s por teste lento (2 testes = +10s totais)
- Com sleep 10s: +10s por teste lento (2 testes = +20s totais)

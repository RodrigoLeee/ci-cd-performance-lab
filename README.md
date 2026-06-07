# ci-cd-performance-lab

Biblioteca de cálculos financeiros usada como base para um experimento acadêmico de CI/CD
no GitHub Actions. O objetivo é gerar execuções reais com variações controladas, coletar
métricas e analisar o desempenho do pipeline.

---

## Estrutura do repositório

```
ci-cd-performance-lab/
├── src/
│   ├── calculator.py      # FinancialCalculator — 10 métodos de cálculo financeiro
│   ├── validator.py       # FinancialValidator — validações e CPF/CNPJ
│   └── portfolio.py       # Portfolio — gestão de carteira de investimentos
│
├── tests/
│   ├── experiment_config.py   # ← ÚNICO arquivo alterado entre experimentos
│   ├── test_calculator.py     # ~30 testes unitários
│   ├── test_validator.py      # ~20 testes unitários
│   ├── test_portfolio.py      # ~15 testes unitários
│   ├── test_parametrized.py   # testes paramétricos (volume controlado)
│   └── test_slow.py           # testes com sleep controlado + falha intencional
│
├── scripts/
│   ├── collect_metrics.py     # coleta métricas via API do GitHub
│   └── generate_charts.py     # gera os 4 gráficos de análise
│
├── reports/                   # gráficos gerados (PNG)
├── data/                      # métricas coletadas (CSV, JSON)
│
└── .github/workflows/
    ├── ci-sequential.yml      # lint → test → build (sequencial)
    └── ci-parallel.yml        # lint ‖ test → build (paralelo)
```

---

## Instalação local

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Rodar todos os testes
pytest tests/

# Rodar com cobertura
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Como reproduzir o experimento

O experimento consiste em **12 execuções** no GitHub Actions com variações controladas.
O único arquivo alterado entre experimentos é `tests/experiment_config.py`.

### Tabela das 12 execuções

| # | Workflow    | Variação            | O que muda                                        | Hipótese                           |
|---|-------------|---------------------|---------------------------------------------------|------------------------------------|
| 1 | sequential  | baseline            | valores padrão em experiment_config.py            | duração estável ~25s               |
| 2 | sequential  | baseline            | valores padrão (repetição)                        | confirmar estabilidade             |
| 3 | sequential  | baseline            | valores padrão (repetição)                        | confirmar estabilidade             |
| 4 | sequential  | teste lento +5s     | `ENABLE_SLOW_TESTS=True`, `SLOW_SLEEP_SECONDS=5`  | +5s no job test                    |
| 5 | sequential  | teste lento +10s    | `ENABLE_SLOW_TESTS=True`, `SLOW_SLEEP_SECONDS=10` | +10s no job test                   |
| 6 | sequential  | teste falhando      | `ENABLE_FAILING_TEST=True`                        | pipeline falha no job test         |
| 7 | sequential  | corrigido           | `ENABLE_FAILING_TEST=False`                       | pipeline volta ao normal           |
| 8 | sequential  | sem cache           | remover bloco `cache@v4` do YAML                  | instalação +15-20s por job         |
| 9 | sequential  | com cache           | restaurar bloco `cache@v4` no YAML                | melhora de tempo vs execução 8     |
| 10| sequential  | volume de testes    | `EXTRA_TEST_MULTIPLIER=5`                         | +tempo no job test (~5x mais casos)|
| 11| sequential  | jobs sequenciais    | valores padrão (baseline sequencial final)        | referência para comparação         |
| 12| parallel    | jobs paralelos      | valores padrão + workflow ci-parallel.yml         | redução do tempo total             |

### Passo a passo

```bash
# Experimento 1-3: commit com valores padrão, push 3 vezes
git add tests/experiment_config.py
git commit -m "exp1: baseline pipeline"
git push

# Experimento 4: editar experiment_config.py e commitar
# ENABLE_SLOW_TESTS = True
# SLOW_SLEEP_SECONDS = 5
git add tests/experiment_config.py
git commit -m "exp4: slow tests +5s"
git push

# ... e assim por diante conforme a tabela acima
```

---

## Como coletar as métricas

```bash
export GITHUB_TOKEN=seu_personal_access_token
export GITHUB_OWNER=seu_usuario_github
export GITHUB_REPO=ci-cd-performance-lab

python scripts/collect_metrics.py
```

O script salva os arquivos:
- `data/metrics.csv` — uma linha por job por execução
- `data/metrics.json` — mesmo conteúdo em formato JSON
- `data/steps_detail.csv` — uma linha por step por job

O token precisa de permissão `repo` (ou `actions:read` em repositórios públicos).

---

## Como gerar os gráficos

```bash
python scripts/generate_charts.py
```

Gera 4 arquivos em `reports/`:

| Arquivo                          | Conteúdo                                               |
|----------------------------------|--------------------------------------------------------|
| `chart_01_pipeline_duration.png` | Duração total por execução (linha + pontos coloridos)  |
| `chart_02_job_duration.png`      | Duração por job em cada execução (barras agrupadas)    |
| `chart_03_success_rate.png`      | Taxa de sucesso/falha (pizza + barras por workflow)    |
| `chart_04_tests_vs_duration.png` | Correlação testes × duração (scatter + tendência)      |

---

## Workflows disponíveis

### `ci-sequential.yml` — CI Sequential

Jobs executam **em sequência**: `lint` → `test` → `build-artifact`.
Cada job aguarda o anterior com `needs:`.

- **Vantagem:** simples de depurar, falha clara por etapa.
- **Desvantagem:** tempo total = soma dos tempos de cada job.

### `ci-parallel.yml` — CI Parallel

Jobs `lint` e `test` executam **em paralelo** (sem `needs:` entre eles).
O job `build-artifact` aguarda ambos com `needs: [lint, test]`.

- **Vantagem:** tempo total ≈ max(lint, test) em vez de lint + test.
- **Desvantagem:** consome 2 runners simultaneamente.

---

## Dependências

| Pacote          | Versão  | Uso                              |
|-----------------|---------|----------------------------------|
| pytest          | 8.2.2   | framework de testes              |
| pytest-cov      | 5.0.0   | cobertura de código              |
| flake8          | 7.1.0   | linting de estilo                |
| requests        | 2.32.3  | API do GitHub em collect_metrics |
| pandas          | 2.2.2   | manipulação de dados CSV         |
| matplotlib      | 3.9.0   | geração dos gráficos             |
| python-dotenv   | 1.0.1   | leitura de .env para o token     |
# baseline run 2
# baseline run 3

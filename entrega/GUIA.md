# Guia de Entrega — CI/CD Performance Lab

Este guia descreve o que está pronto, o que falta e como completar cada item antes de entregar.

---

## O que está nesta pasta

| Arquivo | O que é |
|---|---|
| `RELATORIO.md` | Relatório técnico completo — responde todas as perguntas do enunciado |
| `ci-sequential.yml` | YAML do pipeline sequencial (cópia de `.github/workflows/`) |
| `ci-parallel.yml` | YAML do pipeline paralelo (cópia de `.github/workflows/`) |
| `GUIA.md` | Este arquivo |

---

## Checklist final do enunciado

### Entregáveis

- [x] Link do repositório GitHub
- [x] Link dos arquivos YAML do GitHub Actions (copiados nesta pasta e linkados no relatório)
- [x] Script de coleta das métricas (`scripts/collect_metrics.py`)
- [x] Base de dados gerada em CSV e JSON (`data/metrics.csv`, `data/metrics.json`)
- [x] Gráficos produzidos — 4 gráficos em `reports/`, já inseridos no `RELATORIO.md`
- [x] Relatório técnico em Markdown (`RELATORIO.md`)
- [x] Explicação de como reproduzir o experimento (seção 10 do relatório)

### Requisitos obrigatórios do relatório

- [x] Prints ou links das execuções reais do GitHub Actions
- [x] IDs reais dos workflows executados (tabela na seção 4)
- [x] Commits reais usados no experimento
- [x] Explicação das variações feitas entre execuções
- [x] Gráficos gerados a partir dos dados coletados (seção 6)
- [x] Análise de pelo menos dois resultados inesperados (seção 8)
- [x] Comparação entre hipótese inicial e resultado observado (seção 9)
- [x] Discussão sobre limitações do experimento (seção 7.7)

---

## Sobre o número de runs no GitHub Actions

A aba Actions exibe mais de 12 runs porque ambos os workflows (`CI Sequential` e
`CI Parallel`) disparam em todo push — inclusive em commits administrativos feitos
após o experimento (push dos resultados coletados, ajustes no repositório).

### Distribuição real dos runs

| Workflow | Runs experimentais | Runs extras (commits pós-experimento) | Total |
|---|---|---|---|
| CI Sequential | 12 | 5 | 17 |
| CI Parallel | 12 | 5 | 17 |
| **Total** | **24** | **10** | **34** |

### Os 12 runs experimentais do CI Sequential (únicos analisados no relatório)

| # | Run ID | Commit | Variação |
|---|--------|--------|---------|
| 1 | 27101687780 | `011e972b` | baseline inicial |
| 2 | 27101721791 | `c3fe74eb` | baseline repetição |
| 3 | 27101771617 | `ad5c4513` | baseline repetição |
| 4 | 27101807779 | `ac957c6d` | slow tests +5s |
| 5 | 27101848035 | `ccdf92a7` | slow tests +10s |
| 6 | 27101892323 | `2cf6515b` | falha intencional |
| 7 | 27101915259 | `a08454fc` | correção |
| 8 | 27101955674 | `cacadf83` | sem cache |
| 9 | 27101987231 | `bc476b10` | com cache |
| 10 | 27102021587 | `b71a7291` | 5× testes |
| 11 | 27102049977 | `87a44449` | sequential baseline |
| 12 | 27102077969 | `934da934` | **CI Parallel** |

---

## Prints pendentes

Os placeholders abaixo já estão nos lugares certos no RELATORIO.md.
Salvar os prints na pasta `entrega/prints/` e o relatório os exibirá automaticamente.

| Print | URL para capturar | Nome do arquivo |
|---|---|---|
| Lista das runs | https://github.com/RodrigoLeee/ci-cd-performance-lab/actions/workflows/ci-sequential.yml | `prints/actions-lista-runs.png` |
| Run 6 — falha | https://github.com/RodrigoLeee/ci-cd-performance-lab/actions/runs/27101892323 | `prints/run-6-failure.png` |
| Run 12 — paralelo | https://github.com/RodrigoLeee/ci-cd-performance-lab/actions/runs/27102077969 | `prints/run-12-parallel.png` |

---

## Links rápidos

| Destino | URL |
|---|---|
| Repositório | https://github.com/RodrigoLeee/ci-cd-performance-lab |
| Actions (todas as runs) | https://github.com/RodrigoLeee/ci-cd-performance-lab/actions |
| Filtrar CI Sequential | https://github.com/RodrigoLeee/ci-cd-performance-lab/actions/workflows/ci-sequential.yml |
| Filtrar CI Parallel | https://github.com/RodrigoLeee/ci-cd-performance-lab/actions/workflows/ci-parallel.yml |
| Run 6 — falha intencional | https://github.com/RodrigoLeee/ci-cd-performance-lab/actions/runs/27101892323 |
| Run 12 — paralelo | https://github.com/RodrigoLeee/ci-cd-performance-lab/actions/runs/27102077969 |
| metrics.csv | https://github.com/RodrigoLeee/ci-cd-performance-lab/blob/main/data/metrics.csv |

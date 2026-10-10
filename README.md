# rust-wasm

Análise comparativa de desempenho entre execução nativa e WebAssembly em navegadores utilizando Rust.

## Requisitos

- [Docker](https://www.docker.com/)
- [Python](https://www.python.org/downloads/)

## Configuração

```bash
chmod +x ./stats.sh
chmod +x ./collect-stats.sh
```

## Execução dos benchmarks

```bash
./stats.sh
```

## Scripts Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 ./scripts/generate_chart.py ./stats/2026-08-16_16-30.json
python3 ./scripts/generate_chart_process.py ./stats/2026-08-16_16-30.json
python3 ./scripts/analyze_stats.py ./stats/2026-08-16_16-30.json
```

### Resultados do TCC

Os valores do TCC (tabelas de tempo e memória, Apêndice A, métricas de coleta e análise de sensibilidade) são gerados a partir das coletas de 09/10/2026 dos três computadores, que registram o tempo de cada execução:

```bash
python3 ./scripts/analyze_stats.py \
  ./stats/2026-10-09_21-09.json \
  ./stats/2026-10-09_21-14.json
```

O gráfico do fator Wasm/nativo por algoritmo (um ponto por computador e a média geométrica) é gerado a partir das mesmas coletas:

```bash
python3 ./scripts/generate_factor_chart.py \
  ./stats/2026-10-09_21-09.json \
  ./stats/2026-10-09_21-14.json \
  --output ./charts/tcc/fator-por-algoritmo.png
```

Para cada computador, o `analyze_stats.py` usa a mediana das execuções de cada algoritmo e calcula o desvio padrão. O overhead é calculado por computador e consolidado pela média geométrica dos fatores; a memória é consolidada pela média aritmética. Coletas anteriores, que registram apenas o tempo médio, não são aceitas.

## Adicionando um algoritmo

1. Criar `rust/src/nome_do_algoritmo.rs` com a função `pub fn run(...)`
2. Em `rust/src/lib.rs` adicione `pub mod nome_do_algoritmo;` e o export dentro de `mod wasm_exports`
3. Adicionar a medição em `rust/benches/benchmarks.rs`
4. Adicionar a chamada em `javascript/web/index.html`
5. Configure os parâmetros no `config.json`

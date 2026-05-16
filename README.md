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

## Adicionando um algoritmo

1. Criar `rust/src/nome_do_algoritmo.rs` com a função `pub fn run(...)`
2. Adicionar `pub mod nome_do_algoritmo;` em `rust/src/lib.rs`
3. Adicionar o export em `rust/src/lib.rs` dentro de `mod wasm_exports`
4. Adicionar a medição em `rust/benches/benchmarks.rs`
5. Adicionar a chamada em `javascript/web/index.html`
6. Configure os parâmetros no `config.json`

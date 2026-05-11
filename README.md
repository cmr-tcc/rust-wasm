# rust-wasm

Análise comparativa de desempenho entre execução nativa e WebAssembly em navegadores utilizando Rust.

## Requisitos

- [Rust](https://rustup.rs/)
- [wasm-pack](https://rustwasm.github.io/wasm-pack/installer/)
- [Node.js](https://nodejs.org/)

## Primeira execução

```bash
bash build.sh
```

## Rodando os benchmarks

**Nativo:**
```bash
cargo bench --bench benchmarks
```

**WebAssembly:**
```bash
npm run bench
```

> Após qualquer alteração no código Rust, rode `bash build.sh` novamente antes de `npm run bench`.

## Adicionando um algoritmo

1. Criar `src/nome_do_algoritmo.rs` com a função `pub fn run(...)`
2. Adicionar `pub mod nome_do_algoritmo;` em `src/lib.rs`
3. Adicionar o export em `src/lib.rs` dentro de `mod wasm_exports`
4. Adicionar a medição em `benches/benchmarks.rs`
5. Adicionar a chamada em `web/index.html`

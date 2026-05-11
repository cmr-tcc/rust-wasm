#!/bin/bash
set -e

echo "Compilando para WebAssembly..."
wasm-pack build --target web --out-dir web/pkg

echo "Instalando dependências Node..."
npm install

echo "Pronto. Para rodar os benchmarks:"
echo "  Nativo: cargo bench --bench benchmarks"
echo "  Wasm:   npm run bench"

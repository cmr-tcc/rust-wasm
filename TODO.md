- Parece que compila antes de toda execução Rust, isso pode impactar no resultado

- Limitado no `collect-stats.sh` para 1 thread (`RAYON_NUM_THREADS=1`), pois no Wasm não foi possível compilar com o `wasm-bindgen-rayon`, necessário para usar multi-thread no browser

- Avaliar impacto do `wasm_jit`, mudar nome para `warm_up` e avaliar no Rust também

- Avaliar outras métricas como percentile e mediana ao invés de média no tempo de execução

- No Wasm a performance é feita no lado do JavaScript, o que inclui a sobrecarga de passar o controle para o Rust. Testar medir na função `run` do algoritmo e o retorno ser o tempo gasto

- Tentar limitar a 1 CPU no container para ver se vai passar de 100% de uso de CPU
fn main() {
    let mean_ms = rust_wasm::bench::measure(|| {
        rust_wasm::fibonacci::run(40);
    }, 200);

    println!(r#"[{{"algorithm":"fibonacci","input":40,"mean_ms":{mean_ms:.3}}}]"#);
}

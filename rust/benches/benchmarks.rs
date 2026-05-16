use std::env;

fn benchmark_fibonacci(iterations: usize) {
    let mean_ms = rust_wasm::bench::measure(|| {
        rust_wasm::fibonacci::run(40);
    }, iterations);

    println!(r#"{{"mean_ms":{mean_ms:.3}}}"#);
}

fn benchmark_double(iterations: usize) {
    let mean_ms = rust_wasm::bench::measure(|| {
        rust_wasm::double::run(40);
    }, iterations);

    println!(r#"{{"mean_ms":{mean_ms:.3}}}"#);
}

fn main() {
    let algorithm = env::args()
        .nth(1)
        .expect("missing algorithm argument");

    let iterations = env::args()
        .nth(2)
        .expect("missing iterations argument")
        .parse()
        .expect("iterations must be a number");

    match algorithm.as_str() {
        "fibonacci" => benchmark_fibonacci(iterations),
        "double" => benchmark_double(iterations),
        _ => panic!("unknown algorithm: {}", algorithm),
    }
}
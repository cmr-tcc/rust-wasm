use std::env;

fn benchmark_fibonacci(iterations: usize, parameter: u64) {
    let mean_ms = rust_wasm::bench::measure(|| {
        rust_wasm::fibonacci::run(parameter);
    }, iterations);

    println!(r#"{{"mean_ms":{mean_ms:.3}}}"#);
}

fn benchmark_double(iterations: usize, parameter: u64) {
    let mean_ms = rust_wasm::bench::measure(|| {
        rust_wasm::double::run(parameter);
    }, iterations);

    println!(r#"{{"mean_ms":{mean_ms:.3}}}"#);
}

fn benchmark_nsieve(iterations: usize, parameter: u64) {
    let mean_ms = rust_wasm::bench::measure(|| {
        rust_wasm::nsieve::run(parameter);
    }, iterations);

    println!(r#"{{"mean_ms":{mean_ms:.3}}}"#);
}

fn benchmark_fannkuch_redux(iterations: usize, parameter: u64) {
    let mean_ms = rust_wasm::bench::measure(|| {
        rust_wasm::fannkuch_redux::run(parameter);
    }, iterations);

    println!(r#"{{"mean_ms":{mean_ms:.3}}}"#);
}

fn benchmark_n_body(iterations: usize, parameter: u64) {
    let mean_ms = rust_wasm::bench::measure(|| {
        rust_wasm::n_body::run(parameter);
    }, iterations);

    println!(r#"{{"mean_ms":{mean_ms:.3}}}"#);
}

fn benchmark_spectral_norm(iterations: usize, parameter: u64) {
    let mean_ms = rust_wasm::bench::measure(|| {
        rust_wasm::spectral_norm::main(parameter);
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

    let parameter = env::args()
        .nth(3)
        .expect("missing parameter argument")
        .parse()
        .expect("parameter must be a number");

    match algorithm.as_str() {
        "fibonacci" => benchmark_fibonacci(iterations, parameter),
        "double" => benchmark_double(iterations, parameter),
        "nsieve" => benchmark_nsieve(iterations, parameter),
        "fannkuch_redux" => benchmark_fannkuch_redux(iterations, parameter),
        "n_body" => benchmark_n_body(iterations, parameter),
        "spectral_norm" => benchmark_spectral_norm(iterations, parameter),
        _ => panic!("unknown algorithm: {}", algorithm),
    }
}

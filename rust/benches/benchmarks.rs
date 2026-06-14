use std::env;
use std::thread;
use std::time::Duration;

fn benchmark_fibonacci(iterations: usize, parameter: u64) {
    let mean_ms = rust_wasm::bench::measure(|| {
        rust_wasm::fibonacci::run(parameter);
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

fn benchmark_mandelbrot(iterations: usize, parameter: u64) {
    let mean_ms = rust_wasm::bench::measure(|| {
        rust_wasm::mandelbrot::main(parameter);
    }, iterations);

    println!(r#"{{"mean_ms":{mean_ms:.3}}}"#);
}

fn benchmark_fasta(iterations: usize, parameter: u64) {
    let mean_ms = rust_wasm::bench::measure(|| {
        rust_wasm::fasta::main(parameter);
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

    thread::sleep(Duration::from_secs(10)); // 10 seconds in idle to measure resource usage in stand-by

    match algorithm.as_str() {
        "fibonacci" => benchmark_fibonacci(iterations, parameter),
        "fannkuch_redux" => benchmark_fannkuch_redux(iterations, parameter),
        "n_body" => benchmark_n_body(iterations, parameter),
        "spectral_norm" => benchmark_spectral_norm(iterations, parameter),
        "mandelbrot" => benchmark_mandelbrot(iterations, parameter),
        "fasta" => benchmark_fasta(iterations, parameter),
        _ => panic!("unknown algorithm: {}", algorithm),
    }

    thread::sleep(Duration::from_secs(10)); // 10 seconds in idle to measure resource usage in stand-by
}

use std::env;
use std::thread;
use std::time::Duration;

fn print_measurements(times: &[f64]) {
    let measurements = times
        .iter()
        .map(|time| format!("{time:.3}"))
        .collect::<Vec<_>>()
        .join(",");

    println!(r#"{{"times":[{measurements}]}}"#);
}

fn benchmark_fibonacci(iterations: usize, parameter: u64, warm_up: usize) {
    for _ in 0..warm_up {
        rust_wasm::fibonacci::run(parameter);
    }

    let times = rust_wasm::bench::measure(
        || {
            rust_wasm::fibonacci::run(parameter);
        },
        iterations,
    );

    print_measurements(&times);
}

fn benchmark_fannkuch_redux(iterations: usize, parameter: u64, warm_up: usize) {
    for _ in 0..warm_up {
        rust_wasm::fannkuch_redux::run(parameter);
    }

    let times = rust_wasm::bench::measure(
        || {
            rust_wasm::fannkuch_redux::run(parameter);
        },
        iterations,
    );

    print_measurements(&times);
}

fn benchmark_n_body(iterations: usize, parameter: u64, warm_up: usize) {
    for _ in 0..warm_up {
        rust_wasm::n_body::run(parameter);
    }

    let times = rust_wasm::bench::measure(
        || {
            rust_wasm::n_body::run(parameter);
        },
        iterations,
    );

    print_measurements(&times);
}

fn benchmark_spectral_norm(iterations: usize, parameter: u64, warm_up: usize) {
    for _ in 0..warm_up {
        rust_wasm::spectral_norm::main(parameter);
    }

    let times = rust_wasm::bench::measure(
        || {
            rust_wasm::spectral_norm::main(parameter);
        },
        iterations,
    );

    print_measurements(&times);
}

fn benchmark_mandelbrot(iterations: usize, parameter: u64, warm_up: usize) {
    for _ in 0..warm_up {
        rust_wasm::mandelbrot::main(parameter);
    }

    let times = rust_wasm::bench::measure(
        || {
            rust_wasm::mandelbrot::main(parameter);
        },
        iterations,
    );

    print_measurements(&times);
}

fn benchmark_fasta(iterations: usize, parameter: u64, warm_up: usize) {
    for _ in 0..warm_up {
        rust_wasm::fasta::main(parameter);
    }

    let times = rust_wasm::bench::measure(
        || {
            rust_wasm::fasta::main(parameter);
        },
        iterations,
    );

    print_measurements(&times);
}

fn main() {
    let algorithm = env::args().nth(1).expect("missing algorithm argument");

    let iterations = env::args()
        .nth(2)
        .expect("missing iterations argument")
        .parse()
        .expect("iterations must be a number");

    let warm_up = env::args()
        .nth(3)
        .expect("missing warm-up argument")
        .parse()
        .expect("warm-up must be a number");

    let parameter = env::args()
        .nth(4)
        .expect("missing parameter argument")
        .parse()
        .expect("parameter must be a number");

    thread::sleep(Duration::from_secs(10)); // 10 seconds in idle to measure resource usage in stand-by

    match algorithm.as_str() {
        "fibonacci" => benchmark_fibonacci(iterations, parameter, warm_up),
        "fannkuch_redux" => benchmark_fannkuch_redux(iterations, parameter, warm_up),
        "n_body" => benchmark_n_body(iterations, parameter, warm_up),
        "spectral_norm" => benchmark_spectral_norm(iterations, parameter, warm_up),
        "mandelbrot" => benchmark_mandelbrot(iterations, parameter, warm_up),
        "fasta" => benchmark_fasta(iterations, parameter, warm_up),
        _ => panic!("unknown algorithm: {}", algorithm),
    }

    thread::sleep(Duration::from_secs(10)); // 10 seconds in idle to measure resource usage in stand-by
}

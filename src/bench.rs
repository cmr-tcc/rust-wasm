use std::time::Instant;

pub fn measure<F: FnMut()>(mut function: F, runs: usize) -> f64 {
    let start = Instant::now();

    for _ in 0..runs {
        function();
    }

    let total_ms = start.elapsed().as_micros() as f64 / 1000.0;

    total_ms / runs as f64
}

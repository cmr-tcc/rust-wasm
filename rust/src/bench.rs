use std::time::Instant;

pub fn measure<F: FnMut()>(mut function: F, runs: usize) -> Vec<f64> {
    let mut times = Vec::with_capacity(runs);

    for _ in 0..runs {
        let start = Instant::now();
        function();
        times.push(start.elapsed().as_secs_f64() * 1000.0);
    }

    times
}

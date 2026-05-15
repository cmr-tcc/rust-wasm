pub fn run(n: u64) -> u64 {
    match n {
        0 => 0,
        1 => 1,
        _ => run(n - 1) + run(n - 2),
    }
}

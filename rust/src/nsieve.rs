pub fn run(limit: u64) -> u64 {
    let limit = limit as usize; // um tipo pra índice de vetor ou posições de memória

    if limit < 2 {
        return 0;
    }

    let mut is_prime = vec![true; limit + 1];
    is_prime[0] = false;
    is_prime[1] = false;

    let sqrt_limit = (limit as f64).sqrt() as usize;

    for p in 2..=sqrt_limit {
        if !is_prime[p] {
            continue;
        }

        let mut multiple = p * p;
        while multiple <= limit {
            is_prime[multiple] = false;
            multiple += p;
        }
    }

    is_prime.iter().skip(2).filter(|&&x| x).count() as u64
}

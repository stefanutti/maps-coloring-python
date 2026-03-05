import timeit
from statistics import mean

# -----------------------------
# Configurazione del benchmark
# -----------------------------
NUM_KEYS = 1000          # dimensione del dizionario
LOOKUP_KEY_INT = 500     # chiave da cercare (int)
LOOKUP_KEY_STR = "500"    # chiave da cercare (str)
REPEAT = 50               # numero di ripetizioni
NUMBER = 5000000         # lookup per ripetizione


def build_dicts(n):
    """Crea due dizionari identici:
    - uno con chiavi intere
    - uno con chiavi stringa
    """
    d_int = {i: i for i in range(n)}
    d_str = {str(i): i for i in range(n)}
    return d_int, d_str


def benchmark_lookup(stmt, setup, repeat=REPEAT, number=NUMBER):
    """Esegue timeit.repeat e restituisce i tempi."""
    times = timeit.repeat(stmt, setup=setup, repeat=repeat, number=number)
    return times


def print_results(label, times):
    """Stampa statistiche base."""
    print(f"{label}")
    print(f"  run times : {[round(t, 4) for t in times]}")
    print(f"  mean time : {mean(times):.4f} s")
    print()


def main():
    print("\n=== Benchmark accesso dict ===\n")
    print(f"Dimensione dizionario : {NUM_KEYS}")
    print(f"Lookup per run        : {NUMBER:,}")
    print(f"Ripetizioni           : {REPEAT}\n")

    # Setup condiviso
    setup_code = f"""
d_int = {{i: i for i in range({NUM_KEYS})}}
d_str = {{str(i): i for i in range({NUM_KEYS})}}
"""

    # Benchmark lookup int
    times_int = benchmark_lookup(
        stmt=f"d_int[{LOOKUP_KEY_INT}]",
        setup=setup_code
    )

    # Benchmark lookup str
    times_str = benchmark_lookup(
        stmt=f"d_str['{LOOKUP_KEY_STR}']",
        setup=setup_code
    )

    # Stampa risultati
    print_results("Chiavi intere (int):", times_int)
    print_results("Chiavi stringa (str):", times_str)

    # Confronto finale
    ratio = mean(times_str) / mean(times_int)
    print("=== Confronto ===")
    print(f"str / int ratio ≈ {ratio:.3f}")

    if ratio > 1:
        print("→ int leggermente più veloce")
    else:
        print("→ str leggermente più veloce (raro)")
    print()


if __name__ == "__main__":
    main()

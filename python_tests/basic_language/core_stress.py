#!/usr/bin/env python3
import argparse
import math
import os
import time
from multiprocessing import Process, Event, cpu_count


def burn(stop_event: Event) -> None:
    """ciclo cpu-bound continuo finché stop_event non viene settato."""
    x = 0.0
    # lavoro numerico leggero ma continuo
    while not stop_event.is_set():
        # qualche operazione in virgola mobile per evitare ottimizzazioni
        x = math.sin(x + 1.2345) * math.cos(x + 0.9876) + math.sqrt(12345.6789)
        # un controllo ogni tanto per consentire lo stop pulito
        # (il calcolo resta 100% cpu-bound)
        # niente sleep qui: vogliamo tenere la cpu occupata


def main():
    parser = argparse.ArgumentParser(
        description="stressor cpu a processi multipli"
    )
    parser.add_argument(
        "-p", "--processes",        type=int,
        default=cpu_count(),
        help="numero di processi da avviare (default: tutti i core logici)"
    )
    parser.add_argument(
        "-d", "--duration",
        type=float,
        default=0,
        help="durata in secondi (0 = infinito finché non interrompi)"
    )
    args = parser.parse_args()

    procs = []
    stop_event = Event()

    try:
        for _ in range(max(1, args.processes)):
            p = Process(target=burn, args=(stop_event,), daemon=True)
            p.start()
            procs.append(p)

        if args.duration > 0:
            time.sleep(args.duration)
        else:
            # resta in attesa finché non riceve ctrl+c
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        for p in procs:
            p.join(timeout=2)


if __name__ == "__main__":
    main()

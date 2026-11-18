#!/usr/bin/env python3
"""Run a long job with cool-down breaks: pause it when the CPU gets hot, and for a few minutes
every hour, so the computer is not held at full heat for hours on end.

    python3 tools/cool_guard.py --log logs/cool.log -- python3 -m tamtrain train ...   # run a command
    python3 tools/cool_guard.py --pid 12345 --log logs/cool.log                        # guard a running job

The job and every process it started are paused with SIGSTOP and resumed with SIGCONT, so no
work is lost; a pause only adds wall-clock time (and to any seconds-per-iteration the job
measures itself). The temperature is the CPU package sensor (coretemp "Package id 0"), read
every few seconds. If this guard is stopped, it resumes the job first.

To switch the guard off for a while without touching the job, create the --off-file (the guard
resumes the job and only watches); delete it to switch the guard back on. Never freeze the guard
itself with SIGSTOP: a shell waiting on it may treat that as the job ending and stop everything.
With --pid the guard is a separate process, and stopping it never stops the job.

The package sensor swings fast (on a 4-core desktop CPU: 47 -> 63 °C six seconds after load starts, back
down within a second of stopping), so the pause is decided on the average of the last --window
seconds, an instant reading only triggers above --hard, and every pause lasts at least
--min-pause so the heatsink cools too, not just the chip.
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


def cpu_temp() -> float | None:
    """CPU package temperature in °C, or the hottest core, or None without a sensor."""
    for h in sorted(Path("/sys/class/hwmon").glob("hwmon*")):
        try:
            if (h / "name").read_text().strip() != "coretemp":
                continue
        except OSError:
            continue
        temps = {}
        for f in h.glob("temp*_input"):
            label = f.with_name(f.name.replace("_input", "_label"))
            try:
                temps[label.read_text().strip() if label.exists() else f.name] = int(f.read_text()) / 1000
            except (OSError, ValueError):
                continue
        if temps:
            return temps.get("Package id 0", max(temps.values()))
    for z in sorted(Path("/sys/class/thermal").glob("thermal_zone*")):
        try:
            if (z / "type").read_text().strip() == "x86_pkg_temp":
                return int((z / "temp").read_text()) / 1000
        except (OSError, ValueError):
            continue
    return None


def process_tree(root: int) -> list[int]:
    """root and all its descendants, parents before children."""
    children: dict[int, list[int]] = {}
    for p in Path("/proc").iterdir():
        if not p.name.isdigit():
            continue
        try:
            ppid = int((p / "stat").read_text().rsplit(")", 1)[1].split()[1])
        except (OSError, ValueError, IndexError):
            continue
        children.setdefault(ppid, []).append(int(p.name))
    out, todo = [], [root]
    while todo:
        pid = todo.pop(0)
        out.append(pid)
        todo += children.get(pid, [])
    return out


def signal_tree(root: int, sig: int) -> int:
    done: set[int] = set()
    for _ in range(2):                    # a second pass catches a child started during the first
        for pid in process_tree(root):
            if pid in done:
                continue
            try:
                os.kill(pid, sig)
                done.add(pid)
            except ProcessLookupError:
                pass
    return len(done)


def alive(pid: int) -> bool:
    try:
        state = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
    except (OSError, IndexError):
        return False
    return state != "Z"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hot", type=float, default=80,
                    help="pause when the average CPU temperature over --window reaches this, in °C "
                         "(Intel desktop sensors mark 80 as high, 100 as critical)")
    ap.add_argument("--hard", type=float, default=85, help="pause at once when a single reading reaches this")
    ap.add_argument("--window", type=float, default=30, help="seconds of readings averaged for --hot")
    ap.add_argument("--cool", type=float, default=60, help="resume once the CPU is down to this")
    ap.add_argument("--min-pause", type=float, default=120, help="seconds every heat pause lasts at least")
    ap.add_argument("--break-every", type=float, default=60, help="minutes of work between scheduled breaks (0: none)")
    ap.add_argument("--break-for", type=float, default=5, help="minutes per scheduled break")
    ap.add_argument("--check", type=float, default=5, help="seconds between temperature readings")
    ap.add_argument("--report", type=float, default=15, help="minutes between status lines")
    ap.add_argument("--pid", type=int, help="guard this running process (and its children) instead of a command")
    ap.add_argument("--log", type=Path, help="write the guard's messages here (default: stderr)")
    ap.add_argument("--off-file", type=Path, help="while this file exists the guard does not pause the job")
    ap.add_argument("command", nargs=argparse.REMAINDER, help="-- command to run")
    args = ap.parse_args()
    cmd = args.command[1:] if args.command[:1] == ["--"] else args.command
    if bool(cmd) == bool(args.pid):
        ap.error("give either a command after -- or --pid")
    if cpu_temp() is None:
        ap.error("no CPU temperature sensor found (coretemp or x86_pkg_temp)")
    out = open(args.log, "a", encoding="utf-8", buffering=1) if args.log else sys.stderr

    def say(msg: str) -> None:
        print(f"{time.strftime('%H:%M:%S')} {msg}", file=out, flush=True)

    proc = subprocess.Popen(cmd) if cmd else None
    root = proc.pid if proc else args.pid
    paused: str | None = None
    state = {"paused": False}

    def resume_and_exit(signum, _frame):
        if state["paused"]:
            signal_tree(root, signal.SIGCONT)
        if proc:
            proc.send_signal(signum)
        say(f"guard stopped by signal {signum}; job resumed")
        sys.exit(128 + signum)

    signal.signal(signal.SIGTERM, resume_and_exit)
    signal.signal(signal.SIGINT, resume_and_exit)
    say(f"guarding pid {root}: pause at {args.hot:.0f}°C average over {args.window:g} s or {args.hard:.0f}°C at once, "
        f"for at least {args.min_pause:g} s and until {args.cool:.0f}°C; "
        + (f"{args.break_for:g} min break every {args.break_every:g} min" if args.break_every else "no scheduled breaks")
        + f"; CPU now {cpu_temp():.0f}°C")
    worked = paused_total = 0.0
    break_until = paused_at = 0.0
    peak = 0.0
    last = last_report = running_since = time.time()      # the average needs a full window of running
    pauses = 0
    recent: list[tuple[float, float]] = []
    try:
        while (proc.poll() is None) if proc else alive(root):
            t = cpu_temp()
            now = time.time()
            peak = max(peak, t or 0)
            if args.off_file and args.off_file.exists():
                if not state.get("off"):
                    if paused:
                        signal_tree(root, signal.SIGCONT)
                        state["paused"], paused = False, None
                    state["off"] = True
                    say(f"guard switched off ({args.off_file} exists); job running; CPU {t or 0:.0f}°C")
                last = now
                time.sleep(args.check)
                continue
            if state.get("off"):
                state["off"] = False
                recent, running_since, worked = [], now, 0.0
                say(f"guard switched on again; CPU {t or 0:.0f}°C")
            if t is not None:
                recent = [(s, v) for s, v in recent if s > now - args.window] + [(now, t)]
            avg = sum(v for _, v in recent) / len(recent) if recent else 0.0
            if paused is None:
                worked += now - last
                if t is not None and (t >= args.hard or (avg >= args.hot and now - running_since >= args.window)):
                    paused, pauses, paused_at = "hot", pauses + 1, now
                elif args.break_every and worked >= args.break_every * 60:
                    paused, pauses, break_until = "break", pauses + 1, now + args.break_for * 60
                if paused:
                    n = signal_tree(root, signal.SIGSTOP)
                    state["paused"] = True
                    why = f"CPU at {t:.0f}°C, {avg:.0f}°C average" if paused == "hot" else "scheduled break"
                    say(f"pause ({why}); {n} processes stopped")
            else:
                paused_total += now - last
                if paused == "break" and now >= break_until and t is not None and t > args.cool:
                    paused = "hot"            # the break is over but the CPU is still warm: wait for it
                if (paused == "break" and now >= break_until) or \
                        (paused == "hot" and now - paused_at >= args.min_pause and (t is None or t <= args.cool)):
                    recent, running_since = [], now
                    signal_tree(root, signal.SIGCONT)
                    state["paused"] = False
                    say(f"resume (CPU at {t or 0:.0f}°C)")
                    paused, worked = None, 0.0
            if now - last_report >= args.report * 60:
                say(f"status: CPU {t or 0:.0f}°C now, {peak:.0f}°C peak since last status; "
                    f"{'paused' if paused else 'running'}; {pauses} pauses, {paused_total / 60:.0f} min paused in all")
                peak, last_report = 0.0, now
            last = now
            time.sleep(args.check)
    finally:
        if state["paused"] and alive(root):
            signal_tree(root, signal.SIGCONT)
    say(f"job finished; {pauses} pauses, {paused_total / 60:.0f} min paused in all")
    return proc.returncode if proc else 0


if __name__ == "__main__":
    sys.exit(main())

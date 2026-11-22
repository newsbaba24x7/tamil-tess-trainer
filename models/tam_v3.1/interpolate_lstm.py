#!/usr/bin/env python3
"""Weight-space interpolation of two Tesseract LSTM models with the same network and
character set (WiSE-FT: Wortsman et al., "Robust fine-tuning of zero-shot models", CVPR 2022).

  out = (1 - alpha) * A + alpha * B        (float weight matrices only)

A, B: `.lstm` components (combine_tessdata -e X.traineddata X.lstm) of float (non-integer)
runtime models. Everything except the weight values is copied from B. The parser walks the
serialized network (Tesseract 5 format) and refuses to write anything unless both files have
the same layout, every array has the shape its layer implies, and the walk ends exactly where
the network ends.

  python3 -I interpolate_lstm.py A.lstm B.lstm ALPHA OUT.lstm      # or: --dump A.lstm
  ALPHA may carry per-layer overrides, e.g. "0.5,Lfx192=0.8,Output=0.8".
  python3 -I interpolate_lstm.py --graft SRC.lstm DST.lstm ConvNL,Lfys48,Lfx96,Lrx96 OUT.lstm

Note: Tesseract seeds the noise used when normalising a line image from the model's
iteration counters, so two files with identical weights but different counters can differ
on a few characters. Exactness is therefore checked on bytes: interpolate(A, B, 1) == B and
interpolate(B, A, 1) == A.
"""
import struct, sys

PLUMBING = {"Parallel", "Replicated", "ParBidiLSTM", "DepParUDLSTM", "Par2dLSTM", "Series",
            "RTLReversed", "TTBReversed", "XYTranspose"}
FULLY = {"Logistic", "LinLogistic", "LinTanh", "Tanh", "Relu", "Linear", "Softmax", "SoftmaxNoCTC"}
LSTMS = {"LSTM", "SummLSTM", "LSTMSoftmax", "LSTMBinarySoftmax"}
NF_LAYER_SPECIFIC_LR, K_INT8, K_ADAM, K_DOUBLE = 64, 1, 4, 128
DIMS = {}   # (offset, name) -> (rows, cols) of every weight matrix


class R:
    def __init__(self, b): self.b, self.p = b, 0
    def take(self, fmt):
        v = struct.unpack_from("<" + fmt, self.b, self.p); self.p += struct.calcsize("<" + fmt); return v
    def i8(self): return self.take("b")[0]
    def u8(self): return self.take("B")[0]
    def i32(self): return self.take("i")[0]
    def u32(self): return self.take("I")[0]
    def s(self):
        n = self.u32(); v = self.b[self.p:self.p + n].decode("latin-1"); self.p += n; return v


def weights(r, training, rows, cols, arrays, where):
    mode = r.u8()
    if mode & K_INT8:
        raise SystemExit(f"{where}: integer weights; interpolate float models only")
    size = 8 if mode & K_DOUBLE else 4
    d1, d2 = r.i32(), r.i32()
    if (rows is not None and d1 != rows) or (cols is not None and d2 != cols):
        raise SystemExit(f"{where}: shape {d1}x{d2}, expected {rows}x{cols}")
    r.p += size                                   # GENERIC_2D_ARRAY 'empty_' value
    arrays.append((r.p, d1 * d2, size, where)); DIMS[(r.p, where)] = (d1, d2); r.p += d1 * d2 * size
    if training:                                  # updates_ (+ dw_sq_sum_ with Adam)
        for _ in range(2 if mode & K_ADAM else 1):
            a, b = r.i32(), r.i32(); r.p += size + a * b * size
    return d1, d2


def network(r, arrays, depth=0, log=None):
    r.i8(); t = r.s(); training = r.i8() == 1; r.i8()
    flags, ni, no, nw = r.i32(), r.i32(), r.i32(), r.i32(); name = r.s()
    if log is not None:
        log.append(f"{'  ' * depth}{t} {name} ni={ni} no={no} weights={nw}")
    if t == "Input":
        r.take("5i")
    elif t == "Convolve":
        r.take("2i")
    elif t in ("Maxpool", "Reconfig"):
        r.take("2i")
    elif t in PLUMBING:
        for _ in range(r.u32()):
            network(r, arrays, depth + 1, log)
        if flags & NF_LAYER_SPECIFIC_LR:          # std::vector<float> learning_rates_
            n_lr = r.u32(); r.p += 4 * n_lr
    elif t in FULLY:
        k = len(arrays); weights(r, training, no, ni + 1, arrays, name)
        if sum(c for _, c, _, _ in arrays[k:]) != nw:
            raise SystemExit(f"{name}: weight count differs from its header; refusing")
    elif t in LSTMS:
        na = r.i32()                               # inputs to each gate = ni + cells
        k = len(arrays)
        for g in range(4):                         # CI, GI, GF1, GO (1-D LSTMs have no GFS)
            weights(r, training, no, na + 1, arrays, f"{name}.gate{g}")
        if t.startswith("LSTM") and t.endswith("Softmax"):
            network(r, arrays, depth + 1, log)
        elif sum(c for _, c, _, _ in arrays[k:]) != nw:
            raise SystemExit(f"{name}: weight count differs from its header; refusing")
    else:
        raise SystemExit(f"unknown layer type {t!r} at byte {r.p}")
    return nw


def parse(path, log=None):
    b = open(path, "rb").read(); r = R(b); arrays = []
    total = network(r, arrays, 0, log)
    spec_pos = r.p
    tail = R(b); tail.p = spec_pos
    try:
        spec = tail.s()
    except Exception:
        spec = ""
    if not spec.startswith("["):
        raise SystemExit(f"{path}: network walk ended at byte {spec_pos} but no network spec follows; refusing")
    n = sum(c for _, c, _, _ in arrays)
    # Every weighted layer was checked against its own header above. The outer total is 0 in
    # networks built with --append_index, so it is only compared when present.
    if total and n != total:
        raise SystemExit(f"{path}: parsed {n} weights, header says {total}; refusing")
    return b, arrays, spec


def graft(src_path, dst_path, layers, out):
    """Copy the weights of the named layers from SRC into DST (shapes must match), e.g. to put
    the BEST model's lower layers into a FAST model before interpolating them."""
    S, sa, _ = parse(src_path); D, da, _ = parse(dst_path)
    src = {w: (p, c, s) for p, c, s, w in sa}; o = bytearray(D); n = 0
    for p, c, s, w in da:
        if w.split(".")[0] in layers:
            sp, sc, ss = src.get(w, (None, None, None))
            if (sc, ss) != (c, s):
                raise SystemExit(f"{w}: shape differs between models; refusing")
            o[p:p + c * s] = S[sp:sp + c * s]; n += c
    open(out, "wb").write(o)
    print(f"wrote {out}: {n} weights of layers {sorted(layers)} copied from {src_path}")


def main():
    if sys.argv[1] == "--graft":                   # --graft SRC DST LAYER[,LAYER...] OUT
        graft(sys.argv[2], sys.argv[3], set(sys.argv[4].split(",")), sys.argv[5]); return
    if sys.argv[1] == "--dump":
        log = []; _, arrays, spec = parse(sys.argv[2], log)
        print("\n".join(log)); print(f"spec {spec}; {len(arrays)} weight arrays, {sum(c for _, c, _, _ in arrays)} weights")
        return
    # ALPHA: a number, then optional per-layer overrides "Layer=a" and per-row overrides
    # "Layer@first-last=a" (rows of the weight matrix = output units; for the Output layer with the
    # identity recoder, row i = character i). Example: "0.6,Output@178-185=1".
    a_path, b_path, spec, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    parts = spec.split(","); alpha = float(parts[0]); layer_alpha, row_alpha = {}, []
    for x in parts[1:]:
        k, v = x.split("=")
        if "@" in k:
            lay, rng_ = k.split("@"); lo, _, hi = rng_.partition("-")
            row_alpha.append((lay, int(lo), int(hi or lo), float(v)))
        else:
            layer_alpha[k] = float(v)
    A, aa, sa = parse(a_path); B, ab, sb = parse(b_path)
    if [(p, c, s) for p, c, s, _ in aa] != [(p, c, s) for p, c, s, _ in ab] or len(A) != len(B) or sa != sb:
        raise SystemExit("models differ in layout; refusing")
    o = bytearray(B); used = {}; rows_done = []
    for p, c, s, where in ab:
        lay = where.split(".")[0]
        al = layer_alpha.get(lay, alpha); used[lay] = al
        rows, cols = DIMS[(p, where)]
        alphas = [al] * rows
        for rl, lo, hi, a in row_alpha:
            if rl == lay:
                if hi >= rows:
                    raise SystemExit(f"{lay} has {rows} rows; cannot set rows {lo}-{hi}")
                for i in range(lo, hi + 1):
                    alphas[i] = a
                rows_done.append((rl, lo, hi))
        f = "<%d%s" % (c, "d" if s == 8 else "f")
        va, vb = struct.unpack_from(f, A, p), struct.unpack_from(f, B, p)
        struct.pack_into(f, o, p, *[(1 - alphas[k // cols]) * x + alphas[k // cols] * y for k, (x, y) in enumerate(zip(va, vb))])
    unknown = set(layer_alpha) - set(used) | {r[0] for r in row_alpha} - set(used)
    if unknown:
        raise SystemExit(f"no layer named {sorted(unknown)}; layers are {sorted(used)}")
    open(out, "wb").write(o)
    print(f"wrote {out}: alpha per layer {used}, row overrides {sorted(set(rows_done))}, {sum(c for _, c, _, _ in ab)} weights")


if __name__ == "__main__":
    main()

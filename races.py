"""Runs to remember: 2x2 card screen of favorite races (static data from Garmin)."""
from render import *  # canvas, F, quantize, colors, W, H

def decode(s, prec=1e4):
    pts, i, lat, lon = [], 0, 0, 0
    while i < len(s):
        vals = []
        for _ in range(2):
            shift = res = 0
            while True:
                b = ord(s[i]) - 63; i += 1
                res |= (b & 0x1f) << shift; shift += 5
                if b < 0x20: break
            vals.append(~(res >> 1) if res & 1 else res >> 1)
        lat += vals[0]; lon += vals[1]
        pts.append((lat / prec, lon / prec))
    return pts

RACES = [
    dict(name="Grandma's Marathon", where="Duluth", note="Two Harbors to Duluth", date="Jun 17, 2023",
         stat="26.2 mi", time="4:32:32", gain=493,
         poly='mbu[|f~v@T\\b@l@^f@`@j@d@n@\\f@^h@f@p@`@l@^f@^h@`@d@b@d@`@d@h@j@b@f@f@h@^r@^x@^x@d@r@`@Rh@Td@Pf@Tf@l@Zh@Xd@b@t@`@r@`@n@\\j@\\h@\\d@f@p@`@h@\\n@Pv@`@T^~@Zx@Vp@`@x@Zl@Zf@Xf@\\n@Jx@C|@?dA@bA?lAJnAL~@N`ANz@NbAPp@n@j@b@@h@Hj@\\b@^`@v@\\r@Rr@T`ABr@BdALhANx@Xt@Tp@Xt@\\n@^^Xh@^p@`@p@Xh@\\p@`@r@d@l@X\\j@f@\\`@Zt@Xx@Pz@F~@\\v@\\n@Xh@Xj@Tx@ZfAP\\Rd@H^T|@Vp@b@x@`@n@^v@`@r@b@t@Zp@Rz@Lt@Ll@\\j@Vl@\\|@`@|@`@v@\\j@`@l@d@n@h@v@b@b@X~@N|@H|@Ln@N|@Nv@Vp@d@`ARZ^j@`@d@`@l@Xx@Rp@?z@?\\Nv@`@h@`@l@\\d@^j@b@n@V^Xb@Zd@^p@\\x@Xj@Xr@N\\Vl@^z@\\v@Fj@Vj@d@p@b@n@R^`@f@TZV^V\\\\f@Xb@TZTLVo@Xc@Qq@k@?c@@Y_@VSl@Q@A',
         elev=[730,734,698,682,656,661,648,644,641,643,669,689,628,649,654,643,627,633,632,636,635,642,655,623,651,654,684,658,701,675,659,658,624,623]),
    dict(name="Elm Creek Backyard", where="Maple Grove", note="13 yards, 4.17 mi each", date="Apr 24, 2026",
         stat="54.2 mi", time="13:04:04", gain=4172,
         poly='}upZhu_x@O?A?@BABAJ?FB@L@@L@@AB?FANCDAFGDG@E?AE?QACC?C?MFI@GCEGEEE@EBAAGGGCE@MFAHI\\GVCLE@CD@F?H@JBDD?J@DA@BFBJH?HAL@FBNBH@A@CDCBAD?F?FBJHFBFBBBJHJHNNBBF@FDDCD?B@LL?F?DH@B@FNFN@J?VBJDDDBHA@ABIDKDGDCF?FB?CE]AEEIAK@S@S?GCEG@C@EAGEIIIAC@ADC?ECAG?KCE?Q@ECG?EAK?IAEAKEKCEM[GMKKEGGM?G?M?E@ICKGAE?CC?O?GBEFC@CA@?C?H@B??@E',
         elev=[911,894,925,916,878,897,871,885,913,892,916,895,877,880,890,897,911,905,879,915,906,892,879,882,937,915,916,892,892,887,913,875,883,897]),
    dict(name="Bighorn 32", where="Dayton, WY", note="Down from 8,400 ft", date="Jun 20, 2026",
         stat="31.6 mi", time="9:20:55", gain=3801,
         poly='osjZzwr`AyAeBw@Xi@Jm@Lm@Ba@Jw@Hc@?q@Lm@V_AR}@Wo@f@]fAm@xAi@|D_@l@Lj@_@pAMtAg@h@g@`BaAt@Qr@]h@Q|@N`@El@Hl@NVYp@YWUFUFg@L]?g@J[t@WlAV?b@UZ@XV^Nf@GVDFb@@j@TWZa@b@Kf@Qz@mAYi@JeAVKp@Gf@Yh@}@h@yAn@s@jAaAnAsAV}Ah@iAp@aAx@o@j@q@p@iAL{@ZoB^{At@uBLqA[E_Am@Wu@aAqAk@c@i@{@i@{@o@iBSs@LoASaCLmAHsALc@^i@b@s@b@u@r@mARkAS_AS}@JWX]d@cBLcANw@R]RU^Jx@t@t@v@^_A_@y@QyASi@Gw@Kk@B{@Nu@?gAGg@JgADk@Bi@Gi@Qo@?q@@uAI_AGs@?}@OIUc@KCOOKc@S[Qo@Yo@Ea@Mg@Ia@MY[[OUQ[Oi@AWPe@TWLc@Cs@Jc@F]De@SY?K@Sd@_@E{@Ei@Hs@k@mAAq@Ey@?}@o@_AqAc@{@BiAa@cAcCu@iDcAqCs@wBk@k@gAmA\\iAg@i@',
         elev=[7565,7672,8078,8439,8441,8374,8294,7838,7439,7080,6726,6914,6761,6878,6967,7327,7615,7811,7603,7399,7230,7490,7278,6864,6349,5838,5326,4847,4691,4484,4306,4227,4119,3986,3921]),
    dict(name="Twin Cities Marathon", where="Mpls to St Paul", note="Loony Challenge · 36 mi in 6:07:13",
         legs=[("Sat", "10K", "1:02:37", 'i~lZhmyw@LJTPXTTPV?JPA`@PXVIH^LZRb@Ph@?p@?n@?d@@ZAb@?h@?j@?p@?f@?l@?n@?p@Ar@?j@?n@?j@Af@?r@B??c@?m@?k@?c@@o@Cs@?c@?o@@s@?_@?i@?q@?q@?e@?o@Am@@i@As@Mc@Ug@Qi@Ok@U_@UK[IYUc@[AC'), ("Sat", "5K", "34:49", 'i~lZhmyw@BBDDJHPLLJNJNJN@P@LNLRHTFTH\\HTJRLVHT@\\?`@?X?V?\\CPOB@\\FNHE?_@?[?SAY?Q@UAS?UAWKWMUKUIWEQEUISMUKOMEOASIMKMKSOKI'), ("Sun", "Marathon", "4:29:47", None)], date="Oct 4, 2026",
         stat="26.2 mi", time="4:29:47", gain=625,
         poly='{kmZlp|w@Ob@ENq@nA@ZIf@D^\\f@Xt@Vx@Rp@Pl@XPj@@d@FBf@?z@?bA?fA?~@?t@b@Rj@Pf@@Xb@Xd@n@@RTVt@d@Nf@El@Th@b@l@Nf@@`@Mp@PXc@CiARs@Xi@^[`@YT[@_AN{@Xs@f@Mb@Df@Tl@T\\RXi@j@Cf@Hf@IZi@Aa@@o@Bi@Dw@Fo@R]Dk@Um@Yi@W]Mm@Wm@Yo@Ho@Lk@Sw@U_AC_A_@o@Qy@X[h@?h@?f@Ld@h@f@X^DTm@J{@Gu@[m@g@[]i@g@_@m@Oe@Ye@f@Qx@OC?u@Fw@?aA?aA?_A?{@A_ACs@Os@Mq@Qq@Su@m@Ee@Jg@[o@Oq@Bk@@o@J[^i@Se@?k@Oe@@m@Ri@V]j@_@x@a@n@i@x@c@x@c@h@_@d@Qf@_@q@Gk@\\m@^k@`@k@b@a@^g@^o@Nm@Ri@f@o@d@Ob@Gb@Ol@I?_@Es@J]XY?k@?w@?o@?m@?aA?w@Cm@?_A@}@B}@A{@?gA?_A@}@?cACeA?_A@aA?aA?}@@_AAu@?y@?cAWy@Wo@U{@[g@e@Kc@[c@]',
         elev=[858,908,871,908,884,867,862,862,863,856,852,875,842,830,845,823,829,855,820,808,816,810,818,797,783,822,885,930,955,934,923,859]),
]

def _route(d, pts, box, width=4, dot=6):
    import math
    x0, y0, x1, y1 = box
    lat0 = sum(p[0] for p in pts) / len(pts)
    k = math.cos(math.radians(lat0))
    xs = [p[1] * k for p in pts]; ys = [p[0] for p in pts]
    w, h = max(xs) - min(xs) or 1e-9, max(ys) - min(ys) or 1e-9
    s = min((x1 - x0) / w, (y1 - y0) / h)
    ox = x0 + ((x1 - x0) - w * s) / 2; oy = y0 + ((y1 - y0) - h * s) / 2
    xy = [(ox + (x - min(xs)) * s, oy + (max(ys) - y) * s) for x, y in zip(xs, ys)]
    d.line(xy, fill=BLUE, width=width, joint="curve")
    for (x, y), col in ((xy[-1], RED), (xy[0], GREEN)):
        d.ellipse([x - dot, y - dot, x + dot, y + dot], fill=col, outline=BLACK, width=1 if dot < 5 else 2)

def _elev(d, vals, box):
    x0, y0, x1, y1 = box
    lo, hi = min(vals), max(vals)
    span = max(hi - lo, 400)   # flat races stay flat
    pts = [(x0 + (x1 - x0) * i / (len(vals) - 1), y1 - (y1 - y0) * (v - lo) / span) for i, v in enumerate(vals)]
    d.polygon(pts + [(x1, y1), (x0, y1)], fill=GREEN)
    d.line([x0, y1, x1, y1], fill=BLACK, width=1)

def screen_race(i):
    r = RACES[i % len(RACES)]
    img, d = canvas()
    d.rectangle([0, 0, W, 44], fill=BLACK)
    d.text((20, 22), "RUNS TO REMEMBER", font=F(22, "ExtraBold"), fill=WHITE, anchor="lm")
    d.text((W - 20, 22), f"{i % len(RACES) + 1} of {len(RACES)}", font=F(18, "SemiBold"), fill=WHITE, anchor="rm")
    _route(d, decode(r["poly"]), (30, 66, 410, 456))
    tx = 440
    d.text((tx, 62), r["name"], font=F(30, "ExtraBold"), fill=BLACK)
    d.text((tx, 102), f"{r['date']} · {r['where']}", font=F(16, "SemiBold"), fill=BLACK)
    d.text((tx, 130), r["stat"], font=F(80, "Black"), fill=BLACK)
    d.text((tx, 230), r["time"], font=F(36, "ExtraBold"), fill=BLUE)
    d.text((tx, 274), f"+{r['gain']:,} ft climbed", font=F(20, "Bold"), fill=BLACK)
    if r.get("legs"):
        for j, (day, what, t, poly) in enumerate(r["legs"]):
            y = 316 + j * 30
            d.text((tx, y), day, font=F(17, "SemiBold"), fill=BLACK)
            _route(d, decode(poly or r["poly"]), (tx + 42, y - 2, tx + 66, y + 22), width=2, dot=3)
            d.text((tx + 80, y), what, font=F(17, "Bold"), fill=BLACK)
            d.text((W - 30, y), t, font=F(17, "ExtraBold"), fill=BLACK, anchor="ra")
    else:
        _elev(d, r["elev"], (tx, 320, W - 30, 390))
    d.rectangle([tx, 410, W - 30, 450], fill=YELLOW)
    d.text(((tx + W - 30) / 2, 430), r["note"], font=F(18, "ExtraBold"), fill=BLACK, anchor="mm")
    return img

if __name__ == "__main__":
    import sys
    for i in range(len(RACES)):
        quantize(screen_race(i)).save((sys.argv[1] if len(sys.argv) > 1 else "out") + f"/race{i}.png")

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


# Water from OpenStreetMap (simplified). Polygons are filled, lines are drawn.
TC_LAKES = ['_glZ|b|w@?o@Lm@NUHIHCB?FBB?NRt@\\PRDPJCZ\\h@ZRh@Up@UFDDLLCHOPYK[KFSEE]U]COYMc@IGIEGD[ASK?C', 'unlZzl}w@K[AEAKAE?e@@OB[Lk@P]XUb@CXFVL\\N^TJJBDFNPx@?bAC`@I^Q\\ONC@A@YE]M[YUMYGa@UOK', 'mcmZxu}w@W`@]Oo@C@}@N[CGCCBKBAJSLQ^RDH?PFBHCJM`@LRVJJR?JHLIRTSnAY`@I[IG[YCFIn@U?Ea@Bg@GCAB', 'shmZhv}w@?E?E@A@ABC@AB@D@FHBD@?BBFD@B@?@@B@??@@?@@DA@AF?@CBA@E@A?A?AAGGCC?ACAEECCGIAAAE', 'ellZh_|w@?K@E@C@EDGJMFEH?HDFDH@FBD?D@@B?FDFDFADCFCFD@CB?@BBCFKPEFKBO@M@I?IEEIAGAICIAI?M', 'q}lZlk}w@I^?PENA\\KHQCUHCAK@c@IAOEOUAASFKJFJ?AKDMHEBG?IGMUOg@MSBKBQBAIRWLKP@NLRJTFPCFSFQH?NLLDPLLTHV?H', 'mwlZ~i}w@N?TBL@RBJ@JFFH^t@Fz@Ux@OTDZ@B@LM`@WA]B_@L{@Gu@_@EIIGOOEOGOIYCIACESAM?WBQFUHMJEHAHCn@WVQd@GB?']
TC_RIVER = ['{`lZde{w@Tc@HKFEHCJ?P@\\A\\ITIPMJMFIBEDQDYB[FsBBq@@eBAg@AYGm@Ig@YcASs@COAOAs@Au@C]', 'kgmZ|y{w@x@kAHMnEgH\\s@P[PQNMPGf@Kt@If@ELAd@?R@^B^BP?b@Cj@E^CNAL@TBh@J^Ff@DdAV', 'unmZpd|w@BUBODQDGFKBAHENGNCN?H@NAVELE@A@AFEBGBEDGBIBM@ED]B]B[Hc@H[HQ', 'uelZhj{w@p@WFCHCHCFEBCBEHIFOL[HUFOHS']
SUPERIOR = 'kio[bkdw@o@pA}@`Au@v@i@t@y@`AaBlB}AfBsBvBmChCmCbCeCtBaCjB_DpBcBYSBMfAcBd@y@]cA{@q@gAe@{B_AmCa@aA_BiDiC}C}@gB{@gDm@sBy@yAkAgAsA{CQiAUu@MwAKYO{@[}@aAcB{AiBiAgBk@wA_@o@[{@Iq@UaASo@c@aAsAuByA}C{@qCa@wAaAsBcAeEEDFY{AuCgCsCoAgC}AkCqBkEoC_NsEmFmAmJfAaEkCcCiByCyAuEm@uFWh@QLD[AQcBk@q@c@Yw@iBaDo@m@Wu@u@c@}@aAo@q@Wi@k@}@e@gA[m@kAy@wBiDoCyEsC}E{EoQm@SAgCc@n@AmA`@kA`@ADGHYGQWe@i@Ew@IWAq@CUVw@i@o@sCn@}A'   # shoreline, Superior WI to past Two Harbors
SUPERIOR_CLOSE = [(47.10, -91.50), (46.60, -91.50), (46.60, -92.03)]   # lake side (southeast)

RACES = [
    dict(name="Grandma's Marathon", water="superior", where="Duluth", note="Two Harbors to Duluth", date="Jun 17, 2023",
         stat="26.2 mi", time="4:32:32", gain=493, loss=606,
         poly='mbu[|f~v@T\\b@l@^f@`@j@d@n@\\f@^h@f@p@`@l@^f@^h@`@d@b@d@`@d@h@j@b@f@f@h@^r@^x@^x@d@r@`@Rh@Td@Pf@Tf@l@Zh@Xd@b@t@`@r@`@n@\\j@\\h@\\d@f@p@`@h@\\n@Pv@`@T^~@Zx@Vp@`@x@Zl@Zf@Xf@\\n@Jx@C|@?dA@bA?lAJnAL~@N`ANz@NbAPp@n@j@b@@h@Hj@\\b@^`@v@\\r@Rr@T`ABr@BdALhANx@Xt@Tp@Xt@\\n@^^Xh@^p@`@p@Xh@\\p@`@r@d@l@X\\j@f@\\`@Zt@Xx@Pz@F~@\\v@\\n@Xh@Xj@Tx@ZfAP\\Rd@H^T|@Vp@b@x@`@n@^v@`@r@b@t@Zp@Rz@Lt@Ll@\\j@Vl@\\|@`@|@`@v@\\j@`@l@d@n@h@v@b@b@X~@N|@H|@Ln@N|@Nv@Vp@d@`ARZ^j@`@d@`@l@Xx@Rp@?z@?\\Nv@`@h@`@l@\\d@^j@b@n@V^Xb@Zd@^p@\\x@Xj@Xr@N\\Vl@^z@\\v@Fj@Vj@d@p@b@n@R^`@f@TZV^V\\\\f@Xb@TZTLVo@Xc@Qq@k@?c@@Y_@VSl@Q@A',
         elev=[730,734,698,682,656,661,648,644,641,643,669,689,628,649,654,643,627,633,632,636,635,642,655,623,651,654,684,658,701,675,659,658,624,623]),
    dict(name="Elm Creek Backyard", where="Maple Grove", note="13 yards, 4.17 mi each", date="Apr 24, 2026",
         stat="54.2 mi", time="13:04:04", gain=4172, loss=4207,
         poly='}upZhu_x@O?A?@BABAJ?FB@L@@L@@AB?FANCDAFGDG@E?AE?QACC?C?MFI@GCEGEEE@EBAAGGGCE@MFAHI\\GVCLE@CD@F?H@JBDD?J@DA@BFBJH?HAL@FBNBH@A@CDCBAD?F?FBJHFBFBBBJHJHNNBBF@FDDCD?B@LL?F?DH@B@FNFN@J?VBJDDDBHA@ABIDKDGDCF?FB?CE]AEEIAK@S@S?GCEG@C@EAGEIIIAC@ADC?ECAG?KCE?Q@ECG?EAK?IAEAKEKCEM[GMKKEGGM?G?M?E@ICKGAE?CC?O?GBEFC@CA@?C?H@B??@E',
         elev=[911,894,925,916,878,897,871,885,913,892,916,895,877,880,890,897,911,905,879,915,906,892,879,882,937,915,916,892,892,887,913,875,883,897]),
    dict(name="Bighorn 32", where="Dayton, WY", note="From 8,524 ft down to 3,913 ft", date="Jun 20, 2026",
         stat="31.6 mi", time="9:20:55", gain=3801, loss=7416,
         poly='osjZzwr`AyAeBw@Xi@Jm@Lm@Ba@Jw@Hc@?q@Lm@V_AR}@Wo@f@]fAm@xAi@|D_@l@Lj@_@pAMtAg@h@g@`BaAt@Qr@]h@Q|@N`@El@Hl@NVYp@YWUFUFg@L]?g@J[t@WlAV?b@UZ@XV^Nf@GVDFb@@j@TWZa@b@Kf@Qz@mAYi@JeAVKp@Gf@Yh@}@h@yAn@s@jAaAnAsAV}Ah@iAp@aAx@o@j@q@p@iAL{@ZoB^{At@uBLqA[E_Am@Wu@aAqAk@c@i@{@i@{@o@iBSs@LoASaCLmAHsALc@^i@b@s@b@u@r@mARkAS_AS}@JWX]d@cBLcANw@R]RU^Jx@t@t@v@^_A_@y@QyASi@Gw@Kk@B{@Nu@?gAGg@JgADk@Bi@Gi@Qo@?q@@uAI_AGs@?}@OIUc@KCOOKc@S[Qo@Yo@Ea@Mg@Ia@MY[[OUQ[Oi@AWPe@TWLc@Cs@Jc@F]De@SY?K@Sd@_@E{@Ei@Hs@k@mAAq@Ey@?}@o@_AqAc@{@BiAa@cAcCu@iDcAqCs@wBk@k@gAmA\\iAg@i@',
         elev=[7565,7672,8078,8439,8441,8374,8294,7838,7439,7080,6726,6914,6761,6878,6967,7327,7615,7811,7603,7399,7230,7490,7278,6864,6349,5838,5326,4847,4691,4484,4306,4227,4119,3986,3921]),
    dict(name="Ultra Loony Challenge", water="twincities", where="Twin Cities", note="3 races · 2 days · Mpls to St Paul",
         legs=[("Sat", "10K", "1:02:37", 'i~lZhmyw@LJTPXTTPV?JPA`@PXVIH^LZRb@Ph@?p@?n@?d@@ZAb@?h@?j@?p@?f@?l@?n@?p@Ar@?j@?n@?j@Af@?r@B??c@?m@?k@?c@@o@Cs@?c@?o@@s@?_@?i@?q@?q@?e@?o@Am@@i@As@Mc@Ug@Qi@Ok@U_@UK[IYUc@[AC'), ("Sat", "5K", "34:49", 'i~lZhmyw@BBDDJHPLLJNJNJN@P@LNLRHTFTH\\HTJRLVHT@\\?`@?X?V?\\CPOB@\\FNHE?_@?[?SAY?Q@UAS?UAWKWMUKUIWEQEUISMUKOMEOASIMKMKSOKI'), ("Sun", "Marathon", "4:29:47", None)], date="Oct 3–4, 2026",
         stat="35.9 mi", time="6:07:13", gain=936, loss=944,
         poly='{kmZlp|w@Ob@ENq@nA@ZIf@D^\\f@Xt@Vx@Rp@Pl@XPj@@d@FBf@?z@?bA?fA?~@?t@b@Rj@Pf@@Xb@Xd@n@@RTVt@d@Nf@El@Th@b@l@Nf@@`@Mp@PXc@CiARs@Xi@^[`@YT[@_AN{@Xs@f@Mb@Df@Tl@T\\RXi@j@Cf@Hf@IZi@Aa@@o@Bi@Dw@Fo@R]Dk@Um@Yi@W]Mm@Wm@Yo@Ho@Lk@Sw@U_AC_A_@o@Qy@X[h@?h@?f@Ld@h@f@X^DTm@J{@Gu@[m@g@[]i@g@_@m@Oe@Ye@f@Qx@OC?u@Fw@?aA?aA?_A?{@A_ACs@Os@Mq@Qq@Su@m@Ee@Jg@[o@Oq@Bk@@o@J[^i@Se@?k@Oe@@m@Ri@V]j@_@x@a@n@i@x@c@x@c@h@_@d@Qf@_@q@Gk@\\m@^k@`@k@b@a@^g@^o@Nm@Ri@f@o@d@Ob@Gb@Ol@I?_@Es@J]XY?k@?w@?o@?m@?aA?w@Cm@?_A@}@B}@A{@?gA?_A@}@?cACeA?_A@aA?aA?}@@_AAu@?y@?cAWy@Wo@U{@[g@e@Kc@[c@]',
         elev=[858,908,871,908,884,867,862,862,863,856,852,875,842,830,845,823,829,855,820,808,816,810,818,797,783,822,885,930,955,934,923,859]),
]

def _proj(pts, box):
    import math
    x0, y0, x1, y1 = box
    lat0 = sum(p[0] for p in pts) / len(pts)
    k = math.cos(math.radians(lat0))
    xs = [p[1] * k for p in pts]; ys = [p[0] for p in pts]
    mnx, mxy = min(xs), max(ys)
    w, h = max(xs) - mnx or 1e-9, mxy - min(ys) or 1e-9
    s = min((x1 - x0) / w, (y1 - y0) / h)
    ox = x0 + ((x1 - x0) - w * s) / 2; oy = y0 + ((y1 - y0) - h * s) / 2
    return lambda la, lo: (ox + (lo * k - mnx) * s, oy + (mxy - la) * s)

def _water(img, f, box, polys=(), lines=()):
    """Draw water into box only (clipped)."""
    from PIL import Image, ImageDraw
    x0, y0, x1, y1 = [int(v) for v in box]
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    for poly in polys:
        ld.polygon([f(a, b) for a, b in poly], fill=BLUE + (255,))
    for line in lines:
        ld.line([f(a, b) for a, b in line], fill=BLUE + (255,), width=6, joint="curve")
    mask = Image.new("L", img.size, 0); ImageDraw.Draw(mask).rectangle([x0, y0, x1, y1], fill=255)
    alpha = Image.composite(layer.getchannel("A"), mask.point(lambda v: 0), mask)
    img.paste(layer, (0, 0), alpha)

def _route(d, pts, box, width=4, dot=6, img=None, water=None):
    pad = 16 if water else 0
    f = _proj(pts, (box[0] + pad, box[1] + pad, box[2] - pad, box[3] - pad))
    if water and img is not None:
        _water(img, f, box, **water)
    xy = [f(a, b) for a, b in pts]
    d.line(xy, fill=BLACK, width=width, joint="curve")
    for (x, y), col in ((xy[-1], RED), (xy[0], GREEN)):
        d.ellipse([x - dot, y - dot, x + dot, y + dot], fill=col, outline=BLACK, width=1 if dot < 5 else 2)

def _water_for(r):
    if r.get("water") == "superior":
        return dict(polys=[decode(SUPERIOR) + SUPERIOR_CLOSE])
    if r.get("water") == "twincities":
        order = [2, 1, 3, 0]   # segments north -> south, joined so the river has no gaps
        river = [pt for i in order for pt in decode(TC_RIVER[i])]
        return dict(polys=[decode(p) for p in TC_LAKES], lines=[river])
    return None

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
    legs = r.get("legs")
    if legs:   # small legs on top (5K left, 10K right), main race below at ~75% height
        small = {what: poly for _, what, _, poly in legs if poly}
        for (label, x0, x1) in (("5K", 30, 210), ("10K", 230, 410)):
            if label in small:
                _route(d, decode(small[label]), (x0 + 34, 72, x1, 150), width=3, dot=4)
                d.text((x0, 72), label, font=F(16, "ExtraBold"), fill=BLACK)
        d.line([30, 162, 410, 162], fill=BLACK, width=1)
        _route(d, decode(r["poly"]), (30, 174, 410, 456), img=img, water=_water_for(r))
        d.text((30, 174), "Marathon", font=F(16, "ExtraBold"), fill=BLACK)
    else:
        _route(d, decode(r["poly"]), (30, 66, 410, 456), img=img, water=_water_for(r))
    tx = 440
    d.text((tx, 62), r["name"], font=F(30, "ExtraBold"), fill=BLACK)
    d.text((tx, 102), f"{r['date']} · {r['where']}", font=F(16, "SemiBold"), fill=BLACK)
    d.text((tx, 130), r["stat"], font=F(80, "Black"), fill=BLACK)
    d.text((tx, 230), r["time"], font=F(36, "ExtraBold"), fill=BLUE)
    d.text((tx, 274), f"+{r['gain']:,} ft up · −{r['loss']:,} ft down", font=F(20, "Bold"), fill=BLACK)
    if r.get("legs"):
        for j, (day, what, t, poly) in enumerate(r["legs"]):
            y = 316 + j * 30
            d.text((tx, y), day, font=F(17, "SemiBold"), fill=BLACK)
            d.text((tx + 48, y), what, font=F(17, "Bold"), fill=BLACK)
            d.text((W - 30, y), t, font=F(17, "ExtraBold"), fill=BLACK, anchor="ra")
    else:
        _elev(d, r["elev"], (tx, 306, W - 30, 414))
    d.rectangle([tx, 424, W - 30, 458], fill=YELLOW)
    d.text(((tx + W - 30) / 2, 441), r["note"], font=F(18, "ExtraBold"), fill=BLACK, anchor="mm")
    return img

if __name__ == "__main__":
    import sys
    for i in range(len(RACES)):
        quantize(screen_race(i)).save((sys.argv[1] if len(sys.argv) > 1 else "out") + f"/race{i}.png")

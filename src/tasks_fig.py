# -*- coding: utf-8 -*-
"""Задачи с ответом-числом, пошаговым решением и чертежом: по 100 на каждый параграф главы 1.

Чертёж — список примитивов в системе координат шириной 400:
  ["L", x1, y1, x2, y2, style]        линия (0 обычная, 1 тонкая, 2 пунктир, 3 жирная)
  ["P", x, y, label, dx, dy, nodot]   точка с подписью
  ["A", cx, cy, r, a1, a2, text, unk] дуга угла (градусы, против часовой стрелки)
  ["R", cx, cy, a, s]                 знак прямого угла
  ["D", x1, x2, y, y0, text, unk]     размерная линия отрезка
  ["C", cx, cy, r]                    окружность (циферблат)
  ["T", x, y, text, size]             надпись
"""
import json, random, sys
from math import comb, cos, sin, radians

def fmt(x):
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f"{x:.2f}".rstrip('0').rstrip('.').replace('.', ',')

def pl(n, one, few, many):
    n10, n100 = n % 10, n % 100
    w = one if n10 == 1 and n100 != 11 else few if 2 <= n10 <= 4 and not 12 <= n100 <= 14 else many
    return f"{n} {w}"

def raz(k):
    return f"в {k} раз" + ("а" if k % 10 in (2, 3, 4) and not 12 <= k % 100 <= 14 else "")

def T(q, ans, unit, hint, steps, fig=None):
    return {"q": q, "a": ans, "u": unit, "h": hint, "s": steps, "f": fig}

def r1(v):
    return round(v, 1)

def F(h, p, cap=None):
    d = {"h": h, "p": p}
    if cap:
        d["c"] = cap
    return d

LET = "ABCDEFGHKLMNPQRS"

# ------------------------------------------------ чертежи
def rays_fig(rays, arcs, rights=(), dashed=(), full=False, cap=None, names=()):
    """rays: [(подпись, угол°)], arcs: [(a1, a2, текст, неизвестный)], rights: [угол начала прямого угла]."""
    degs = [d for _, d in rays]
    if full:
        O, L, h = (200, 135), 112, 270
    elif max(degs) <= 100:
        O, L, h = (70, 205), 180, 240
    else:
        O, L, h = (200, 205), 160, 240
    p = []
    for lab, d in rays:
        x, y = O[0] + L * cos(radians(d)), O[1] - L * sin(radians(d))
        p.append(["L", O[0], O[1], r1(x), r1(y), 2 if lab in dashed else 0])
        if lab:
            nod = 1 if lab in names else 0
            p.append(["P", r1(x), r1(y), lab, r1(14 * cos(radians(d))), r1(-14 * sin(radians(d))), nod])
    for i, (a1, a2, txt, unk) in enumerate(sorted(arcs, key=lambda a: (a[1] - a[0]) % 360)):
        p.append(["A", O[0], O[1], 32 + 17 * i, a1, a2, txt, 1 if unk else 0])
    for d in rights:
        p.append(["R", O[0], O[1], d, 12])
    ds = sorted(set(x % 360 for x in degs))
    best, mid = -1, 270
    for i, a in enumerate(ds):
        b = ds[(i + 1) % len(ds)]
        gap = (b - a) % 360 or 360
        if gap > best:
            best, mid = gap, a + gap / 2
    p.append(["P", O[0], O[1], "O", r1(16 * cos(radians(mid))), r1(-16 * sin(radians(mid))), 0])
    return F(h, p, cap)

def seg_fig(pts, dims, line=False, cap=None):
    """pts: [(буква, координата)], dims: [(буква1, буква2, текст, неизвестный, ряд)] — ряд <0 сверху, >0 снизу."""
    pos = dict(pts)
    lo, hi = min(pos.values()), max(pos.values())
    X = lambda v: r1(40 + (v - lo) / (hi - lo) * 320)
    y = 105
    p = []
    if line:
        p.append(["L", 10, y, 390, y, 1])
    p.append(["L", X(lo), y, X(hi), y, 3])
    for lab, v in pts:
        p.append(["P", X(v), y, lab, 0, -15, 0])
    rows = {-2: 40, -1: 68, 1: 138, 2: 168}
    for a, b, txt, unk, row in dims:
        p.append(["D", X(pos[a]), X(pos[b]), rows[row], y, txt, 1 if unk else 0])
    hmax = max([105] + [rows[d[4]] for d in dims])
    return F(hmax + 22, p, cap)

def clock_fig(h, m):
    cx, cy, R = 200, 118, 98
    p = [["C", cx, cy, R]]
    for k in range(1, 13):
        a = radians(90 - 30 * k)
        p.append(["T", r1(cx + 80 * cos(a)), r1(cy - 80 * sin(a)), str(k), 14])
        p.append(["L", r1(cx + 92 * cos(a)), r1(cy - 92 * sin(a)), r1(cx + R * cos(a)), r1(cy - R * sin(a)), 0])
    ah, am = 90 - (30 * h + m / 2), 90 - 6 * m
    p.append(["L", cx, cy, r1(cx + 48 * cos(radians(ah))), r1(cy - 48 * sin(radians(ah))), 3])
    p.append(["L", cx, cy, r1(cx + 72 * cos(radians(am))), r1(cy - 72 * sin(radians(am))), 0])
    a1, a2 = (ah, am) if (am - ah) % 360 <= 180 else (am, ah)
    p.append(["A", cx, cy, 24, a1 % 360, a2 % 360, "?", 1])
    p.append(["P", cx, cy, "", 0, 0, 0])
    return F(236, p)

def line_through(x, y, d, style=0):
    dx, dy = 600 * cos(radians(d)), -600 * sin(radians(d))
    return ["L", r1(x - dx), r1(y - dy), r1(x + dx), r1(y + dy), style]

def intersect(l1, l2):
    (x1, y1, d1), (x2, y2, d2) = l1, l2
    u1, v1 = cos(radians(d1)), -sin(radians(d1))
    u2, v2 = cos(radians(d2)), -sin(radians(d2))
    det = u1 * (-v2) - (-u2) * v1
    if abs(det) < 1e-9:
        return None
    t = ((x2 - x1) * (-v2) - (-u2) * (y2 - y1)) / det
    return x1 + t * u1, y1 + t * v1

H1 = 230

def fig_points(n, seed):
    rr = random.Random(seed)
    show = n if n <= 7 else 5
    p = []
    pts = []
    for i in range(show):
        a = radians(i * 360 / show + rr.uniform(-12, 12) + 90)
        pts.append((200 + 150 * cos(a), 115 - 85 * sin(a)))
    if show <= 6:
        for i in range(show):
            for j in range(i + 1, show):
                (xa, ya), (xb, yb) = pts[i], pts[j]
                p.append(["L", r1(xa), r1(ya), r1(xb), r1(yb), 1])
    for i, (x, y) in enumerate(pts):
        a = (x - 200, y - 115)
        nrm = (a[0] ** 2 + a[1] ** 2) ** .5 or 1
        p.append(["P", r1(x), r1(y), LET[i], r1(14 * a[0] / nrm), r1(14 * a[1] / nrm), 0])
    return F(H1, p, None if show == n else f"Пример для {show} точек: принцип подсчёта тот же.")

def fig_lines(n, seed):
    rr = random.Random(seed)
    show = n if n <= 6 else 4
    ls = [(200 + rr.uniform(-55, 55), 115 + rr.uniform(-30, 30), i * 180 / show + 15 + rr.uniform(-6, 6)) for i in range(show)]
    p = [line_through(*l) for l in ls]
    for i in range(show):
        for j in range(i + 1, show):
            q = intersect(ls[i], ls[j])
            if q and 4 < q[0] < 396 and 4 < q[1] < H1 - 4:
                p.append(["P", r1(q[0]), r1(q[1]), "", 0, 0, 0])
    return F(H1, p, None if show == n else f"Пример для {show} прямых: принцип подсчёта тот же.")

def fig_collinear(n, k, seed):
    rr = random.Random(seed)
    sk, so = min(k, 6), min(n - k, 5)
    p = [["L", 10, 175, 390, 175, 0], ["P", 384, 175, "a", 0, 14, 1]]
    for i in range(sk):
        p.append(["P", r1(50 + i * 300 / max(sk - 1, 1)), 175, LET[i], 0, 15, 0])
    for i in range(so):
        p.append(["P", r1(50 + (i + .5) * 300 / so + rr.uniform(-20, 20)), r1(rr.uniform(35, 120)), LET[sk + i], 0, -14, 0])
    return F(H1, p, None if (sk == k and so == n - k) else "Показаны не все точки.")

def fig_two_lines(k, m):
    O = (200, 115)
    da, db = 15, 115
    p = [line_through(O[0], O[1], da), line_through(O[0], O[1], db)]
    p.append(["P", r1(O[0] + 190 * cos(radians(da))), r1(O[1] - 190 * sin(radians(da))), "a", 0, -14, 1])
    p.append(["P", r1(O[0] + 105 * cos(radians(db))), r1(O[1] - 105 * sin(radians(db))), "b", 14, 0, 1])
    p.append(["P", O[0], O[1], "O", 14, 12, 1])
    for cnt, d, lim in ((k, da, 175), (m, db, 100)):
        step = 2 * lim / (cnt + 1)
        ts = [-lim + step * (i + 1) for i in range(cnt)]
        ts = [t if abs(t) > 12 else t + 18 for t in ts]
        for t in ts:
            p.append(["P", r1(O[0] + t * cos(radians(d))), r1(O[1] - t * sin(radians(d))), "", 0, 0, 0])
    return F(H1, p)

def fig_parallel(n, k):
    sk, so = min(k, 3), min(n - k, 3)
    p = []
    for i in range(sk):
        p.append(line_through(200, 50 + i * 60, 0))
    for i in range(so):
        p.append(line_through(110 + i * 90, 115, 60 + i * 30))
    return F(H1, p, None if (sk == k and so == n - k) else f"Пример: {sk} непересекающиеся прямые и {so} пересекающие их.")

def fig_concurrent(n):
    show = min(n, 6)
    O = (200, 95)
    p = []
    for i in range(show):
        p.append(line_through(O[0], O[1], 35 + i * 110 / max(show - 1, 1)))
    p.append(["L", -10, 196, 410, 186, 3])
    p.append(["P", O[0], O[1], "O", 0, -15, 0])
    return F(H1, p, None if show == n else f"Пример для {show} прямых.")

# ------------------------------------------------ § 1
def g1(r):
    out = []
    for _ in range(30):
        n = r.randint(5, 40)
        out.append(T(f"На плоскости отмечено {pl(n,'точка','точки','точек')}, никакие три из которых не лежат на одной прямой. Через каждые две точки провели прямую. Сколько всего прямых провели?",
                     comb(n, 2), "", "Каждая прямая проходит ровно через две точки. Посчитайте пары точек.",
                     [f"Из каждой точки можно провести прямые к остальным {n-1} точкам: {n}·{n-1} = {n*(n-1)}.",
                      "Так каждая прямая посчитана дважды (AB и BA).",
                      f"{n*(n-1)} : 2 = {comb(n,2)}."], fig_points(n, n)))
        n = r.randint(5, 40)
        out.append(T(f"На плоскости проведено {pl(n,'прямая','прямые','прямых')}. Любые две из них пересекаются, никакие три не проходят через одну точку. Найдите число точек пересечения.",
                     comb(n, 2), "", "Каждая пара прямых даёт одну точку пересечения.",
                     [f"Каждая прямая пересекает остальные {n-1}: {n}·{n-1} = {n*(n-1)}.",
                      "Каждая точка посчитана дважды — по одной для каждой из двух прямых.",
                      f"{n*(n-1)} : 2 = {comb(n,2)}."], fig_lines(n, n + 100)))
    for _ in range(20):
        k = r.randint(3, 6); n = r.randint(k + 2, 16)
        out.append(T(f"Отмечено {pl(n,'точка','точки','точек')}. Ровно {k} из них лежат на одной прямой, а других троек точек на одной прямой нет. Сколько различных прямых проходит хотя бы через две отмеченные точки?",
                     comb(n, 2) - comb(k, 2) + 1, "", f"Сначала посчитайте все пары точек, а потом учтите, что пары из {k} точек на одной прямой дают одну прямую.",
                     [f"Всего пар точек: {n}·{n-1} : 2 = {comb(n,2)}.",
                      f"Пары из {k} точек на одной прямой: {k}·{k-1} : 2 = {comb(k,2)}, но все они задают одну прямую.",
                      f"{comb(n,2)} − {comb(k,2)} + 1 = {comb(n,2)-comb(k,2)+1}."], fig_collinear(n, k, n * 7 + k)))
    for _ in range(20):
        k = r.randint(2, 9); m = r.randint(2, 9)
        out.append(T(f"Прямые a и b пересекаются в точке O. На прямой a отмечено {pl(k,'точка','точки','точек')}, на прямой b — {pl(m,'точка','точки','точек')} (точка O не отмечена). Никакие три отмеченные точки, кроме лежащих на a или на b, не лежат на одной прямой. Сколько прямых проходит хотя бы через две отмеченные точки?",
                     2 + k * m, "", "Отдельно посчитайте прямые a и b и прямые, соединяющие точку на a с точкой на b.",
                     ["Точки на прямой a задают одну прямую — саму a. Так же для b.",
                      f"Каждая точка на a соединяется с каждой точкой на b: {k}·{m} = {k*m} прямых.",
                      f"Всего: 2 + {k*m} = {2+k*m}."], fig_two_lines(k, m)))
    for n in range(3, 21):
        out.append(T(f"На какое наибольшее число частей могут разделить плоскость {pl(n,'прямая','прямые','прямых')}?",
                     1 + n + comb(n, 2), "", "Каждая новая прямая, пересекая все предыдущие, добавляет на одну часть больше, чем число точек пересечения на ней.",
                     ["Одна прямая делит плоскость на 2 части.",
                      "k-я прямая пересекает k − 1 прежних и добавляет k новых частей.",
                      f"1 + (1 + 2 + … + {n}) = 1 + {n*(n+1)//2} = {1+n+comb(n,2)}."], fig_lines(n, n + 300)))
    for _ in range(15):
        n = r.randint(5, 15); k = r.randint(2, n - 2)
        out.append(T(f"Проведено {pl(n,'прямая','прямые','прямых')}. Среди них {k} попарно не пересекаются, а все остальные пары прямых пересекаются, причём никакие три прямые не проходят через одну точку. Сколько точек пересечения?",
                     comb(n, 2) - comb(k, 2), "", f"Посчитайте все пары прямых и вычтите пары из тех {k} прямых, которые не пересекаются.",
                     [f"Всего пар прямых: {comb(n,2)}.",
                      f"Не пересекаются пары из {k} прямых: {comb(k,2)}.",
                      f"{comb(n,2)} − {comb(k,2)} = {comb(n,2)-comb(k,2)}."], fig_parallel(n, k)))
    for n in range(3, 15):
        out.append(T(f"Через точку O проведено {pl(n,'прямая','прямые','прямых')}. Затем провели ещё одну прямую, которая не проходит через O и пересекает все эти прямые. Сколько всего точек пересечения?",
                     n + 1, "", "Точка O — одна общая точка; новая прямая даёт свои точки.",
                     ["Первые прямые пересекаются только в точке O — это 1 точка.",
                      f"Новая прямая пересекает каждую из {n} прямых в своей точке — {n} точек.",
                      f"1 + {n} = {n+1}."], fig_concurrent(n)))
    return out

# ------------------------------------------------ § 2
def g2(r):
    out = []
    for _ in range(25):
        a, b, c = r.randint(2, 20), r.randint(2, 20), r.randint(2, 20)
        P4 = [("A", 0), ("B", a), ("C", a + b), ("D", a + b + c)]
        kind = r.randrange(3)
        if kind == 0:
            out.append(T(f"Точки A, B, C, D лежат на прямой в указанном порядке. AB = {a} см, BC = {b} см, CD = {c} см. Найдите AD.", a + b + c, "см",
                         "AD состоит из трёх отрезков.", [f"AD = AB + BC + CD.", f"AD = {a} + {b} + {c} = {a+b+c} см."],
                         seg_fig(P4, [("A", "B", f"{a}", 0, -1), ("B", "C", f"{b}", 0, -1), ("C", "D", f"{c}", 0, -1), ("A", "D", "?", 1, 1)], line=True)))
        elif kind == 1:
            out.append(T(f"Точки A, B, C, D лежат на прямой в указанном порядке. AD = {a+b+c} см, AB = {a} см, CD = {c} см. Найдите BC.", b, "см",
                         "Из всего отрезка AD вычтите крайние части.", [f"AD = AB + BC + CD.", f"BC = AD − AB − CD = {a+b+c} − {a} − {c} = {b} см."],
                         seg_fig(P4, [("A", "B", f"{a}", 0, -1), ("B", "C", "?", 1, -1), ("C", "D", f"{c}", 0, -1), ("A", "D", f"{a+b+c}", 0, 1)], line=True)))
        else:
            out.append(T(f"Точки A, B, C, D лежат на прямой в указанном порядке. AC = {a+b} см, BD = {b+c} см, BC = {b} см. Найдите AD.", a + b + c, "см",
                         "Найдите сначала AB и CD.", [f"AB = AC − BC = {a+b} − {b} = {a} см.", f"CD = BD − BC = {b+c} − {b} = {c} см.", f"AD = AB + BC + CD = {a} + {b} + {c} = {a+b+c} см."],
                         seg_fig(P4, [("B", "C", f"{b}", 0, -1), ("A", "D", "?", 1, -2), ("A", "C", f"{a+b}", 0, 1), ("B", "D", f"{b+c}", 0, 2)], line=True)))
    for _ in range(15):
        y = r.randint(2, 12); d = 2 * r.randint(1, 8); x = y + d
        out.append(T(f"Точка M — середина отрезка AB. Точка C лежит на отрезке MB, AC = {x} см, CB = {y} см. Найдите MC.", d // 2, "см",
                     "Найдите AB, затем AM.", [f"AB = AC + CB = {x} + {y} = {x+y} см.", f"AM = AB : 2 = {fmt((x+y)/2)} см.", f"MC = AC − AM = {x} − {fmt((x+y)/2)} = {d//2} см."],
                     seg_fig([("A", 0), ("M", (x + y) / 2), ("C", x), ("B", x + y)], [("M", "C", "?", 1, -1), ("A", "C", f"{x}", 0, 1), ("C", "B", f"{y}", 0, 1)])))
    for _ in range(15):
        p, q = r.choice([(1, 2), (1, 3), (2, 3), (3, 5), (1, 4), (2, 5), (3, 4)])
        t = 2 * r.randint(1, 6)
        ac, cb = p * t, q * t
        out.append(T(f"Точка C делит отрезок AB в отношении AC : CB = {p} : {q}, AB = {ac+cb} см. Точка M — середина AC. Найдите MB.", ac / 2 + cb, "см",
                     "Найдите длину одной части, затем AC и CB.", [f"Одна часть: {ac+cb} : ({p} + {q}) = {t} см.", f"AC = {ac} см, CB = {cb} см.", f"MC = AC : 2 = {fmt(ac/2)} см.", f"MB = MC + CB = {fmt(ac/2)} + {cb} = {fmt(ac/2+cb)} см."],
                     seg_fig([("A", 0), ("M", ac / 2), ("C", ac), ("B", ac + cb)], [("A", "C", f"{p} ч.", 0, -1), ("C", "B", f"{q} ч.", 0, -1), ("M", "B", "?", 1, 1), ("A", "B", f"{ac+cb}", 0, 2)])))
    for _ in range(15):
        p, q = r.choice([(1, 2), (1, 3), (2, 3), (3, 5), (1, 4), (2, 5), (3, 4), (4, 7), (2, 7)])
        t = r.randint(2, 9)
        out.append(T(f"Точка C лежит на отрезке AB, AC : CB = {p} : {q}, причём CB длиннее AC на {(q-p)*t} см. Найдите AB.", (p + q) * t, "см",
                     "Разность частей соответствует разности чисел в отношении.", [f"Пусть одна часть равна x. Тогда CB − AC = {q}x − {p}x = {q-p}x.", f"{q-p}x = {(q-p)*t}, x = {t} см.", f"AB = {p+q}x = {p+q}·{t} = {(p+q)*t} см."],
                     seg_fig([("A", 0), ("C", p * t), ("B", (p + q) * t)], [("A", "C", f"{p}x", 0, -1), ("C", "B", f"{q}x", 0, -1), ("A", "B", "?", 1, 1)])))
    for _ in range(15):
        a = r.randint(15, 60); x = r.randint(2, a // 2 - 1); y = r.randint(2, max(2, a - x - max(3, a // 4)))
        out.append(T(f"На отрезке AB длиной {a} см отмечены точки C и D так, что AC = {x} см и BD = {y} см, точка C лежит между A и D. Найдите CD.", a - x - y, "см",
                     "Из всего отрезка вычтите две крайние части.", [f"AB = AC + CD + DB.", f"CD = {a} − {x} − {y} = {a-x-y} см."],
                     seg_fig([("A", 0), ("C", x), ("D", a - y), ("B", a)], [("A", "C", f"{x}", 0, -1), ("C", "D", "?", 1, -1), ("D", "B", f"{y}", 0, -1), ("A", "B", f"{a}", 0, 1)])))
    for _ in range(15):
        d1, c1 = r.randint(1, 4), r.randint(1, 9); mm = r.randint(12, 95)
        ab = d1 * 100 + c1 * 10
        out.append(T(f"Точка B лежит между A и C. AB = {d1} дм {c1} см, BC = {mm} мм. Найдите AC в миллиметрах.", ab + mm, "мм",
                     "Переведите все длины в миллиметры: 1 дм = 100 мм, 1 см = 10 мм.", [f"AB = {d1}·100 + {c1}·10 = {ab} мм.", f"AC = AB + BC = {ab} + {mm} = {ab+mm} мм."],
                     seg_fig([("A", 0), ("B", ab), ("C", ab + mm)], [("A", "B", f"{d1} дм {c1} см", 0, -1), ("B", "C", f"{mm} мм", 0, -1), ("A", "C", "?", 1, 1)])))
    for _ in range(15):
        k = r.randint(2, 6); cb = r.randint(2, 9); d = r.randint(1, k * cb - cb - 1) if k * cb - cb > 2 else 1
        ac = k * cb - d
        out.append(T(f"Точка C лежит на отрезке AB. Длина AC на {d} см меньше, чем {k}·CB, а AB = {ac+cb} см. Найдите CB.", cb, "см",
                     "Обозначьте CB через x и составьте уравнение.", [f"Пусть CB = x, тогда AC = {k}x − {d}.", f"x + {k}x − {d} = {ac+cb}, {k+1}x = {ac+cb+d}.", f"x = {ac+cb+d} : {k+1} = {cb} см."],
                     seg_fig([("A", 0), ("C", ac), ("B", ac + cb)], [("A", "C", f"{k}x − {d}", 0, -1), ("C", "B", "x = ?", 1, -1), ("A", "B", f"{ac+cb}", 0, 1)])))
    return out

# ------------------------------------------------ § 3
def g3(r):
    out = []
    for _ in range(20):
        a = r.randint(70, 179); x = r.randint(12, a // 2 - 5); y = r.randint(12, a - x - 14)
        out.append(T(f"Внутри угла AOB, равного {a}°, проведены лучи OC и OD (луч OC ближе к OA). ∠AOC = {x}°, ∠DOB = {y}°. Найдите ∠COD.", a - x - y, "°",
                     "Угол AOB состоит из трёх углов.", [f"∠AOB = ∠AOC + ∠COD + ∠DOB.", f"∠COD = {a}° − {x}° − {y}° = {a-x-y}°."],
                     rays_fig([("A", 0), ("C", x), ("D", a - y), ("B", a)], [(0, x, f"{x}°", 0), (x, a - y, "?", 1), (a - y, a, f"{y}°", 0)])))
    for _ in range(15):
        a = 2 * r.randint(30, 85); x = r.randint(8, a // 2 - 12)
        out.append(T(f"OC — биссектриса угла AOB, ∠AOB = {a}°. Луч OD лежит внутри угла COB, ∠COD = {x}°. Найдите ∠AOD.", a // 2 + x, "°",
                     "Сначала найдите ∠AOC.", [f"∠AOC = ∠AOB : 2 = {a//2}°.", f"∠AOD = ∠AOC + ∠COD = {a//2}° + {x}° = {a//2+x}°."],
                     rays_fig([("A", 0), ("C", a // 2), ("D", a // 2 + x), ("B", a)], [(a // 2, a // 2 + x, f"{x}°", 0), (0, a // 2 + x, "?", 1), (0, a, f"{a}°", 0)], dashed=("C",))))
    for _ in range(15):
        p, q, s = r.choice([(1, 2, 3), (2, 3, 4), (1, 3, 5), (1, 2, 6), (2, 3, 5), (3, 4, 5), (1, 1, 2), (1, 4, 4), (2, 5, 8)])
        t = r.randint(3, 179 // (p + q + s))
        A = (p + q + s) * t
        out.append(T(f"Лучи OC и OD делят угол AOB на три угла: ∠AOC : ∠COD : ∠DOB = {p} : {q} : {s}. ∠AOB = {A}°. Найдите ∠DOB.", s * t, "°",
                     "Найдите градусную меру одной части.", [f"Всего частей: {p} + {q} + {s} = {p+q+s}.", f"Одна часть: {A}° : {p+q+s} = {t}°.", f"∠DOB = {s}·{t}° = {s*t}°."],
                     rays_fig([("A", 0), ("C", p * t), ("D", (p + q) * t), ("B", A)], [(0, p * t, f"{p}x", 0), (p * t, (p + q) * t, f"{q}x", 0), ((p + q) * t, A, "?", 1)],
                              cap=f"∠AOB = {A}°")))
    for _ in range(15):
        y = r.randint(10, 70); d = 2 * r.randint(2, 25); x = y + d
        if x + y >= 180: continue
        m = (x + y) / 2
        out.append(T(f"Луч OC проходит внутри угла AOB, ∠AOC = {x}°, ∠COB = {y}°. OM — биссектриса угла AOB. Найдите ∠MOC.", d // 2, "°",
                     "Найдите ∠AOB и ∠AOM.", [f"∠AOB = {x}° + {y}° = {x+y}°.", f"∠AOM = {x+y}° : 2 = {fmt(m)}°.", f"∠MOC = ∠AOC − ∠AOM = {x}° − {fmt(m)}° = {d//2}°."],
                     rays_fig([("B", 0), ("C", y), ("M", m), ("A", x + y)], [(0, y, f"{y}°", 0), (y, m, "?", 1), (y, x + y, f"{x}°", 0)], dashed=("M",))))
    for h in range(1, 12):
        for m in r.sample([10, 20, 40, 50], 2):
            hour = 30 * h + m / 2; minute = 6 * m
            ang = abs(hour - minute); ang = min(ang, 360 - ang)
            out.append(T(f"Найдите меньший угол между часовой и минутной стрелками в {h}:{m:02d}.", ang, "°",
                         "Минутная стрелка проходит 6° в минуту, часовая — 0,5° в минуту.",
                         [f"Минутная стрелка: {m}·6° = {minute}° от отметки 12.", f"Часовая стрелка: {h}·30° + {m}·0,5° = {fmt(hour)}°.", f"Разность: |{fmt(hour)}° − {minute}°| = {fmt(abs(hour-minute))}°" + (f", меньший угол 360° − {fmt(abs(hour-minute))}° = {fmt(ang)}°." if abs(hour - minute) > 180 else ".")],
                         clock_fig(h, m)))
    for _ in range(15):
        a = r.randint(60, 178); x = r.randint(10, a - 10)
        out.append(T(f"Луч OC проходит внутри угла AOB, ∠AOB = {a}°, ∠AOC = {x}°. Найдите ∠COB в минутах.", (a - x) * 60, "′",
                     "Найдите угол в градусах, затем умножьте на 60.", [f"∠COB = {a}° − {x}° = {a-x}°.", f"1° = 60′, {a-x}° = {(a-x)*60}′."],
                     rays_fig([("A", 0), ("C", x), ("B", a)], [(0, x, f"{x}°", 0), (x, a, "?", 1), (0, a, f"{a}°", 0)])))
    return out

# ------------------------------------------------ § 4
def g4(r):
    out = []
    for _ in range(15):
        p, q = r.choice([(1, 2), (1, 3), (2, 3), (1, 5), (4, 5), (1, 8), (2, 7), (7, 11), (5, 13), (1, 4), (3, 7)])
        t = 180 // (p + q)
        big = q * t
        out.append(T(f"Смежные углы относятся как {p} : {q}. Найдите угол между биссектрисой большего угла и общей стороной этих углов.", big / 2, "°",
                     "Найдите больший угол, затем его половину.", [f"{p}x + {q}x = 180°, x = {t}°.", f"Больший угол: {q}·{t}° = {big}°.", f"Биссектриса делит его пополам: {fmt(big/2)}°."],
                     rays_fig([("C", 0), ("B", p * t), ("M", p * t + big / 2), ("A", 180)], [(0, p * t, f"{p}x", 0), (p * t, p * t + big / 2, "?", 1), (p * t, 180, f"{q}x", 0)], dashed=("M",),
                              cap="OM — биссектриса большего угла")))
    for _ in range(15):
        x = 2 * r.randint(8, 85)
        n = x + (180 - x) / 2
        out.append(T(f"Углы AOB и BOC смежные, ∠AOB = {x}°. ON — биссектриса угла BOC. Найдите ∠AON.", 90 + x / 2, "°",
                     "Найдите ∠BOC, затем ∠BON.", [f"∠BOC = 180° − {x}° = {180-x}°.", f"∠BON = {180-x}° : 2 = {fmt((180-x)/2)}°.", f"∠AON = ∠AOB + ∠BON = {x}° + {fmt((180-x)/2)}° = {fmt(90+x/2)}°."],
                     rays_fig([("A", 0), ("B", x), ("N", n), ("C", 180)], [(0, x, f"{x}°", 0), (0, n, "?", 1)], dashed=("N",))))
    for _ in range(20):
        x = r.randint(20, 90); y = r.randint(15, 160 - x)
        out.append(T(f"Прямые AB, CD и EF пересекаются в точке O. Лучи идут по кругу в порядке OA, OC, OE, OB, OD, OF. ∠AOC = {x}°, ∠COE = {y}°. Найдите ∠EOB.", 180 - x - y, "°",
                     "∠AOB развёрнутый, он состоит из трёх углов.", [f"∠AOB = 180° = ∠AOC + ∠COE + ∠EOB.", f"∠EOB = 180° − {x}° − {y}° = {180-x-y}°."],
                     rays_fig([("A", 0), ("C", x), ("E", x + y), ("B", 180), ("D", 180 + x), ("F", 180 + x + y)], [(0, x, f"{x}°", 0), (x, x + y, f"{y}°", 0), (x + y, 180, "?", 1)], full=True)))
    for _ in range(25):
        s = r.randint(20, 80); k = r.randint(2, 6); d = s * (k + 1) - 180
        if d <= 0 or k * s - d <= s: continue
        out.append(T(f"Один из смежных углов на {d}° меньше, чем другой угол, умноженный на {k}. Найдите меньший угол.", s, "°",
                     "Обозначьте меньший угол через x и составьте уравнение.", [f"Пусть меньший угол x, тогда больший {k}x − {d}°.", f"x + {k}x − {d}° = 180°, {k+1}x = {180+d}°.", f"x = {180+d}° : {k+1} = {s}°."],
                     rays_fig([("C", 0), ("B", s), ("A", 180)], [(0, s, "x = ?", 1), (s, 180, f"{k}x − {d}°", 0)])))
    for _ in range(15):
        s = r.randint(215, 330); x = 360 - s
        out.append(T(f"При пересечении двух прямых сумма одного из углов и двух смежных с ним углов равна {s}°. Найдите этот угол.", x, "°",
                     "Смежные с углом x углы равны 180° − x.", [f"x + 2·(180° − x) = {s}°.", f"360° − x = {s}°.", f"x = {x}°."],
                     rays_fig([("A", 0), ("C", x), ("B", 180), ("D", 180 + x)], [(0, x, "1", 1), (x, 180, "2", 0), (180 + x, 360, "3", 0)], full=True,
                              cap=f"∠1 + ∠2 + ∠3 = {s}°, найдите ∠1")))
    for _ in range(15):
        x = r.randint(10, 85)
        out.append(T(f"Прямые AB и CD пересекаются в точке O, ∠AOC = {x}°. OM — биссектриса угла BOD. Найдите ∠AOM.", 180 - x / 2, "°",
                     "∠BOD вертикален ∠AOC.", [f"∠BOD = ∠AOC = {x}° (вертикальные).", f"∠BOM = {fmt(x/2)}°.", f"∠AOM = 180° − ∠BOM = 180° − {fmt(x/2)}° = {fmt(180-x/2)}° (∠AOB развёрнутый)."],
                     rays_fig([("A", 0), ("C", x), ("B", 180), ("M", 180 + x / 2), ("D", 180 + x)], [(0, x, f"{x}°", 0), (180 + x / 2, 360, "?", 1)], dashed=("M",), full=True)))
    for _ in range(15):
        d = 2 * r.randint(3, 80); big = (180 + d) // 2
        out.append(T(f"Один из углов, образованных при пересечении двух прямых, на {d}° больше другого. Найдите больший угол.", big, "°",
                     "Неравные углы при пересечении прямых — смежные.", ["Вертикальные углы равны, значит, эти углы смежные.", f"x + x + {d}° = 180°, x = {(180-d)//2}°.", f"Больший угол: {(180-d)//2}° + {d}° = {big}°."],
                     rays_fig([("A", 0), ("C", big), ("B", 180), ("D", 180 + big)], [(0, big, "?", 1), (big, 180, "x", 0)], full=True,
                              cap=f"Один угол на {d}° больше другого")))
    return out

# ------------------------------------------------ § 5
def g5(r):
    out = []
    for _ in range(20):
        x = r.randint(5, 85)
        out.append(T(f"Прямые AB и CD перпендикулярны и пересекаются в точке O. OK — биссектриса угла AOC, луч OM лежит внутри угла COB, ∠COM = {x}°. Найдите ∠KOM.", 45 + x, "°",
                     "∠AOC = 90°, его биссектриса даёт 45°.", ["∠KOC = 90° : 2 = 45°.", f"∠KOM = ∠KOC + ∠COM = 45° + {x}° = {45+x}°."],
                     rays_fig([("B", 0), ("M", 90 - x), ("C", 90), ("K", 135), ("A", 180), ("D", 270)], [(90 - x, 90, f"{x}°", 0), (90 - x, 135, "?", 1)],
                              rights=(270,), dashed=("K",), full=True)))
    for _ in range(15):
        y = 2 * r.randint(3, 42)
        m = y + (90 - y) / 2
        out.append(T(f"∠AOB = 90°, луч OC проходит внутри него, ∠COB = {y}°. OM — биссектриса угла AOC. Найдите ∠MOB.", 45 + y / 2, "°",
                     "Найдите ∠AOC, затем ∠MOC.", [f"∠AOC = 90° − {y}° = {90-y}°.", f"∠MOC = {90-y}° : 2 = {fmt((90-y)/2)}°.", f"∠MOB = ∠MOC + ∠COB = {fmt((90-y)/2)}° + {y}° = {fmt(45+y/2)}°."],
                     rays_fig([("B", 0), ("C", y), ("M", m), ("A", 90)], [(0, y, f"{y}°", 0), (0, m, "?", 1)], rights=(0,), dashed=("M",))))
    for _ in range(15):
        p, q = r.choice([(1, 2), (1, 4), (2, 3), (1, 5), (4, 5), (1, 8), (2, 7), (1, 2), (7, 8), (4, 11)])
        t = 90 // (p + q)
        dd = 180 - p * t
        out.append(T(f"OC ⟂ AB (точка O лежит на прямой AB). Луч OD лежит внутри угла AOC, ∠AOD : ∠DOC = {p} : {q}. Найдите ∠DOB.", 90 + q * t, "°",
                     "∠AOC = 90°. Найдите ∠DOC, затем прибавьте ∠COB.", [f"{p}x + {q}x = 90°, x = {t}°.", f"∠DOC = {q}·{t}° = {q*t}°.", f"∠DOB = ∠DOC + ∠COB = {q*t}° + 90° = {90+q*t}°."],
                     rays_fig([("B", 0), ("C", 90), ("D", dd), ("A", 180)], [(dd, 180, f"{p}x", 0), (90, dd, f"{q}x", 0), (0, dd, "?", 1)], rights=(0,))))
    for _ in range(15):
        x = r.randint(5, 85)
        out.append(T(f"Прямые a и b перпендикулярны и пересекаются в точке O. Через O проведена прямая c, которая образует с прямой a угол {x}°. Найдите меньший угол между прямыми c и b.", 90 - x, "°",
                     "Угол между a и b равен 90°, прямая c проходит внутри одного из прямых углов.", [f"Луч прямой c лежит внутри прямого угла между a и b.", f"Угол между c и b: 90° − {x}° = {90-x}°."],
                     rays_fig([("a", 0), ("c", x), ("b", 90), ("", 180), ("", 180 + x), ("", 270)], [(0, x, f"{x}°", 0), (x, 90, "?", 1)],
                              rights=(90,), full=True, names=("a", "b", "c"))))
    for _ in range(15):
        x = r.randint(10, 85)
        rs = [("A", 0), ("B", x), ("C", 90), ("D", x + 90)]
        out.append(T(f"∠AOB = {x}°. Лучи OC и OD проведены так, что OC ⟂ OA, OD ⟂ OB, и лучи OB, OC, OD лежат по одну сторону от прямой OA (в порядке OB, OC, OD). Найдите ∠BOC.", 90 - x, "°",
                     "∠AOC = 90°, луч OB лежит внутри него.", [f"∠AOC = 90°.", f"∠BOC = ∠AOC − ∠AOB = 90° − {x}° = {90-x}°."],
                     rays_fig(rs, [(0, x, f"{x}°", 0), (x, 90, "?", 1)], rights=(0,))))
        out.append(T(f"∠AOB = {x}°. Лучи OC и OD проведены так, что OC ⟂ OA, OD ⟂ OB, и лучи OB, OC, OD лежат по одну сторону от прямой OA (в порядке OB, OC, OD). Найдите ∠COD.", x, "°",
                     "∠BOD = 90°, а ∠BOC вы можете найти.", [f"∠BOC = 90° − {x}° = {90-x}°.", f"∠COD = ∠BOD − ∠BOC = 90° − {90-x}° = {x}°."],
                     rays_fig(rs, [(0, x, f"{x}°", 0), (90, x + 90, "?", 1)], rights=(0,))))
    for _ in range(15):
        x = r.randint(105, 168)
        out.append(T(f"∠AOB = {x}°. Внутри угла проведены лучи OC и OD, OC ⟂ OA, OD ⟂ OB. Найдите ∠COD.", 180 - x, "°",
                     "Найдите сначала ∠AOD.", [f"∠AOD = ∠AOB − ∠DOB = {x}° − 90° = {x-90}°.", f"∠COD = ∠AOC − ∠AOD = 90° − {x-90}° = {180-x}°."],
                     rays_fig([("A", 0), ("D", x - 90), ("C", 90), ("B", x)], [(x - 90, 90, "?", 1), (0, x, f"{x}°", 0)], rights=(0, x - 90))))
    for _ in range(15):
        k = r.choice([2, 3, 4, 5, 8, 9, 14, 17]); s = 90 // (k + 1)
        if 90 % (k + 1): continue
        out.append(T(f"Луч OC проходит внутри прямого угла AOB, угол AOC {raz(k)} больше угла COB. Найдите ∠AOC.", k * s, "°",
                     "Обозначьте ∠COB через x.", [f"x + {k}x = 90°, x = 90° : {k+1} = {s}°.", f"∠AOC = {k}·{s}° = {k*s}°."],
                     rays_fig([("B", 0), ("C", s), ("A", 90)], [(0, s, "x", 0), (s, 90, f"{k}x = ?", 1)], rights=(0,))))
    return out

def take(gens, r, n, seen):
    pool = []
    for g in gens:
        pool += g(r) + g(r)
    r.shuffle(pool)
    out = []
    for t in pool:
        if t["q"] in seen: continue
        seen.add(t["q"]); out.append(t)
        if len(out) == n: break
    assert len(out) == n, (gens, len(out))
    return out

def main():
    seen = set()
    res = []
    for i, g in enumerate([g1, g2, g3, g4, g5]):
        res.append(take([g], random.Random(100 + i), 100, seen))
    res.append(take([g1, g2, g3, g4, g5], random.Random(777), 100, seen))
    items = []
    for ti, ts in enumerate(res):
        for t in ts:
            assert t["f"], t["q"]
            items.append([ti, t["q"], round(t["a"], 4), t["u"], t["h"], t["s"], t["f"]])
        print(ti, len(ts), file=sys.stderr)
    json.dump(items, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

main()

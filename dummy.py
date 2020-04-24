import re
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from logik.table import Table
from logik.regression import SimpleRegression


def regression(x, y):
    x, y = np.array(x), np.array(y)
    x = np.log10(x)
    y = np.log10(y)
    tab = Table(columns=2, column_names=["x", "y"])
    for x_, y_ in zip(x, y):
        tab.add((float(x_), float(y_)))
    a = SimpleRegression(tab, {"x": 0, "y": 1})
    # print(f"m: {a.b}\ny: {a.a}")
    a_2 = a.b * 2
    print(f"delta_stds: {(1 + a_2.value) / a_2.error}")
    f = np.vectorize(lambda x: 10 ** (a.b.value * x + a.a.value))
    return f(x)


def auswertung(paths, names=[]):
    frq_pattern = re.compile("FRQ\[\d*\]")
    df_pattern = re.compile("DF\[[\d.]*\]")
    pra_pattern = re.compile("PRA\[[\d.]\]")

    all_pras = []
    all_frqs = []
    all_sin_stds = []
    all_cos_stds = []
    all_sin_means = []
    all_cos_means = []
    for path in paths:
        files = [file for file in os.listdir(path) if file[-4:] == ".csv"]
        sin_stds = []
        cos_stds = []

        sin_means = []
        cos_means = []
        frqs = []

        for file in files:
            data = open(path + "\\" + file, "r")
            lines = data.readlines()
            datas = list(zip(*[line.split(";")[1:] for line in lines[1:]]))

            sin = []
            for data in datas[0]:
                try:
                    sin.append(float(data.replace("\n", "")))
                except:
                    pass

            cos = []
            for data in datas[1]:
                try:
                    cos.append(float(data.replace("\n", "")))
                except:
                    pass

            frq = int(re.findall(frq_pattern, file)[0][4:-1])
            pra = int(re.findall(pra_pattern, file)[0][4:-1])
            df = float(re.findall(df_pattern, file)[0][3:-1]) ** 0.5
            frqs.append(int(frq))

            s_mean = sum(sin) / len(sin)
            # s_mean = np.mean(np.array(sin))
            c_mean = sum(cos) / len(cos)
            # c_mean = np.mean(np.array(cos))
            s_sa = (sum([(s - s_mean) ** 2 for s in sin]) / (len(sin) - 1)) ** 0.5
            # s_sa = np.std(np.array(sin))
            c_sa = (sum([(s - c_mean) ** 2 for s in cos]) / (len(cos) - 1)) ** 0.5
            # c_sa = np.std(np.array(cos))
            sin_stds.append(s_sa / (df))
            cos_stds.append(c_sa / (df))
            sin_means.append(s_mean)
            cos_means.append(c_mean)

        # sort all
        f_sorting = list(zip(frqs, sin_stds, cos_stds, sin_means, cos_means))
        f_sorting.sort(key=lambda x: x[0])
        frqs, sin_stds, cos_stds, sin_means, cos_means = list(zip(*f_sorting))

        all_pras.append(pra)
        all_frqs.append(frqs)
        all_sin_stds.append(sin_stds)
        all_cos_stds.append(cos_stds)
        all_sin_means.append(sin_means)
        all_cos_means.append(cos_means)

    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Frequenz [Hz]")
    plt.ylabel("Standardabweichung / $\sqrt{f_{NEP}}$ [V/$\sqrt{Hz}$]")
    plt.title("Standardabweichung des Lock-In Amplifiers     13.02.2020\n" +
              " bei verschiedenen Vorverstärkungsstufen                          ")

    names += [""] * (len(all_pras) - len(names))
    colors = ["r", "b", "g", "peru", "dimgrey"]
    handles = []
    for pra, sin_stds, frqs, cos_stds, name, color in zip(all_pras, all_sin_stds, all_frqs, all_cos_stds, names,
                                                          colors):
        sins_reg = regression(frqs, sin_stds)
        plt.plot(frqs, sins_reg, "--", color=color)
        plt.plot(frqs, sin_stds, "x", color=color, ms=4)
        handles.append(mpatches.Patch(color=color, label=f"Messung für PRA = {pra}"))
    handles.append(Line2D([0], [0], ls="--", label="Lineare Regression", color="black"))
    handles.append(Line2D([0], [0], ls="None", marker="x", label="Messpunkte", color="black"))
    plt.legend(handles=handles, fontsize="small")
    plt.show()

    """plt.plot(list(range(len(cos_means))), cos_means, "r", label="Arithm. Mittelwert bei Mischung mit Referenzcosinus")
    plt.plot(list(range(len(sin_means))), sin_means, "b", label="Arithm. Mittelwert bei Mischung mit Referenzsinus")
    plt.plot(list(range(len(sin_means))), [sum(sin_means) / len(sin_means)] * len(sin_means),
             label="Arithm. Mittelwert Sinus")
    plt.plot(list(range(len(cos_means))), [sum(cos_means) / len(cos_means)] * len(cos_means),
             label="Arithm. Mittelwert Cosinus")
    plt.legend()
    plt.show()"""


username = os.getlogin()
if username == "Daniel":
    messungen_path = r"C:\Users\Daniel\Dropbox\C2_Praktikum\Lock-In_Dokumentation\Spezificationen\Messungen_pras\\"
else:
    messungen_path = r"C:\Users\NPC\Desktop\Messungen\\"

auswertung([messungen_path + "PRA0_120s",
            messungen_path + "PRA1_120s",
            messungen_path + "PRA2_120s",
            messungen_path + "PRA3_120s",
            messungen_path + "PRA4_120s"],
           names=["Sinus für"] * 5)


"""
13.02.2020
Messungen:
    PRA0_sin_cos_offset

Raumtemperatur: 19.4°C
Messgerät Voltcraft Multi-Termometer DT-300
"""

"""
Mögliche Verbesserungen des LOCK-INS
1. neue FRQ einstellungsfunktion welche psc berücksichtigt 
    -> z.B. FRQ primfaktorzerlegen und daraus die beiden Zahlen PSC und ARR berechnen
2. höhere Harmonische mit einbauen
3. SYNC with extern signal möglich machen
4. Allgemeine Code optimierung (*3.3 V z.B. nur bei Abfrage nötig...)
"""
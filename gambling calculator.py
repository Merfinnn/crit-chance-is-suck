import tkinter as tk
from tkinter import ttk, messagebox
import math

CRIT_CONST = 666.6666666666667


def get_float(entry, allow_blank=True):
    value = entry.get().strip()
    if value == "":
        if allow_blank:
            return 0.0
        raise ValueError("Required field cannot be blank")
    return float(value)

def binomial_prob(n, k, p):
    return math.comb(n, k) * (p ** k) * ((1 - p) ** (n - k))

def calculate_crit_chance(BC, BCR, X, Y, CP, DCRP):
    C  = (BC + X) * (1 + CP / 100) + Y
    CR = BCR * (1 - DCRP / 100)
    FC = C - CR

    if FC + CRIT_CONST == 0:
        raise ValueError("Final Crit + constant must not be zero")

    CC = FC / (FC + CRIT_CONST)

    if not (0 <= CC <= 1):
        raise ValueError(f"Crit Chance out of range: {CC}")

    return CC

def calculate_binomial():
    try:
        n = int(get_float(entry_n, allow_blank=False))

        BC  = get_float(entry_BC,  allow_blank=False)
        BCR = get_float(entry_BCR, allow_blank=False)

        if BC == 0 or BCR == 0:
            raise ValueError("Crit Base and CritRes Base must not be 0")

        X    = get_float(entry_X)
        Y    = get_float(entry_Y)
        CP   = get_float(entry_CP)
        DCRP = get_float(entry_DCRP)

        p = calculate_crit_chance(BC, BCR, X, Y, CP, DCRP)

    except ValueError as e:
        messagebox.showerror("Input Error", str(e))
        return

    label_cc.config(text=f"Crit Chance (p) = {p:.16f}")

    for row in tree.get_children():
        tree.delete(row)

    x_vals = list(range(n + 1))
    exact_probs = [binomial_prob(n, k, p) for k in x_vals]

    cumulative_probs = [0.0] * (n + 1)
    running_sum = 0.0
    for i in reversed(range(n + 1)):
        running_sum += exact_probs[i]
        cumulative_probs[i] = running_sum

    y_vals = []

    for k in x_vals:
        exact = exact_probs[k]
        cumulative = cumulative_probs[k]

        y_vals.append(exact)

        one_in_exact = f"{1 / exact:.2f}" if exact > 0 else "∞"
        one_in_cum   = f"{1 / cumulative:.2f}" if cumulative > 0 else "∞"

        tree.insert(
            "",
            "end",
            values=(
                f"{k}/{n}",
                f"{exact:.16f}",
                one_in_exact,
                f"{cumulative:.16f}",
                one_in_cum
            )
        )

root = tk.Tk()
root.title("gambling calculator")
root.geometry("900x600")

frame_top = tk.Frame(root)
frame_top.pack(pady=12)

frame_input = tk.Frame(frame_top)
frame_input.pack(side="left", padx=10)

frame_button = tk.Frame(frame_top)
frame_button.pack(side="right", padx=20)

def add_row(label, entry, row, default=""):
    tk.Label(frame_input, text=label).grid(row=row, column=0, sticky="w", padx=5)
    entry.grid(row=row, column=1, padx=5)
    entry.insert(0, default)

def add_pair(label1, entry1, label2, entry2, row):
    tk.Label(frame_input, text=label1).grid(row=row, column=0, sticky="w", padx=5)
    entry1.grid(row=row, column=1, padx=5)

    tk.Label(frame_input, text=label2).grid(row=row, column=2, sticky="w", padx=5)
    entry2.grid(row=row, column=3, padx=5)

tk.Label(frame_input, text="Base Stats", font=("Segoe UI", 10, "bold"))\
    .grid(row=0, column=0, columnspan=1, sticky="w", pady=(0, 5))

tk.Label(frame_input, text="Modifiers", font=("Segoe UI", 10, "bold"))\
    .grid(row=0, column=2, columnspan=3, sticky="w", pady=(0, 5))

entry_n    = tk.Entry(frame_input, width=14)
entry_BC   = tk.Entry(frame_input, width=14)
entry_BCR  = tk.Entry(frame_input, width=14)
entry_X    = tk.Entry(frame_input, width=14)
entry_Y    = tk.Entry(frame_input, width=14)
entry_CP   = tk.Entry(frame_input, width=14)
entry_DCRP = tk.Entry(frame_input, width=14)

entry_n.insert(0, "7")

add_pair("n (trials)", entry_n,
         "Crit from equipment", entry_X, 1)

add_pair("Crit Base", entry_BC,
         "Crit from skill", entry_Y, 2)

add_pair("CritRes Base", entry_BCR,
         "Crit Buff (%)", entry_CP, 3)

add_pair("", tk.Label(frame_input),
         "Crit Debuff (%)", entry_DCRP, 4)

tk.Button(
    frame_button,
    text="Calculate",
    width=14,
    height=2,
    command=calculate_binomial
).pack(expand=True)

label_cc = tk.Label(root, text="Crit Chance (p) = -", font=("Segoe UI", 10))
label_cc.pack(pady=6)

columns = (
    "k/n",
    "P(X = k)",
    "1 in X (= k)",
    "P(X ≥ k)",
    "1 in X (≥ k)"
)

tree = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    if col == "k/n":
        tree.column(col, anchor="center", width=70, stretch=False)
    else:
        tree.column(col, anchor="center")

tree.pack(expand=True, fill="both", padx=10, pady=10)

show_graph = tk.BooleanVar(value=False)

root.mainloop()
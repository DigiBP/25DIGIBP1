import json

import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
import webbrowser, threading, os
from collections import Counter, defaultdict

# read config file
with open("../config.json", "r") as f:
    config = json.load(f)
f.close()

WEBAPP_HOST_IP = config["webappHostIP"]
WEBAPP_PORT = config["webappPort"]

FILE = "../form_data.xlsx"
SHEET = "feedbackData"

#  Statuses that count as completed
CLOSED_STATES = {"completed", "cancelled", "terminate"}

# Mapping of feedback type values to more understandable values
FEEDBACK_TYPE_MAP = {
    "ftNegative":   "Negativ",
    "ftPositive":   "Positiv",
    "ftSuggestion": "Vorschlag"
}

URGENCY_MAP = {
    "uLow":   "Niedrig",
    "uMedium":   "Mittel",
    "uHigh": "Hoch"
}

IMPACTSCOPE_MAP = {
    "isSpecific":   "Spezifisch",
    "isSmall":   "Klein",
    "isLarge": "Gross"
}

# Mapping of colors to specific statuses and feedback types for the dashboard
STATUS_COLOR_MAP = {
    "open":         "#81d4fa",   # light blue
    "review-board": "#fff59d",   # light yellow
    "terminate":    "#90a4ae",   # medium grey
    "cancelled":    "#cfd8dc",   # light grey
    "withdrawn":    "#ef9a9a",   # light red
    "closed":       "#4f9a58",   # SVK green
    "completed":    "#4f9a58"    # SVK green
}

TYPE_COLOR_MAP = {
    "Negativ":     "#ef9a9a",   # light red
    "Positiv":     "#4f9a58",   # SVK green
    "Vorschlag":   "#aed581",   # light green
    "Undefiniert": "#eceff1"    # light grey
}

app = Flask(__name__)
app.secret_key = "any-pgp-wordlist-here"          # necessary for flash messages


# ---------- Helper functions --------------------------------------------------
def read_data() -> pd.DataFrame:
    df = pd.read_excel(
        FILE,
        sheet_name=SHEET,
        dtype={"businessKey": str},
    )
    df["feedbackDate"] = pd.to_datetime(df["feedbackDate"],
                                        dayfirst=True,
                                        errors="coerce")

    # Apply mapping of german values
    df["feedbackTypeDE"] = df["feedbackType"].map(FEEDBACK_TYPE_MAP) \
        .fillna(df["feedbackType"])

    df["urgencyDE"] = df["urgency"].map(URGENCY_MAP) \
        .fillna(df["urgency"])

    df["impactScopeDE"] = df["impactScope"].map(IMPACTSCOPE_MAP) \
        .fillna(df["impactScope"])

    return df

def write_data(df: pd.DataFrame):
    df["businessKey"] = df["businessKey"].astype(str)
    df.to_excel(FILE, sheet_name=SHEET, index=False)

def render_lists(df: pd.DataFrame):
    closed = df[df["status"].str.lower().isin(CLOSED_STATES)].copy()
    open_  = df[~df["status"].str.lower().isin(CLOSED_STATES)].copy()
    # Create name & preview to avoid looping in the template
    for frame in (open_, closed):
        frame["name"]    = frame["firstName"].fillna("") + " " + frame["lastName"].fillna("")
        frame["preview"] = frame["feedbackText"].str[:60].fillna("") + "…"
    return open_, closed

# ---------- Routing -----------------------------------------------------------
@app.route("/")
def index():
    df = read_data().reset_index(names="_idx")
    open_, closed = render_lists(df)

    # Collect dashboard data
    all_df = pd.concat([open_, closed], ignore_index=True)

    # all NaN of classification values are mapped to "Undefiniert" for visualization purposes
    all_df["feedbackTypeDE"] = all_df["feedbackTypeDE"].fillna("Undefiniert")
    all_df["urgencyDE"] = all_df["urgencyDE"].fillna("Undefiniert")
    all_df["impactScopeDE"] = all_df["impactScopeDE"].fillna("Undefiniert")

    records = all_df.to_dict("records")

    # 1) Status distribution  + colors
    status_counts = Counter(r["status"] for r in records)
    status_labels = list(status_counts.keys())
    status_values = list(status_counts.values())
    status_colors = [STATUS_COLOR_MAP.get(s, "#cccccc") for s in status_labels]

    # 2) Feedback type distribution + colors
    type_counts = Counter(r["feedbackTypeDE"] for r in records)
    type_labels = list(type_counts.keys())
    type_values = list(type_counts.values())
    type_colors = [TYPE_COLOR_MAP.get(t, "#cccccc") for t in type_labels]

    # 3) Time series: Number of feedbacks per day
    date_counts = defaultdict(int)
    for r in records:
        dt = r["feedbackDate"]
        if not pd.isna(dt):
            d = pd.to_datetime(dt).date().isoformat()
            date_counts[d] += 1
    sorted_dates = sorted(date_counts)
    time_labels  = sorted_dates
    time_counts  = [date_counts[d] for d in sorted_dates]

    chart_data = {
        "status": {"labels": status_labels, "counts": status_values,
                   "colors": status_colors},
        "type": {"labels": type_labels, "counts": type_values,
                 "colors": type_colors},
        "time": {"labels": time_labels, "counts": time_counts}
    }

    return render_template(
        "overview.html",
        open=open_.to_dict("records"),
        closed=closed.to_dict("records"),
        chart_data=chart_data
    )

@app.route("/detail/<int:idx>")
def detail(idx):
    df = read_data()
    try:
        row = df.loc[idx].copy()
    except KeyError:
        flash("Datensatz nicht gefunden.", "danger")
        return redirect(url_for("index"))

    # Convert all NaN values to empty strings
    row = row.where(pd.notnull(row), "")

    return render_template("detail.html", row=row.to_dict(), idx=idx)

@app.post("/terminate/<int:idx>")
def terminate(idx):
    df = read_data()
    status = str(df.at[idx, "status"]).lower()

    if status == "terminate":
        flash("Sie haben das Feedback bereits terminiert.", "warning")
        return redirect(url_for("detail", idx=idx))

    if status == "complete":
        flash("Das Feedback wurde bereits abgeschlossen.", "warning")
        return redirect(url_for("detail", idx=idx))

    if status == "cancelled":
        flash("Dieses Feedback wurde bereits terminiert.", "warning")
        return redirect(url_for("detail", idx=idx))

    df.at[idx, "status"] = "terminate"
    write_data(df)
    flash("Feedback terminiert.", "success")
    return redirect(url_for("index"))

@app.post("/update_measures/<int:idx>")
def update_measures(idx):
    measures = (request.form.get("measuresTaken") or "").strip()
    if not measures or measures.lower() == "nan":
        flash("Bitte geben Sie getroffene Massnahmen ein.", "warning")
        return redirect(url_for("detail", idx=idx))

    df = read_data()
    df.at[idx, "measuresTaken"] = measures
    write_data(df)
    flash("Massnahmen gespeichert.", "success")
    return redirect(url_for("detail", idx=idx))


@app.post("/complete_feedback/<int:idx>")
def complete_feedback(idx):
    measures = request.form.get("measuresTaken", "").strip()
    df = read_data()
    status = str(df.at[idx, "status"]).lower()

    if status != "review-board":
        flash("Das Feedback muss im Status 'Review-Board' sein, bevor es abgeschlossen werden kann.", "warning")
        return redirect(url_for("detail", idx=idx))

    if not measures or measures.lower() == "nan":
        flash("Dokumentieren Sie Massnahmen, um das Feedback abzuschliessen.", "warning")
        return redirect(url_for("detail", idx=idx))

    df.at[idx, "measuresTaken"] = measures
    df.at[idx, "status"] = "completed"
    write_data(df)
    flash("Feedback abgeschlossen.", "success")
    return redirect(url_for("index"))

# ---------- Start app ------------------------------------------------------
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    # Browser automatisch öffnen
    threading.Timer(1.0, open_browser).start()
    app.run(host=WEBAPP_HOST_IP, port=WEBAPP_PORT, debug=False)

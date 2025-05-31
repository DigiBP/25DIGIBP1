import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
import webbrowser, threading, os
from collections import Counter, defaultdict

FILE = "../form_data.xlsx"
SHEET = "feedbackData"

#  Statuses that count as completed
CLOSED_STATES = {"completed", "cancelled", "terminate"}

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
    return df

def write_data(df: pd.DataFrame):
    df["businessKey"] = df["businessKey"].astype(str)
    df.to_excel(FILE, sheet_name=SHEET, index=False)

def render_lists(df: pd.DataFrame):
    closed = df[df["status"].str.lower().isin(CLOSED_STATES)].copy()
    open_  = df[~df["status"].str.lower().isin(CLOSED_STATES)].copy()
    # Name & Preview erzeugen, um nicht im Template zu loopen
    for frame in (open_, closed):
        frame["name"]    = frame["firstName"].fillna("") + " " + frame["lastName"].fillna("")
        frame["preview"] = frame["feedbackText"].str[:60].fillna("") + "…"
    return open_, closed

# ---------- Routing -----------------------------------------------------------
@app.route("/")
def index():
    df = read_data().reset_index(names="_idx")
    open_, closed = render_lists(df)

    # Dashboard-Daten sammeln
    all_df = pd.concat([open_, closed], ignore_index=True)

    # ---- alle NaN in feedbackType zu "Unbekannt" ----
    all_df["feedbackType"] = all_df["feedbackType"].fillna("Unbekannt")
    # ------------------------------------------------------------------------------

    records = all_df.to_dict("records")

    # 1) Status-Verteilung
    status_counts = Counter(r["status"] for r in records)

    # 2) Feedback-Type-Verteilung (nun ohne doppeltes NaN)
    type_counts   = Counter(r["feedbackType"] for r in records)

    # 3) Zeitreihe: Anzahl Feedbacks pro Tag
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
        "status": {"labels": list(status_counts.keys()), "counts": list(status_counts.values())},
        "type":   {"labels": list(type_counts.keys()),   "counts": list(type_counts.values())},
        "time":   {"labels": time_labels,                "counts": time_counts}
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
        row = df.loc[idx]
    except KeyError:
        flash("Datensatz nicht gefunden.", "danger")
        return redirect(url_for("index"))
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
    measures = request.form.get("measuresTaken", "").strip()

    if measures == "":
        flash("Bitte geben Sie getroffene Massnahmen ein.", "warning")
        return redirect(url_for("detail", idx=idx))

    df = read_data()
    df.at[idx, "measuresTaken"] = measures
    write_data(df)
    flash("Massnahmen gespeichert.", "success")
    return redirect(url_for("detail", idx=idx))

@app.post("/complete_feedback/<int:idx>")
def complete_feedback(idx):
    measures = request.form.get("measures", "").strip()
    df = read_data()
    status = str(df.at[idx, "status"]).lower()

    if status != "review-board":
        flash("Das Feedback muss im Status 'Review-Board' sein, bevor es abgeschlossen werden kann.", "warning")
        return redirect(url_for("detail", idx=idx))

    if not measures:
        flash("Dokumentieren Sie Massnahmen, um das Feedback abzuschliessen.", "warning")
        return redirect(url_for("detail", idx=idx))

    df.at[idx, "measuresTaken"] = measures
    df.at[idx, "status"] = "closed"
    write_data(df)
    flash("Feedback abgeschlossen.", "success")
    return redirect(url_for("index"))

# ---------- Start app ------------------------------------------------------
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    # Browser automatisch öffnen
    threading.Timer(1.0, open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=False)

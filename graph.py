"""
BMI Trend Visualization Module
==============================
This module utilizes matplotlib to generate an interactive, visual line graph
tracking a user's Body Mass Index (BMI) over time.

Features:
- Line chart with visible data markers
- Standard health category color reference bands (Underweight, Normal, Overweight, Obese)
- Custom gridlines, axis labels, titles, and legends
- Handles missing or insufficient user records gracefully with error popups
"""

import tkinter.messagebox as msgbox
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

from database import get_user_history, DEFAULT_DB_PATH


def plot_bmi_trend(username: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Retrieves all historical BMI records for a specific user and displays a line plot
    visualizing the BMI progression over time.

    Args:
        username (str): The name of the user whose trend graph will be plotted.
        db_path (str): File path to the SQLite database.

    Returns:
        bool: True if plot was successfully generated and shown, False if failed/no data.
    """
    clean_username = username.strip()
    if not clean_username:
        msgbox.showwarning("Input Required", "Please enter or select a user name to view the BMI trend graph.")
        return False

    # Retrieve database records
    try:
        records: List[Dict[str, Any]] = get_user_history(clean_username, db_path=db_path)
    except Exception as e:
        msgbox.showerror("Database Error", f"Unable to fetch history for '{clean_username}':\n{str(e)}")
        return False

    if not records:
        msgbox.showinfo(
            "No Records Found",
            f"No BMI records found for user '{clean_username}'.\n\n"
            "Please calculate and save at least one BMI entry first!"
        )
        return False

    # Extract dates and BMI values
    dates = []
    bmi_values = []

    for r in records:
        try:
            # Parse timestamp string into datetime object
            dt = datetime.strptime(r["date"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # Fallback parsing if date format varies
            dt = datetime.strptime(r["date"].split(".")[0], "%Y-%m-%d %H:%M:%S")
        dates.append(dt)
        bmi_values.append(r["bmi"])

    # Configure matplotlib figure style
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, ax = plt.subplots(figsize=(9, 5.5))
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#FFFFFF')

    # Plot the user's BMI trend line
    ax.plot(
        dates,
        bmi_values,
        marker='o',
        linewidth=2.5,
        markersize=7,
        color='#2563EB',
        label=f"{clean_username}'s BMI",
        zorder=4
    )

    # Annotate points with numerical BMI values
    for d, b in zip(dates, bmi_values):
        ax.annotate(
            f"{b:.1f}",
            (d, b),
            textcoords="offset points",
            xytext=(0, 8),
            ha='center',
            fontsize=9,
            fontweight='bold',
            color='#1E293B'
        )

    # Draw WHO Category Reference Threshold Lines
    ax.axhline(y=18.5, color='#3B82F6', linestyle='--', linewidth=1.2, alpha=0.7, label='Underweight Threshold (18.5)')
    ax.axhline(y=25.0, color='#F59E0B', linestyle='--', linewidth=1.2, alpha=0.7, label='Overweight Threshold (25.0)')
    ax.axhline(y=30.0, color='#EF4444', linestyle='--', linewidth=1.2, alpha=0.7, label='Obese Threshold (30.0)')

    # Add colored background bands for categories
    min_y = min(min(bmi_values) - 2.0, 15.0)
    max_y = max(max(bmi_values) + 3.0, 35.0)

    ax.axhspan(min_y, 18.5, color='#DBEAFE', alpha=0.3, label='Underweight Zone')
    ax.axhspan(18.5, 24.9, color='#DCFCE7', alpha=0.3, label='Normal Weight Zone')
    ax.axhspan(25.0, 29.9, color='#FEF3C7', alpha=0.3, label='Overweight Zone')
    ax.axhspan(29.9, max_y, color='#FEE2E2', alpha=0.3, label='Obese Zone')

    # Chart formatting
    ax.set_title(f"BMI Progress & Trend Analysis for '{clean_username}'", fontsize=13, fontweight='bold', pad=15, color='#0F172A')
    ax.set_xlabel("Date & Time of Entry", fontsize=11, fontweight='bold', labelpad=10, color='#334155')
    ax.set_ylabel("Body Mass Index (BMI)", fontsize=11, fontweight='bold', labelpad=10, color='#334155')

    # Date formatting on X-axis
    if len(dates) > 1 and (dates[-1] - dates[0]).days > 2:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d, %H:%M'))
    else:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S\n%d %b'))

    fig.autofmt_xdate(rotation=30, ha='right')

    ax.set_ylim(min_y, max_y)
    ax.grid(True, linestyle=':', alpha=0.6, color='#94A3B8')

    # Legend positioning
    handles, labels = ax.get_legend_handles_labels()
    # Deduplicate legend items while maintaining order
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper left', bbox_to_anchor=(1.01, 1), borderaxespad=0, fontsize=9)

    plt.tight_layout()

    # Show figure plot window
    plt.show()
    return True

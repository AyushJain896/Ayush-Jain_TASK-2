"""
BMI Trend Visualization Module
==============================
This module utilizes matplotlib to generate interactive visual line graphs
tracking Body Mass Index (BMI) over time for individual users or comparing
multiple users together on the same chart.

Features:
- Single-user line chart with date timestamps
- Multi-user comparative line chart (Overlapped Step-by-Step Entry Index: Entry 1, Entry 2, Entry 3...)
- Standard health category color reference bands (Underweight, Normal, Overweight, Obese)
- Custom gridlines, axis labels, titles, and legends
- Handles missing or insufficient user records gracefully with dialog alerts
"""

import tkinter.messagebox as msgbox
from typing import List, Dict, Any
import matplotlib.pyplot as plt
from datetime import datetime

from database import get_user_history, DEFAULT_DB_PATH

# Vibrant color palette for multi-user comparison lines
USER_COLORS = [
    '#2563EB',  # Royal Blue
    '#16A34A',  # Emerald Green
    '#EA580C',  # Orange
    '#9333EA',  # Purple
    '#0284C7',  # Sky Blue
    '#DC2626',  # Crimson Red
    '#059669',  # Teal Green
    '#D97706',  # Amber
]


def plot_bmi_trend(username: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Retrieves all historical BMI records for a single user and displays a line plot
    visualizing the BMI progression over time using date timestamps.
    """
    clean_username = username.strip()
    if not clean_username:
        msgbox.showwarning("Input Required", "Please enter or select a user name to view the BMI trend graph.")
        return False

    try:
        records = get_user_history(clean_username, db_path=db_path)
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

    dates = []
    bmi_values = []
    for r in records:
        try:
            dt = datetime.strptime(r["date"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = datetime.strptime(r["date"].split(".")[0], "%Y-%m-%d %H:%M:%S")
        dates.append(dt)
        bmi_values.append(r["bmi"])

    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, ax = plt.subplots(figsize=(9, 5.5))
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#FFFFFF')

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

    ax.axhline(y=18.5, color='#3B82F6', linestyle='--', linewidth=1.2, alpha=0.7, label='Underweight (18.5)')
    ax.axhline(y=25.0, color='#F59E0B', linestyle='--', linewidth=1.2, alpha=0.7, label='Overweight (25.0)')
    ax.axhline(y=30.0, color='#EF4444', linestyle='--', linewidth=1.2, alpha=0.7, label='Obese (30.0)')

    min_y = min(min(bmi_values) - 2.0, 15.0)
    max_y = max(max(bmi_values) + 3.0, 35.0)

    ax.axhspan(min_y, 18.5, color='#DBEAFE', alpha=0.3)
    ax.axhspan(18.5, 24.9, color='#DCFCE7', alpha=0.3)
    ax.axhspan(25.0, 29.9, color='#FEF3C7', alpha=0.3)
    ax.axhspan(29.9, max_y, color='#FEE2E2', alpha=0.3)

    ax.set_title(f"BMI Progress & Trend Analysis for '{clean_username}'", fontsize=13, fontweight='bold', pad=15, color='#0F172A')
    ax.set_xlabel("Date & Time of Entry", fontsize=11, fontweight='bold', labelpad=10, color='#334155')
    ax.set_ylabel("Body Mass Index (BMI)", fontsize=11, fontweight='bold', labelpad=10, color='#334155')

    fig.autofmt_xdate(rotation=30, ha='right')
    ax.set_ylim(min_y, max_y)
    ax.grid(True, linestyle=':', alpha=0.6, color='#94A3B8')

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper left', bbox_to_anchor=(1.01, 1), borderaxespad=0, fontsize=9)

    plt.tight_layout()
    plt.show()
    return True


def plot_multi_user_bmi_trend(usernames: List[str], db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Retrieves historical BMI records for multiple users and displays their BMI trends
    OVERLAPPED step-by-step (User 1's 1st entry aligned with User 2's 1st entry, 2nd with 2nd, etc.).

    Args:
        usernames (List[str]): List of usernames to compare.
        db_path (str): File path to the SQLite database.

    Returns:
        bool: True if plot was successfully generated, False otherwise.
    """
    clean_usernames = [u.strip() for u in usernames if u.strip()]
    if not clean_usernames:
        msgbox.showwarning("Input Required", "Please select at least one user name to view the BMI graph.")
        return False

    user_data_map = {}
    all_bmi_values = []
    max_entries = 0

    # Retrieve database records for each user
    for username in clean_usernames:
        try:
            records = get_user_history(username, db_path=db_path)
            if records:
                bmis = [r["bmi"] for r in records]
                user_data_map[username] = bmis
                all_bmi_values.extend(bmis)
                if len(bmis) > max_entries:
                    max_entries = len(bmis)
        except Exception as e:
            print(f"[Graph Error] Failed to fetch history for '{username}': {e}")

    if not user_data_map:
        msgbox.showinfo(
            "No Records Found",
            f"No historical BMI records found for the selected user(s): {', '.join(clean_usernames)}.\n\n"
            "Please calculate and save at least one BMI entry first!"
        )
        return False

    # Configure matplotlib figure style
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#FFFFFF')

    # Plot each user's trend line starting from Entry 1
    for idx, (user, bmis) in enumerate(user_data_map.items()):
        color = USER_COLORS[idx % len(USER_COLORS)]
        # Entry numbers: 1, 2, 3, 4 ...
        x_indices = list(range(1, len(bmis) + 1))

        ax.plot(
            x_indices,
            bmis,
            marker='o',
            linewidth=2.5,
            markersize=7,
            color=color,
            label=f"{user}",
            zorder=4
        )

        # Annotate points with numerical BMI values
        for x, b in zip(x_indices, bmis):
            ax.annotate(
                f"{b:.1f}",
                (x, b),
                textcoords="offset points",
                xytext=(0, 7),
                ha='center',
                fontsize=8.5,
                fontweight='bold',
                color=color
            )

    # Draw WHO Category Reference Threshold Lines
    ax.axhline(y=18.5, color='#3B82F6', linestyle='--', linewidth=1.2, alpha=0.7, label='Underweight (18.5)')
    ax.axhline(y=25.0, color='#F59E0B', linestyle='--', linewidth=1.2, alpha=0.7, label='Overweight (25.0)')
    ax.axhline(y=30.0, color='#EF4444', linestyle='--', linewidth=1.2, alpha=0.7, label='Obese (30.0)')

    # Add colored background bands for categories
    min_y = min(min(all_bmi_values) - 2.0, 15.0)
    max_y = max(max(all_bmi_values) + 3.0, 35.0)

    ax.axhspan(min_y, 18.5, color='#DBEAFE', alpha=0.25)
    ax.axhspan(18.5, 24.9, color='#DCFCE7', alpha=0.25)
    ax.axhspan(25.0, 29.9, color='#FEF3C7', alpha=0.25)
    ax.axhspan(29.9, max_y, color='#FEE2E2', alpha=0.25)

    # Chart Title and Formatting
    if len(user_data_map) == 1:
        title_text = f"BMI Progress Trend for '{list(user_data_map.keys())[0]}'"
    else:
        title_text = f"Overlapped BMI Progress Comparison: {' vs '.join(user_data_map.keys())}"

    ax.set_title(title_text, fontsize=13, fontweight='bold', pad=15, color='#0F172A')
    ax.set_xlabel("Measurement Entry Number (Entry #1, #2, #3...)", fontsize=11, fontweight='bold', labelpad=10, color='#334155')
    ax.set_ylabel("Body Mass Index (BMI)", fontsize=11, fontweight='bold', labelpad=10, color='#334155')

    # Set X ticks as Entry #1, Entry #2, etc.
    entry_ticks = list(range(1, max_entries + 1))
    ax.set_xticks(entry_ticks)
    ax.set_xticklabels([f"Entry #{i}" for i in entry_ticks])

    ax.set_ylim(min_y, max_y)
    ax.grid(True, linestyle=':', alpha=0.6, color='#94A3B8')

    # Legend positioning
    ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1), borderaxespad=0, fontsize=9.5)

    plt.tight_layout()
    plt.show()
    return True

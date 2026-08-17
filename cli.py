"""
BMI Calculator & Health Tracker - Command Line Interface (CLI)
===============================================================
A pure Python interactive command-line interface for calculating Body Mass Index,
classifying health categories, storing records in SQLite, viewing user history,
and generating multi-user comparison trend charts.
"""

import sys
from bmi import calculate_bmi, get_bmi_category, validate_inputs
from database import (
    init_db,
    save_record,
    get_user_history,
    get_all_users,
    delete_record,
    clear_user_history,
    DEFAULT_DB_PATH
)
from graph import plot_bmi_trend, plot_multi_user_bmi_trend


def print_banner():
    """Prints application header banner."""
    print("=" * 60)
    print("      ⚖️  BMI CALCULATOR & HEALTH TRACKER - CLI MODE  ⚖️")
    print("=" * 60)


def menu_calculate_and_save():
    """Handles interactive CLI input for BMI calculation and saving."""
    print("\n--- 🧮 CALCULATE & SAVE BMI ---")
    username = input("Enter User Name: ").strip()
    weight_str = input("Enter Weight (kg): ").strip()
    height_str = input("Enter Height (m): ").strip()

    is_valid, error_msg, clean_username, weight, height = validate_inputs(
        username, weight_str, height_str
    )

    if not is_valid:
        print(f"\n❌ Input Error: {error_msg}")
        return

    bmi = calculate_bmi(weight, height)
    cat_info = get_bmi_category(bmi)

    print("\n" + "-" * 40)
    print(f" User Name:  {clean_username}")
    print(f" Weight:     {weight:.1f} kg")
    print(f" Height:     {height:.2f} m")
    print(f" BMI Value:  {bmi:.2f}")
    print(f" Category:   {cat_info['category'].upper()}")
    print(f" Advice:     {cat_info['message']}")
    print("-" * 40)

    save_choice = input("\nDo you want to save this record to database? (y/n): ").strip().lower()
    if save_choice in ['y', 'yes']:
        try:
            row_id = save_record(
                username=clean_username,
                weight=weight,
                height=height,
                bmi=bmi,
                category=cat_info['category'],
                db_path=DEFAULT_DB_PATH
            )
            print(f"✅ Successfully saved record ID #{row_id} for user '{clean_username}'.")
        except Exception as e:
            print(f"❌ Failed to save record: {e}")


def menu_view_history():
    """Displays user history table in CLI."""
    print("\n--- 📜 VIEW USER HISTORY ---")
    users = get_all_users(DEFAULT_DB_PATH)
    if users:
        print("Existing Users:", ", ".join(users))

    username = input("Enter User Name to view history: ").strip()
    if not username:
        print("❌ Username cannot be empty.")
        return

    try:
        records = get_user_history(username, db_path=DEFAULT_DB_PATH)
        if not records:
            print(f"\nℹ️  No records found for user '{username}'.")
            return

        print(f"\nHistorical Records for '{username}':")
        print("-" * 68)
        print(f"{'ID':<6} | {'Date & Time':<20} | {'Weight':<8} | {'Height':<8} | {'BMI':<6} | {'Category':<12}")
        print("-" * 68)

        for r in records:
            print(f"{r['id']:<6} | {r['date']:<20} | {r['weight']:<8.1f} | {r['height']:<8.2f} | {r['bmi']:<6.2f} | {r['category']:<12}")

        print("-" * 68)
    except Exception as e:
        print(f"❌ Failed to retrieve history: {e}")


def menu_compare_users_graph():
    """Interactive prompt to pick multiple users and launch comparison chart."""
    print("\n--- 👥 MULTI-USER COMPARISON GRAPH ---")
    users = get_all_users(DEFAULT_DB_PATH)
    if not users:
        print("ℹ️  No users found in database yet.")
        return

    print("Available Users:", ", ".join(users))
    user_input = input("Enter usernames to compare separated by commas (e.g. Alice, Bob, Charlie): ").strip()
    if not user_input:
        print("❌ No usernames entered.")
        return

    selected = [u.strip() for u in user_input.split(",") if u.strip()]
    plot_multi_user_bmi_trend(selected, db_path=DEFAULT_DB_PATH)


def menu_delete_record():
    """Deletes a specific record by ID."""
    print("\n--- 🗑️ DELETE RECORD ---")
    record_id_str = input("Enter Record ID to delete: ").strip()
    try:
        record_id = int(record_id_str)
        if delete_record(record_id, db_path=DEFAULT_DB_PATH):
            print(f"✅ Successfully deleted record ID #{record_id}.")
        else:
            print(f"❌ Record ID #{record_id} not found.")
    except ValueError:
        print("❌ Invalid Record ID. Please enter a valid integer.")
    except Exception as e:
        print(f"❌ Error deleting record: {e}")


def menu_clear_user():
    """Clears all records for a user."""
    print("\n--- ⚠️ CLEAR ALL USER RECORDS ---")
    username = input("Enter User Name whose records should be deleted: ").strip()
    if not username:
        print("❌ Username cannot be empty.")
        return

    confirm = input(f"Are you sure you want to delete ALL records for '{username}'? (y/n): ").strip().lower()
    if confirm in ['y', 'yes']:
        try:
            count = clear_user_history(username, db_path=DEFAULT_DB_PATH)
            print(f"✅ Deleted {count} record(s) for user '{username}'.")
        except Exception as e:
            print(f"❌ Error clearing user history: {e}")


def main():
    """CLI Loop Entry Point."""
    init_db(DEFAULT_DB_PATH)
    print_banner()

    while True:
        print("\nSelect an Option:")
        print(" 1. Calculate & Save BMI")
        print(" 2. View User History")
        print(" 3. Compare Multi-User BMI Trends Graph (2, 3, or more people)")
        print(" 4. Delete Specific Record")
        print(" 5. Clear All Records for a User")
        print(" 6. Exit")

        choice = input("\nEnter choice (1-6): ").strip()

        if choice == '1':
            menu_calculate_and_save()
        elif choice == '2':
            menu_view_history()
        elif choice == '3':
            menu_compare_users_graph()
        elif choice == '4':
            menu_delete_record()
        elif choice == '5':
            menu_clear_user()
        elif choice == '6':
            print("\nThank you for using BMI Calculator & Health Tracker! Goodbye. 👋")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please select 1-6.")


if __name__ == "__main__":
    main()

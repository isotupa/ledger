import os
import sys
import csv
import argparse
from datetime import datetime
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# --- Configuration & Constants ---
DATA_DIR = Path("expenses")
CONFIG_FILE = Path("settings.conf")
DATE_FMT = "%d-%m-%Y"

# ANSI Colors for Terminal (works in most modern terminals)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# --- Visualization Helper ---
class TerminalUI:
    @staticmethod
    def print_header():
        art = f"""
{Colors.BLUE}╔════════════════════════════════════════════════════════════╗
║             {Colors.BOLD}TERMINAL EXPENSE MANAGER v2.0{Colors.ENDC}{Colors.BLUE}                  ║
╚════════════════════════════════════════════════════════════╝{Colors.ENDC}
        """
        print(art)

    @staticmethod
    def print_bar_chart(data: Dict[str, float], title: str):
        if not data:
            print(f"{Colors.WARNING}No data to plot.{Colors.ENDC}")
            return

        print(f"\n{Colors.BOLD}--- {title} ---{Colors.ENDC}")
        max_val = max(data.values()) if data.values() else 1
        max_width = 50  # Character width of the longest bar

        # Sort by value descending
        sorted_data = sorted(data.items(), key=lambda item: item[1], reverse=True)

        for label, value in sorted_data:
            bar_len = int((abs(value) / max_val) * max_width)
            # Choose color based on expense (red) or profit (green)
            color = Colors.GREEN if value > 0 else Colors.FAIL
            char = "█" 
            
            bar = f"{color}{char * bar_len}{Colors.ENDC}"
            print(f"{label:>15} | {bar} {value:.2f}")
        print("")

    @staticmethod
    def print_table(headers: List[str], rows: List[List[str]]):
        # Calculate column widths
        widths = [len(h) for h in headers]
        for row in rows:
            for i, val in enumerate(row):
                widths[i] = max(widths[i], len(str(val)))
        
        # Add padding
        widths = [w + 2 for w in widths]
        
        # Create format string
        fmt = "".join([f"{{:<{w}}}" for w in widths])
        
        print(Colors.BOLD + fmt.format(*headers) + Colors.ENDC)
        print("-" * sum(widths))
        for row in rows:
            print(fmt.format(*[str(r) for r in row]))
        print("-" * sum(widths))

# --- Core Logic ---
class ExpenseTracker:
    def __init__(self):
        self.categories = self._load_config()
        DATA_DIR.mkdir(exist_ok=True)

    def _load_config(self) -> Dict[str, List[str]]:
        cats = {}
        if not CONFIG_FILE.exists():
            # Create default if missing
            default_conf = "Food:Groceries,Dining Out\nTransport:Fuel,Public,Car"
            with open(CONFIG_FILE, 'w') as f:
                f.write(default_conf)
            print(f"{Colors.WARNING}Created default settings.conf{Colors.ENDC}")
        
        with open(CONFIG_FILE, 'r') as f:
            for line in f:
                if ':' in line:
                    key, val = line.strip().split(':')
                    cats[key] = val.split(',')
        return cats

    def get_file_path(self, year: int, month: int) -> Path:
        return DATA_DIR / f"{month}_{year}.csv"

    def add_expense(self, year: int, month: int):
        print(f"{Colors.HEADER}Interactive Mode: {month}/{year}{Colors.ENDC}")
        
        try:
            day = input("Day (DD): ")
            # Validate date
            full_date_str = f"{day}-{month}-{year}"
            datetime.strptime(full_date_str, DATE_FMT) # Raises error if invalid
            
            title = input("Title: ")
            
            # Category Selection
            print("\nCategories:")
            cat_keys = list(self.categories.keys())
            for i, k in enumerate(cat_keys):
                print(f"{i}: {k}")
            cat_idx = int(input("Select Category ID: "))
            selected_cat = cat_keys[cat_idx]

            # Sub-category Selection
            print(f"\nSub-types for {selected_cat}:")
            subs = self.categories[selected_cat]
            for i, s in enumerate(subs):
                print(f"{i}: {s}")
            sub_idx = int(input("Select Sub-type ID: "))
            selected_sub = subs[sub_idx]

            details = input("Details (optional): ") or "NA"
            
            is_profit = input("Is this Income? (y/N): ").lower() == 'y'
            amount_str = input("Amount: ")
            amount = float(amount_str)
            if not is_profit:
                amount = -abs(amount) # Expenses are negative internally
            
            # Write
            fpath = self.get_file_path(year, month)
            file_exists = fpath.exists()
            
            with open(fpath, 'a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Date", "Title", "Type", "Subtype", "Details", "Amount"])
                writer.writerow([full_date_str, title, selected_cat, selected_sub, details, amount])
            
            print(f"{Colors.GREEN}Entry Saved!{Colors.ENDC}")

        except ValueError as e:
            print(f"{Colors.FAIL}Input Error: {e}{Colors.ENDC}")
        except IndexError:
            print(f"{Colors.FAIL}Invalid selection.{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}Error: {e}{Colors.ENDC}")

    def load_expenses(self, year: int, month: Optional[int] = None) -> List[dict]:
        expenses = []
        months_to_load = [month] if month else range(1, 13)
        
        for m in months_to_load:
            path = self.get_file_path(year, m)
            if path.exists():
                with open(path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Clean up formatting
                        try:
                            row['Amount'] = float(row['Amount'])
                            expenses.append(row)
                        except ValueError:
                            continue # Skip bad rows
        return expenses

    def view_report(self, year: int, month: int = None, by_type: str = None):
        data = self.load_expenses(year, month)
        if not data:
            print(f"{Colors.WARNING}No records found for specified date.{Colors.ENDC}")
            return

        total = sum(d['Amount'] for d in data)
        
        # 1. Table View
        headers = ["Date", "Title", "Type", "Subtype", "Amount"]
        rows = [[d['Date'], d['Title'], d['Type'], d['Subtype'], f"{d['Amount']:.2f}"] 
                for d in data if (not by_type or d['Type'] == by_type)]
        
        TerminalUI.print_table(headers, rows)
        
        # 2. Aggregation for Plotting
        type_totals = defaultdict(float)
        for d in data:
            # If filtering by type, plot subtypes. If global, plot main types
            key = d['Subtype'] if by_type else d['Type']
            if by_type and d['Type'] != by_type:
                continue
            type_totals[key] += d['Amount']

        # 3. Plot
        plot_title = f"Expenses by {'Subtype' if by_type else 'Type'}"
        TerminalUI.print_bar_chart(type_totals, plot_title)

        print(f"\n{Colors.BOLD}Total Net: {total:.2f}{Colors.ENDC}")


# --- Main Execution ---
def main():
    TerminalUI.print_header()
    tracker = ExpenseTracker()

    # Professional Argument Parsing
    parser = argparse.ArgumentParser(description="CLI Expense Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: Add
    add_parser = subparsers.add_parser("add", help="Add a new expense")
    add_parser.add_argument("-y", "--year", type=int, default=datetime.now().year)
    add_parser.add_argument("-m", "--month", type=int, default=datetime.now().month)

    # Command: View
    view_parser = subparsers.add_parser("view", help="View expenses and charts")
    view_parser.add_argument("-y", "--year", type=int, required=True, help="Year to view")
    view_parser.add_argument("-m", "--month", type=int, help="Specific month (1-12)")
    view_parser.add_argument("-t", "--type", type=str, help="Filter by specific Type (e.g. Food)")

    args = parser.parse_args()

    if args.command == "add":
        try:
            while True:
                tracker.add_expense(args.year, args.month)
                if input("Add another? (Y/n): ").lower() == 'n':
                    break
        except KeyboardInterrupt:
            print("\nExiting...")

    elif args.command == "view":
        tracker.view_report(args.year, args.month, args.type)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
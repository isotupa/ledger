import os
import sys
import csv

types = {}

def load_conf_file(path="settings.conf"):
    with open(path) as fp:
        for line in fp:
            full = line.split(":")
            type = full[0]
            subtypes = full[1].split(",")
            subtypes[-1] = subtypes[-1].replace("\n","")
            types[type] = subtypes
            
def create_expense(path="expenses/01_2016.csv", date="00-00", title="NA", ttype="NA", subtype="NA", details="NA", amount="NA"):
    try:
        with open(path, "a", newline="") as fp:
            spamwriter = csv.writer(fp, delimiter=',')
            spamwriter.writerow([date, title, ttype, subtype, details, amount])
    except:
        raise Exception("File does not exist")

def print_help(arg):
        print(f'''Usage: {arg} OPTIONS -y YEAR -m MONTH
              Options:
              -i              Interactive mode to add expenses
              -v VIEW_OPTION   View expenses
                VIEW_OPTION:
                1: View expenses by month
                2: View expenses by year
                3: View expenses by type
              -y YEAR     Specify the year (e.g., 2026)
              -m MONTH    Specify the month (1-12)''')

def view_expenses_by_month(year, month):
    path = f"expenses/{month}_{year}.csv"
    try:
        with open(path, "r") as fp:
            spamreader = csv.reader(fp, delimiter=',')
            total_expenses = 0
            for row in spamreader:
                print(', '.join(row))
                if row[5] != "Amount":
                    total_expenses += float(row[5])
            print("Total Expenses: ", total_expenses)
    except:
        raise Exception("File does not exist")

def view_expenses_by_year(year):
    total_expenses = 0
    for month in range(1, 13):
        path = f"expenses/{month}_{year}.csv"
        try:
            with open(path, "r") as fp:
                spamreader = csv.reader(fp, delimiter=',')
                for row in spamreader:
                    if row[5] != "Amount":
                        total_expenses += float(row[5])
        except:
            continue
    print("Total Expenses for year ", year, ": ", total_expenses)

def view_expenses_by_type(year, ttype):
    total_expenses = 0
    for month in range(1, 13):
        path = f"expenses/{month}_{year}.csv"
        try:
            with open(path, "r") as fp:
                spamreader = csv.reader(fp, delimiter=',')
                for row in spamreader:
                    if row[2] == ttype and row[5] != "Amount":
                        total_expenses += float(row[5])
        except:
            continue
    print(f"Total Expenses for type {ttype} in year {year}: ", total_expenses)

def interactive_program(month, year):
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    print("Interactive Expense Entry (press Ctrl+C to exit at any time)")
    print(f"Enter the day of the expense in {months[int(month)-1]} (DD): ")
    day = input()
    print("Enter the title of the expense: ")
    title = input()
    print("Select the type of expense from the following list: ")
    for i, t in enumerate(types.keys()):
        print(f"{i}: {t}")
    type_index = int(input())
    ttype = list(types.keys())[type_index]
    print(f"Select the subtype of {ttype} from the following list: ")
    for i, st in enumerate(types[ttype]):
        print(f"{i}: {st}")
    subtype_index = int(input())
    subtype = types[ttype][subtype_index]
    print("Enter additional details (or NA): ")
    details = input()
    print("Expense(0) or Profit(1): (Default:0) ")
    answer = input()
    sign = -1
    if answer == "1":
        sign = 1
    print("Enter the amount: ")
    amount = float(input()) * sign
    date = f"{day}-{month}-{year}"
    return date, title, ttype, subtype, details, amount

# ledger -i -y 2026 -m 1
def main():
    args = sys.argv
    if args[1] == "-i":
        if args[2] != "-y":
            print_help(args[0])
        else:
            year = int(args[3])
            month = int(args[5])
            if month < 1 or month > 12:
                print("Month must be between 1 and 12")
                return
            path = f"expenses/{month}_{year}.csv"
            if not os.path.exists("expenses"):
                os.mkdir("expenses")
            if not os.path.exists(path):
                with open(path, "w", newline="") as fp:
                    spamwriter = csv.writer(fp, delimiter=',')
                    spamwriter.writerow(["Date", "Title", "Type", "Subtype", "Details", "Amount"])
            while True:
                date, title, ttype, subtype, details, amount = interactive_program(month, year)
                create_expense(path, date, title, ttype, subtype, details, amount)
    elif args[1] == "-v":
        view_option = args[2]
        if view_option == "1":
            if args[3] != "-y":
                print_help(args[0])
            else:
                year = int(args[4])
                month = int(args[6])
                if month < 1 or month > 12:
                    print("Month must be between 1 and 12")
                    return
                view_expenses_by_month(year, month)
        elif view_option == "2":
            if args[3] != "-y":
                print_help(args[0])
            else:
                year = int(args[4])
                view_expenses_by_year(year)
        elif view_option == "3":
            if args[3] != "-y":
                print_help(args[0])
            else:
                year = int(args[4])
                ttype = args[6]
                view_expenses_by_type(year, ttype)
        else:
            print_help(args[0])
    else:
        print_help(args[0])
    return

if __name__ == "__main__":
    load_conf_file()
    main()
"""
Symulator systemu bankowego
tworzenie konta z numerem karty zgodnym z algorytmem Luhna i losowym PINem
logowanie
sprawdzanie sumy na koncie
przelew
zamknięcie konta
"""
import math
import random
import sqlite3

conn = sqlite3.connect('card.s3db') # tworzenie bazy danych
cur = conn.cursor()

# accounts = {}
# try:
#     cur.execute(
#         f"""SELECT * FROM card; """
#     )
#
# except:
"""Tworzenie tabeli jeśli nie ma"""
cur.execute(
    """Create Table if not exists card (
    id INTEGER PRIMARY KEY,
    number TEXT,
    pin TEXT,
    balance INTEGER DEFAULT 0);"""
)
conn.commit()


def menu_start():
    answer = input('''1. Create an account
2. Log into account
0. Exit
''')
    if answer == "1":
        create_card()
    elif answer == "2":
        login()
    elif answer == "0":
        print("\nBye!")


def create_card():
    # global accounts
    inn = 400000    # numer banku
    can = random.random() # numer karty
    num = int(can * 1000000000) + inn * 1000000000
    card_num = checksum(num) + num * 10 # dodanie sumy kontrolnej
    pin = ""
    for d in range(4):
        pin += "".join(str(random.randint(0, 9)))
    # balance = 0
    print(f"""Your card has been created
Your card number:
{card_num}
Your card PIN:
{pin}
""")

    cur.execute(
        f"""INSERT INTO card (number, pin)
VALUES ({card_num}, {pin});"""
    )
    conn.commit()   # dodanie wpisu
    # accounts[card_num] = {"pin": pin, "balance": balance}
    menu_start()


def checksum(num):
    """Suma kontrolna wg algorytmu Luhna"""
    num = str(num)
    # print(num)
    num = [int(num[i]) * 2 if i % 2 == 0 else int(num[i]) for i in range(len(num))]
    # print(num)
    num = [d - 9 if d > 9 else d for d in num]
    # print(num)
    su = sum(num)
    # print(su)
    if su % 10 == 0:
        return 0
    else:
        # print(int((math.ceil(su/10,) * 10) - su))
        return int((math.ceil(su / 10, ) * 10) - su)


def login():
    # global accounts
    cnum = int(input("Enter your card number:\n"))
    # print(accounts[cnum])
    pnum = input("Enter your PIN:\n")
    cur.execute(f"""
    SELECT * FROM card WHERE pin = {pnum} AND number = {cnum};
    """)
    account = cur.fetchone()
    if account:
        print("\nYou have successfully logged in!\n")
        menu_account(cnum)
    else:
        print("\nWrong card number or PIN!\n")
        menu_start()
    # if cnum in accounts:
    #     if pnum == accounts[cnum]["pin"]:
    #         print("\nYou have successfully logged in!\n")
    #         menu_account(cnum)
    #     else:
    #         print("\nWrong card number or PIN!\n")
    #         menu_start()
    # else:
    #     print("\nWrong card number or PIN!\n")
    #     menu_start()


def menu_account(cnum):
    # global accounts
    answer = input("""1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
""")
    if answer == "1":
        """Balance"""
        # balance = accounts[cnum]["balance"]
        cur.execute(f"""
SELECT balance from accounts where number = {cnum};""")
        balance = cur.fetchone()
        print(f"\nBalance: {balance}\n")
        menu_account(cnum)
    elif answer == "2":
        """Add income"""
        income = int(input("Enter income:\n"))
        cur.execute(f"""
UPDATE card SET balance = balance + {income} WHERE number = {cnum}""")
        conn.commit()
        print("Income was added!\n")
        menu_account(cnum)
    elif answer == "3":
        """Do transfer"""
        card_num = int(input("Enter card number:\n"))
        if card_num == cnum:
            """Ten sam numer"""
            print("You can't transfer money to the same account!\n")
            menu_account(cnum)
        elif checksum(card_num // 10) != card_num % 10:
            """Zła suma kontrolna"""
            print("Probably you made a mistake in the card number. Please try again!\n")
            menu_account(cnum)
        else:
            cur.execute(f"""
    SELECT {card_num} FROM card where number = {card_num};""")
            exists = cur.fetchone()
            if not exists:
                """Nie ma numeru w bazie"""
                print("Such a card does not exist.\n")
                menu_account(cnum)
            else:
                money = int(input("Enter how much money you want to transfer:\n"))
                cur.execute(f"""
    SELECT balance FROM card where number = {cnum};""")
                balance = cur.fetchone()
                if money > int(balance[0]):
                    """Za mało kasy"""
                    print("Not enough money!\n")
                    menu_account(cnum)
                else:
                    cur.execute(f"""
UPDATE card SET balance = CASE WHEN number = {cnum} THEN balance - {money}
                                WHEN number = {card_num} THEN balance + {money}
                        END;""")
                    conn.commit()
                    print("Success!\n")
                    menu_account(cnum)
    elif answer == "4":
        """Close account"""
        cur.execute(f"""
Delete from card where number = {cnum};""")
        conn.commit()
        print("The account has been closed!\n")
        menu_start()
    elif answer == "5":
        """Log out"""
        print("\nYou have successfully logged out!\n")
        menu_start()
    elif answer == "0":
        """Exit"""
        print("\nBye!")


menu_start()

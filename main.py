from backups import restore_query
from configurations import config_query
from ts import ts_query


print("########## Welcome ##########")

options = {
    "1": "Take or restore a backup.",
    "2": "Configuration.",
    "3": "Troubleshooting.",
    "4": "Quit from the program."
}

def input_function():
    option = ""
    while option != "4":
        for key, value in options.items():
            print(key + ") " + value)
        option = input("Choose an option: ")
        if option == "1":
            restore_query()
        elif option == "2":
            config_query()
        elif option == "3":
            ts_query()
        elif option == "4":
            print("Exitting.")
            break
        else:
            print("Enter a correct option.")

input_function()

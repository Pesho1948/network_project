from inventory import devices
from netmiko import ConnectHandler
from backups import router_check

options = {
    "1" : "Configure interface.",
    "2" : "Configure OSPF.",
    "3" : "Configure ACL",
    "4" : "Quit from the configuration menu."
}
#Asks for hostname and test for correct name
def host_query():
    router_input = input("To which router should I connect (R1 - R4): ").upper()
    hostname = router_check(router_input)
    if isinstance(hostname, int):
        return hostname
    else:
        print("Wrong hostname\n")
        return host_query()

#Process id for OSPF config
def process_id():
    user_input = int(input("Choose a process id [1-65535]: "))
    if user_input >= 1 and user_input <= 65535:
        return user_input
    else:
        print("Make sure to enter a correct process id.\n")
        return process_id()

#OSPF configuration
def ospf_config():
    i = int(input("To how many routers to connect: "))
    while i > 0:
        router_input = host_query()
        connect = ConnectHandler(**devices[router_input])
        chosen_id = process_id()
        ipv4 = input("Enter a network: ")
        mask = input("Enter a wildcard mask: ")
        commands = [
            f"router ospf {chosen_id}",
            f"network {ipv4} {mask} area 0",
            "int fast0/0",
            f"ip ospf {chosen_id} area 0"
        ]
        output = connect.send_config_set(commands)
        print(output)
        i -= 1
        print("\n")

#Int config
def interface_config():
    router_input = host_query()
    connect = ConnectHandler(**devices[router_input])
    show_int = connect.send_command("show ip int brief | incl un")
    print(show_int)
    int_config = input("\nChoose an interface: ")
    if "/" in int_config:
        if int_config in show_int:
            ip_v4 = input("Enter an IPv4 address [A.B.C.D]: ")
            subnet_mask = input("Enter a subnet mask [A.B.C.D]: ")
            commands = ["interface " + int_config, "ip addr " + ip_v4 + " " + subnet_mask, "no shut"]
            output = connect.send_config_set(commands)
            verification = connect.send_command(f"sh ip int brief | sec {int_config}")
            print(verification)
            print("\n")
        else:
            print("Not in the list.\n")
            connect.disconnect()
            return interface_config()
    else:
        print("Enter the full name of the interface.\n")
        connect.disconnect()
        return interface_config()
    connect.disconnect()

def acl_config():
    router_input = host_query()
    connect = ConnectHandler(**devices[router_input])
    acl_number = int(input("Define an ACL number[1-99]: "))
    statements = int(input("How many ACL statements to define: "))
    commands = [f"ip access-list standard {acl_number}",] # list for permits/denies + network
    i = 1
    while statements > 0:
        permit_deny = input("Should I permit or deny traffic [permit, deny]: ")
        network_mask = input("Enter a network and wildcard mask [A.B.C.D A.B.C.D]: ")
        decision = permit_deny + " " + network_mask
        commands.append(decision)
        print(f"The access control entry is: {commands[i]}.\n")
        statements -= 1
        i += 1
    result = connect.send_config_set(commands)
    verification = connect.send_command(f"sh ip access-list {acl_number}")
    print(verification)
    print("\n")
    
def config_query():
    option = ""
    
    print("Configuration menu")
    while option != "4":
        for key, value in options.items():
            print(key + ") " + value)
        option = input("Choose an option: ")
        if option == "1":
            interface_config()
        elif option == "2":
            ospf_config()
        elif option == "3":     
            acl_config()
        elif option == "4":
            print("Exitting.")
            break
        else:
            print("Enter a correct option.\n")
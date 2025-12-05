import json
from datetime import datetime


def mask(value):
    if value.startswith("Счет"):

        return "Счет **" + value[-4:]
    elif " " in value:
        return value[:5] + " " + value[6:8] + "** **** " + value[-4:]
    return value

def display_last_5_operations(file_path):

    with open(file_path, 'r', encoding='utf-8') as f:
        operations = json.load(f)

    executed_operations = [op for op in operations if op['state'] == 'EXECUTED']

    executed_operations.sort(key=lambda op: datetime.strptime(op['date'], "%Y-%m-%dT%H:%M:%S.%f"), reverse=True)

    for op in executed_operations[:5]:
        date = datetime.strptime(op['date'], "%Y-%m-%dT%H:%M:%S.%f").strftime("%d.%m.%Y")
        description = op['description']
        amount = op['operationAmount']['amount']
        currency = op['operationAmount']['currency']['name']

        from_account = mask(op['from']) if 'from' in op else ""
        to_account = mask(op['to'])

        print(f"{date} {description}")
        print(f"{from_account} -> {to_account}")
        print(f"{amount} {currency}")
        print()

display_last_5_operations('operations.json')

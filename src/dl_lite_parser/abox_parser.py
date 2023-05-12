
# Example of the content of the file abox.txt
from dl_lite.abox import ABox
from dl_lite.assertion import assertion

def process_line(line):
    splitted = line.split(';')
    names = splitted[0].split('(')
    assertion_name = names[0]
    if ',' in names[1]:
        individuals = names[1].split(',')
        individual_1 = individuals[0]
        individual_2 = individuals[1].replace(")", "")
        return  assertion(assertion_name,individual_1,individual_2),splitted[1:]
    else:
        individual_1 = names[1].replace(")", "")
        return  assertion(assertion_name,individual_1),splitted[1:]



def read_abox(file_path: str):
    abox = ABox()
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip() == "BEGINABOX" or line.strip() == "ENDABOX":
                continue
            new_assertion,successors = process_line(line) 
            abox.add_assertion(new_assertion,successors)
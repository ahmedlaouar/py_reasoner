
import sys
"""
def check_circular(check_element, next__element, dataset, first_call=True):
    for successor in dataset[next__element]:
        if check_element in dataset[successor]:
            if first_call:
                continue
            else:
                return True,successor
        else:
            test, f_point = check_circular(check_element, successor, dataset, False)
            if test:
                return test,f_point 
    return False,-1
"""
def check_circular(check_element, dataset):
    stack = [(check_element, True)]
    while stack:
        current_element, first_call = stack.pop()
        for successor in dataset[current_element]:
            if check_element in dataset[successor]:
                if first_call:
                    continue
                else:
                    return True, successor
            else:
                stack.append((successor, False))
    return False, -1

def check_dataset(dataset):
    for check_element in dataset:
        test, f_point = check_circular(check_element, dataset)
        if test:
            return test,f_point,check_element

if __name__ == '__main__':  
    #sys.setrecursionlimit(5000)
    common_path = "benchmark_data/data/"
    dataset = {}
    # Read the dataset from the file
    with open(common_path+'dataset_small.txt', 'r') as file:
        lines = file.read().splitlines()

        for i in range(len(lines)):
            splitted = lines[i].split(";",maxsplit=-1)
            if splitted[1:] == [""] : splitted[1:] = []
            successors = [int(x) for x in splitted[1:-1]]
            dataset[i+1] = successors.copy()
            
    #for element in dataset:
    #    print(str(element)+" : ",dataset[element])
    print(check_dataset(dataset))
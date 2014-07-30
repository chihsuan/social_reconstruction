import csv

def read_csv(file_name):
    data = [] 
    with open(file_name, 'r') as input_file:
        data = csv.reader(input_file).next()

    return data

def write_csv(file_name, content):
    with open(file_name, 'w') as output_file:
        writer = csv.writer(output_file)  
        writer.writerows(content)  


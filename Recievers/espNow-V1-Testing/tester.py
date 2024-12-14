"""
Gets 8char strings and splits it by 2 into a list then extracts section based on tallyID
"""

tallyIDInt = 5

source = '12345678'
output = []

while source:
    output.append(source[:2])
    source = source[2:]
    
    
print(output[tallyIDInt-1])

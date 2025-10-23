import json

file_path = '/Users/graysonkeenan/Desktop/C.O.R.E/History.json'

# Read the file
with open(file_path, 'r') as f:
    data = json.load(f)


if 'history' not in data:
    data['history'] = [] 

data['history'].append('new_value')
print(data)
# Save it back to the file
with open(file_path, 'w') as f:
    json.dump(data, f, indent=2)

print("Appended to 'history' successfully!")

text ='jf'

prompt = text,data


print(prompt)
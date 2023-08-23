detectors = [
    "entryA",
    "bedroom",
    "aisleA",
    "studyroom",
    "BedroomC",
    "intersection",
    "aisleC",
    "aisleB",
    "kitchen",
    "meetingroom",
    "entryB",
    "BedroomB",
]

print("\"NORMAL\":{")
print("\t\"normal\": \"NORMAL\", ")
for detector in detectors:
    print(f"\t\"{detector}\": \"{detector}\", ")
print("\t\"reset\": \"NORMAL\"\n}, ")

for detector in detectors:
    print(f"\"{detector}\":""{")
    print(f"\t\"normal\": \"{detector}\", ")
    for i in detectors:
        print(f"\t\"{i}\": \"{detector}\", ")
    print("\t\"reset\": \"NORMAL\"\n}, ")

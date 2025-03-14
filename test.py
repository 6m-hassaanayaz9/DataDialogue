from security import safe_requests
 
URL = "http://127.0.0.1:12345/"
# question = "Which business has the best inspection score?"
# question = "What score does it have?"
# question = "Give me the names of 5 restaurants closest to it"
# question = "Give me the distance as well"
# question = "And what inspection scores do these restaurants have?"
questions = [
    "Which business has the best inspection score?",
    "What score does it have?",
    "Give me the names of 5 restaurants closest to it.",
    "Give me the distance as well.",
    "And what inspection scores do these restaurants have?"
]
for question in questions:
    PARAMS = {'auth':123,'question':question,'database':"SF"}
    

    r = safe_requests.get(url = URL, params = PARAMS,timeout=3600,verify = False)
    print(r.json())
    data = r.json()
    print(data)

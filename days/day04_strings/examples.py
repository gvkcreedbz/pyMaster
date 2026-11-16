"""Day 04 - Code along: cleaning a signup form."""

# ---- 1. Indexing and slicing ----
word = "PYTHON"
print(word[0], word[-1], word[1:4], word[::-1], len(word))

# ---- 2. Messy form input -> clean data ----
raw_name = "   aarav   SHARMA  "
raw_email = "  Aarav.Sharma@Gmail.COM "
name = " ".join(raw_name.split()).title()   # collapse spaces + Title Case
email = raw_email.strip().lower()
print(repr(name), repr(email))

# ---- 3. Splitting and joining ----
first, last = name.split()
print("First:", first, "| Last:", last)
username = f"{first}.{last}".lower()
print("Suggested username:", username)

# ---- 4. Searching ----
print("@ in email?", "@" in email, "| domain:", email.split("@")[1])
print(email.find("gmail"), email.count("a"), email.endswith(".com"))

# ---- 5. Hashtag from a caption ----
caption = "learning python is really fun!"
no_punct = caption.replace("!", "")
hashtag = "#" + "".join(no_punct.title().split())
print(hashtag)                     # #LearningPythonIsReallyFun

# ---- 6. Immutability ----
s = "Python"
new_s = "J" + s[1:]       # build a new string
print(s, new_s)

# ---- 7. Multi-line message with an f-string ----
otp = 4821
message = f"""Dear {first},
Your OTP is {otp}.
Do not share it with anyone."""
print(message)

from hashlib import sha1
from requests import get


def main():
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 {} PASSWORD".format(sys.argv[0]))

    pwned_count = password_pwned(sys.argv[1])

    if pwned_count == -1:
        print("Could not complete the request at this time. Possible internet connection issues.")
    else:
        print("Your password has appeared in the HIBP database {} times.".format(pwned_count))


def password_pwned(password):
    """Determine if the supplied plaintext password appears in the Have I been Pwned
    - Pwned Passwords databse, and if so how many time.

    @return int count - How many times the password has appeared in the database or -1 if the script failed to make the request.
    """

    pw_hash = str(sha1(password.encode()).hexdigest())

    url = "https://api.pwnedpasswords.com/range/" + pw_hash[:5]

    response = get(url)

    if response.status_code != 200:
        return -1

    for line in response.text.split("\r\n"):
        if pw_hash[5:].upper() in line:
            return int(line.split(":")[1])

    return 0


if __name__ == "__main__":
	main()

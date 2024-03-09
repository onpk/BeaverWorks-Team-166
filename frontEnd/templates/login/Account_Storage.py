import requests
from bs4 import BeautifulSoup

class UserAccount:
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
        self.preferences = {}

    @classmethod
    def from_html(cls, url):
        # Fetch HTML content from the website
        response = requests.get(url)
        html_content = response.text

        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract relevant information (replace 'class' and 'span')
        username = soup.find('span', {'class': 'username'}).text
        password = soup.find('span', {'class': 'password'}).text
        email = soup.find('span', {'class': 'email'}).text

        # Create an instance of the class with extracted data
        user_account = cls(username, password, email)

        # Extract and store user preferences (replace with actual HTML element and attribute names)
        user_account.preferences['theme'] = soup.find('span', {'class': 'theme'}).text
        user_account.preferences['language'] = soup.find('span', {'class': 'language'}).text

        return user_account

    def __str__(self):
        return f"Username: {self.username}\nPassword: {self.password}\nEmail: {self.email}\nPreferences: {self.preferences}"

# example usage
url = 'https://example.com/user_profile'
user_account = UserAccount.from_html(url)


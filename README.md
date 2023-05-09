# YouTubeAdStudy

### Setup

Download selenium
`pip install selenium`

Download a driver for chrome found here https://chromedriver.chromium.org/downloads. Make sure the driver matches your chrome version (check in Chrome Settings)

Put the directory containing this chrome driver that you just downloaded in the environment PATH variable.

(Optional)
You will also need a Google account. Change the username and password in the config file to your google acount. To setup the driver to launch using your account:
1. Open chrome
2. Log in to the account
3. Fully exit chrome
4. Copy the "User Data" folder found in your computers chrome directory, and paste it into the main folder for this repo 
5. Change the 'user_data' entry in the config file to the copied directory (works best if you delete the spaces from the "User Data" directory name

(Optional)
Create a file called `config.json` in the main folder of this repo that follows the format:
```
{
	"username": "johndoe123",
	"password": "password123",
	"user_data": "C:\\Users\\jdoe\\Documents\\ThisRepo\\UserData"
}
```
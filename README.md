# Setup Steps:
	1. Install python 3.7
	2. Clone the repository from web url (https://github.com/andrewnm9/api-testing-restful-booker.git)
	3. Open a command window and navigate to the api-testing-restful-booker folder
	4. Create a new virtual environment by running python3 -m venv ENV in the command window
	5. Activate the virtual environment from the command window by running ENV\Scripts\activate.bat
	6. Run pip install -r requirements.txt in the command window

<br />

# Adding Integration Tests:
	1. Open test_api_integration.py in a text editor
	2. Create a new test as a class method using pytest (https://doc.pytest.org/en/3.0.1/example/index.html) to one of the API test classes (TestAuthAPI, TestBrandingAPI, TestReportAPI, TestMessageAPI, TestRoomAPI, TestBookingAPI)

<br />

# Adding End to End Tests:
	1. Open test_api_end_to_end.py in a text editor
	2. Create a new test as a function, using the API test class methods as test steps

<br />

# Running Tests:
	1. Run tests by opening a command window, activating the virtual environment, navigate to the api-testing-restful-booker folder, and running pytest
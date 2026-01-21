# `clientcode/setup` Directory

This directory contains utility scripts for setting up and configuring the DeyeCloud API integration for the project. Its primary purpose is to streamline the authentication process by obtaining and managing API tokens.

## Contents

*   ### `setup_token.sh`

    This is a bash script designed to automate the process of obtaining an access token from the DeyeCloud API and configuring it within the project. It handles the following steps:
    1.  **Prompts for Credentials:** Asks the user to input their DeyeCloud API Email, Password, AppId, and AppSecret.
    2.  **Updates `obtain_token.py`:** Modifies the `clientcode/account/obtain_token.py` script with the provided credentials.
    3.  **Obtains Token:** Executes the `obtain_token.py` script to make an API call to DeyeCloud and retrieve an access token.
    4.  **Updates `variable.py`:** Inserts the newly obtained access token into `clientcode/variable.py`, making it available for other API-related scripts in the project.

## How to use `setup_token.sh`

To run the setup script, navigate to the project's root directory and execute the script:

```bash
bash clientcode/setup/setup_token.sh
```

Follow the prompts to enter your DeyeCloud API credentials. Upon successful execution, your API token will be configured in `clientcode/variable.py`.

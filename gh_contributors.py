#!/usr/bin/env python3

# Pre-requisites:
#   sudo apt install python3-pip -y
#   pip3 install requests matplotlib urllib3

# Run as: chmod +x ./gh_contributors.py && ./gh_contributors.py

###############################################################################################################
# Version  Author                  Comments
# 1.0      Madhavan Sridharan      Initial version to capture GH repo contributor and draw a pie chart.
###############################################################################################################

from datetime import datetime
from collections import Counter
import getpass
import os
import sys
import urllib.request
import json
import matplotlib.pyplot as plt
import subprocess

############################
##### GLOBAL CONSTANTS #####
############################
global GH_API_URL
GH_API_URL = 'https://api.github.com'
global GH_CLI_LATEST
GH_CLI_LATEST = 'https://github.com/cli/cli/releases/latest'
global GH_ORG
GH_ORG = None
global GH_REPO
GH_REPO = None
global GH_CLI_INSTALLED
GH_CLI_INSTALLED = False
global YEAR_DATE
YEAR_DATE = datetime.now().strftime("%Y%m%d")
global USER_CHART_BASED_ON
USER_CHART_BASED_ON = os.environ.get('USER_CHART_BASED_ON') if os.environ.get('USER_CHART_BASED_ON') else 'location'

#############################
##### UTILITY FUNCTIONS #####
#############################

def get_string_from_list(input_list: list, separator: str = ' ') -> str:
    """
    Convert a list to a string.
    """
    return separator.join(input_list)

def run_shell_command(command: list, inputs: str | None = None) -> any:
    """
    Run a shell command w/ the given inputs and return the output & stderr.
    """
    print(f'>>>>>>>>>>>>>>>>Begin run_shell_command command: [{get_string_from_list(command)}] with inputs: [{inputs}]')
    try:
        result = subprocess.run(command, input=inputs, shell=True, capture_output=True, text=True)

        # Parse the JSON output
        if result and result.returncode == 0:
            print(f"Request Succeeded. Returncode: {result.returncode}")
            return result
        else:
            print(f'Error Returncode: {result.returncode} and Error: {result.stderr}')
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None

def check_gh_cli_installed() -> None:
    """
    Check if the GitHub CLI is installed.
    """
    print('>>>>>>>>>>>>>>>>Begin check_gh_cli_installed')
    # Check if the GitHub CLI is installed
    global GH_CLI_INSTALLED
    while (not GH_CLI_INSTALLED):
        if os.system('gh --version') != 0:
            print("GitHub CLI is not installed. Please install it from https://cli.github.com/")

            # create a case block to check the OS and provide the appropriate installation instructions
            sys_platform = identify_sys_platform()
            if sys_platform.startswith('linux'):
                print("Please run the following commands to install the GitHub CLI:")
                print("\tsudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key C99B11DEB97541F0")
                print('\tsudo apt-add-repository https://cli.github.com/packages')
                print('\tsudo apt update')
                print('\tsudo apt install gh')
            elif sys_platform.startswith('darwin'):
                print("Please run the following command to install the GitHub CLI:")
                print("\tbrew install gh")
                print("Attempting to install...")
                print('Running "echo $HOMEBREW_NO_INSTALL_CLEANUP"')
                os.system('echo $HOMEBREW_NO_INSTALL_CLEANUP')
                result = run_shell_command(['brew install gh --quiet']) #, '--dry-run'
                if result:
                    if result.returncode == 0:
                        print("GitHub CLI installed successfully!")
                        GH_CLI_INSTALLED = True
                        return
                    elif result.stderr:
                        print(f'Attempt to install failed [{result.stderr}]. Please refer to above steps, install gh CLI and re-try the script again.')
                        exit(1)
            else:
                print(f"Please install the GitHub CLI from {GH_CLI_LATEST} appropriate for your OS [{sys_platform}] and re-run this program.")
            exit(1)
        else:
            GH_CLI_INSTALLED = True
    print('>>>>>>>>>>>>>>>>End check_gh_cli_installed')

def identify_sys_platform() -> str:
    """
    Identify the System Platform.
    Ref: https://docs.python.org/3/library/sys.html#sys.platform
    """
    print('>>>>>>>>>>>>>>>>Begin identify_sys_platform')
    # Identify the OS
    print(f'Detected system platform: {sys.platform}')
    print('>>>>>>>>>>>>>>>>End identify_sys_platform')
    return sys.platform

def get_contributors_data() -> None:
    """
    Get the contributors' data from the GitHub API.
    """
    print(f'>>>>>>>>>>>>>>>>Begin get_contributors_data - GH_ORG: {GH_ORG} - GH_REPO: {GH_REPO}')
    if GH_ORG is not None and len(GH_ORG) > 0 and GH_REPO is not None and len(GH_REPO) > 0:
        try:
            # --include is not required here to capture headers nor is --slurp to capture the output in a single JSON array
            result = run_shell_command([f'gh api --paginate --method GET -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28" /repos/{GH_ORG}/{GH_REPO}/contributors?anon=1&per_page=500&page=10'])
            if result and result.returncode == 0:
                print(f"Request to fetch GH contributors Succeeded. Returncode: {result.returncode}")
                print(f'Writing to [{CONTRIB_DATA_FILE}] file')
                with open(CONTRIB_DATA_FILE, 'w') as file:
                    file.write(result.stdout)
            else:
                print(f"Error: Unable to fetch contributor data from GitHub API & write to a file [{CONTRIB_DATA_FILE}].")
                exit(1)
        except Exception as e:
            print(f"Error: Unable to fetch data from GitHub API. Please check the GitHub Organization [{GH_ORG}] and Repository [{GH_REPO}] IDs. {e}")
            exit(1)
    else:
        print("Non-empty GitHub Organization and Repository IDs are required.")
        exit(1)
    print('>>>>>>>>>>>>>>>>End get_contributors_data')

def prepare_user_data():
    """
    Prepare user data from the contributors' details.
    """
    print('>>>>>>>>>>>>>>>>Begin prepare_user_data')
    try:
        with open(CONTRIB_DATA_FILE, 'r') as file1:
            file_data = json.load(file1)
    except FileNotFoundError:
        print(f"Error: File [{CONTRIB_DATA_FILE}] not found. Please check the file existence in the current directory.")
        exit(1)
    except json.JSONDecodeError:
        print("Error: Parsing error in the JSON file [{CONTRIB_DATA_FILE}]. Check for formatting issues.")
        exit(1)
    if file_data:
        # Test with just 2 items
        # file_data = file_data[:2]
        contrib_file_data_size = len(file_data)
        anonymous_contributors = 0
        print(f'''Total contributors fetched: {contrib_file_data_size}''')
        try:
            with open(USER_DATA_FILE, 'w') as file2:
                file2.write('[') # This is required to prepare a JSON array of user data
                for item in file_data:
                    if not isinstance(item, dict):
                        print(f'Item is not a dictionary: {item}. Skipping...')
                        continue
                    username = item.get('login')
                    if username and username is not None:
                        # Run a shell command in a loop to get the user's details --slurp
                        result = run_shell_command([f'gh api --paginate --method GET -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28" /users/{username}'])
                        if result and result.returncode == 0:
                            print(f"Request to fetch GH user login data Succeeded. Returncode: {result.returncode}")
                            print(f'Writing contributor [{contrib_file_data_size}]\'s data to [{USER_DATA_FILE}] file.')
                            
                            file2.write(result.stdout + ',' if contrib_file_data_size > 1 else result.stdout + ']')
                            contrib_file_data_size -= 1
                        else:
                            print(f"Error: Unable to fetch user [{username}] data from GitHub API & write to a file [{USER_DATA_FILE}].")
                            exit(1)
                    else:
                        print(f'Skipping user data for {item}...')
                        contrib_file_data_size -= 1
                        anonymous_contributors += 1
        finally:
            print(f'Closing the file. There were a total of {anonymous_contributors} anonymous contributors that will be excluded from this analysis!')

    print('>>>>>>>>>>>>>>>>End prepare_user_data')

def draw_pie_chart() -> None:
    print('>>>>>>>>>>>>>>>>Begin dwaw_pie_chart')
    try:
        with open(USER_DATA_FILE, 'r') as file3:
            file3_data = json.load(file3)
        
        locations = [item[f'{USER_CHART_BASED_ON}'] for item in file3_data if item.get(f'{USER_CHART_BASED_ON}')]
        print(f"Size: {len(locations)} and '{USER_CHART_BASED_ON}'s: {locations}")

        if locations is not None and len(locations) == 0:
            print(f"'{USER_CHART_BASED_ON}' counts is '0' and cannot draw a pie chart. Please retry with a different parameter from https://docs.github.com/en/rest/users/users?apiVersion=2022-11-28#update-the-authenticated-user by setting 'USER_CHART_BASED_ON' env property.")
            #raise Exception(f"'{USER_CHART_BASED_ON}' counts is '0' and cannot draw a pie chart. Please retry with a different parameter from https://docs.github.com/en/rest/users/users?apiVersion=2022-11-28#update-the-authenticated-user by setting 'USER_CHART_BASED_ON' env property.")
            exit(1)

        location_counts = Counter(locations)
        print(f"'{USER_CHART_BASED_ON}' Counts: {location_counts}")

        # Prepare data for the pie chart
        labels = list(location_counts.keys())
        sizes = list(location_counts.values())

        # Plot the pie chart
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title(f'{GH_ORG}/{GH_REPO} committers based on {USER_CHART_BASED_ON}')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Optionally, Display the chart by un-commenting the below line
        # plt.show()
        # save the chart to a file
        plt.savefig(USER_CHART_FILE)
    except FileNotFoundError:
        print(f"Error: File [{USER_DATA_FILE}] not found. Please check the file path.")
    except json.JSONDecodeError:
        print(f"Error: Parsing error in the JSON file [{USER_DATA_FILE}]. Check for formatting issues.")
    finally:
        print('>>>>>>>>>>>>>>>>End dwaw_pie_chart')

# entry point for the program
if __name__ == '__main__':
    if (os.environ.get('GH_TOKEN') is None or len(os.environ.get('GH_TOKEN')) == 0) and (os.environ.get('GITHUB_TOKEN') is None or len(os.environ.get('GITHUB_TOKEN')) == 0):
        print("GitHub Personal Access Token not found. Create a PAT by following the instructions at https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens")
        os.environ['GH_TOKEN'] = getpass.getpass("\nEnter your GitHub Personal Access Token: ")

    if os.environ.get('GH_ORG') is None:
        os.environ['GH_ORG'] = GH_ORG = input("\nEnter the GitHub Organization ID. E.g. in github.com/apache/cassandra, 'apache' is the GH org: ")
    else:
        GH_ORG = os.environ.get('GH_ORG')

    if os.environ.get('GH_REPO') is None:
        os.environ['GH_ORG'] = GH_REPO = input("\nEnter the GitHub Repository ID. E.g. in github.com/apache/cassandra, 'cassandra' is the GH repo: ")
    else:
        GH_REPO = os.environ.get('GH_REPO')

    global CONTRIB_DATA_FILE
    CONTRIB_DATA_FILE = f'{GH_ORG}_{GH_REPO}_contributors_{YEAR_DATE}.json'
    global USER_DATA_FILE
    USER_DATA_FILE = f'{GH_ORG}_{GH_REPO}_login_details_{YEAR_DATE}.json'
    global USER_CHART_FILE
    USER_CHART_FILE = f'{GH_ORG}_{GH_REPO}_pie_chart_{YEAR_DATE}.png'#./

    try:
        check_gh_cli_installed()
        get_contributors_data()
        prepare_user_data()
        draw_pie_chart()
    except Exception as e:
        raise e
    print('>>>>>>>>>>>>>>>>End of program')
    exit(0)
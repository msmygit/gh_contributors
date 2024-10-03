# GitHub Contributors
- Fetches the contributors list from a GitHub org &amp; repo combo and quickly creates a pie chart based on a parameter.
- Using this script simplifies pulling a repo contribution, making the process more robust and improving the user experience.
- GitHub has [default rate-limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28) for API calls in place and hence we use PAT tokens here. If you don't want to mess with tokens and want a more quick-and-dirty method, answers at [this stackoverflow post](https://stackoverflow.com/questions/9597410/list-all-developers-on-a-project-in-git) has it and one could do some manual steps with the data.

> [!IMPORTANT]
> This utility can only access [*non-anonymous* GitHub user profile](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/setting-your-profile-to-private) data.

## Getting Started
1. Preferably, create [a python virtual environment](https://packaging.python.org/en/latest/tutorials/installing-packages/#creating-virtual-environments) or skip this step if an environment is already available to run this.
2. Install the recommended packages:
   ```
   sudo apt install python3-pip -y
   pip3 install requests matplotlib urllib3
   ```
3. Get it going with `chmod +x ./gh_contributors.py && ./gh_contributors.py`
4. There will be 3 files created, in case of a happy path:
   - `<GH_ORG>_<GH_REPO>_contributors_<YYYYMMDD>.json` containing the contributor details.
   - `<GH_ORG>_<GH_REPO>_login_details_<YYYYMMDD>.json` containing the contributor/user details from above data.
   - `<GH_ORG>_<GH_REPO>_pie_chart_<YYYYMMDD>.png` containing a simple pie chart based on contributor distribution.

<details>
<summary>Expand/Collapse to view the steps to run this program in a non-interactive mode</summary>

For those who prefer the non-interactive mode, set the below environment variables and run it with step 3 from above,
```
export GH_TOKEN= (or) GITHUB_TOKEN=<Your GitHub PAT token>
export GH_ORG=<GitHub Org>
export GH_REPO=<GitHub Repo>
export USER_CHART_BASED_ON=<a valid reponse parameter from https://docs.github.com/en/rest/users/users?apiVersion=2022-11-28#update-the-authenticated-user>
```
</details>

## Things To Know
The GitHub PAT token needs to have access to an organization's repositories or else one will see an error as below in the JSON files,
```
{"message":"Resource protected by organization SAML enforcement. You must grant your Personal Access token access to this organization.","documentation_url":"https://docs.github.com/articles/authenticating-to-a-github-organization-with-saml-single-sign-on/","status":"403"}
```
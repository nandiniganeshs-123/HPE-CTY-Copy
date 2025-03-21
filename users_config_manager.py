import json
import requests


class UsersConfigManager:
    def __init__(self, file_path: str):
        self.file_path = file_path


    def load_data(self) -> dict[str, any]:
        try:
            with open(self.file_path) as f:
                data = json.load(f)  # Load data from the file
            return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Failed to load data from file: {self.file_path}. Error: {str(e)}")
            return {}


    def save_data(self, data: dict[str, any]) -> None:
        try:
            with open(self.file_path, "w") as f:
                json.dump(data, f, indent=4)  # Save data to the file
        except IOError as e:
            print(f"Failed to save data to file: {self.file_path}. Error: {str(e)}")


    def add_user(self, user: str, url: str, userName: str, api_key: str) -> None:
        current_info = self.load_data()
        current_info[user] = {
            "url": url,
            "userName": userName,
            "api_key": api_key,
            "repos": []  # Initialize the repositories list for the user
        }
        self.save_data(current_info)
        print(f"added user {user}")


    def delete_user(self, user: str) -> None:
        current_info = self.load_data()
        if user in current_info:
            del current_info[user]  # Delete the user from the data
            self.save_data(current_info)
            print(f"deleted user {user}")
        else:
            print(f"user {user} not found")


    def list_repos(self, base_url: str, api_key: str) -> list[str]:
        api_endpoint = f'{base_url}/api/repositories'
        headers = {'X-JFrog-Art-Api': api_key}

        try:
            response = requests.get(api_endpoint, headers=headers)  # Send a GET request to the API endpoint
            response.raise_for_status()  # Raise an exception if the request fails

            repositories = response.json()  # Extract the repositories from the response
            repository_names = [repo['key'] for repo in repositories]  # Extract the repository names
            return repository_names
        except requests.RequestException as e:
            print(f"Request failed for URL: {base_url}. Error: {str(e)}")
            return []


    def update_repo_list(self) -> None:
        users_data = self.load_data()
        for user in users_data.keys():
            user_info = users_data[user]
            try:
                repos = self.list_repos(user_info["url"], user_info["api_key"])  # Get the list of repositories
                user_info["repos"] = repos  # Update the repositories list for the user
                users_data[user] = user_info
            except Exception as e:
                print(f"Failed to update repository list for user: {user}. Error: {str(e)}")

        self.save_data(users_data)

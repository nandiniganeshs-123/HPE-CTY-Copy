import os
from dohq_artifactory import RepositoryLocal
from artifactory import ArtifactoryPath
from users_config_manager import UsersConfigManager
import datetime


class ArtifactoryManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.user_config_manager = UsersConfigManager(file_path)


    def download_file(self, download_path: ArtifactoryPath, file_name: str)  -> None:
        try:
            with download_path.open() as fd, open(file_name, "wb") as out:
                out.write(fd.read())  # Download the file and save it locally
        except Exception as e:
            print(f"Failed to download file: {file_name}. Error: {str(e)}")


    def download(self, user: str, download_list: list[str]) -> None:
        try:
            users_info = self.user_config_manager.load_data()
            user_info = users_info[user]
            base_url = user_info["url"]

            for item in download_list:
                path_to_download = os.path.join(base_url, item)
                file_name = os.path.basename(path_to_download)
                download_path = ArtifactoryPath(path_to_download, auth=(user_info["userName"], user_info["api_key"]))
                self.download_file(download_path, file_name)
        except Exception as e:
            print(f"Failed to download files. Error: {str(e)}")


    def upload(self, user: str, upload_list: list[str]) -> None:
        try:
            users_info = self.user_config_manager.load_data()
            user_info = users_info[user]
            base_url = user_info["url"]

            for item in upload_list:
                path_to_upload = os.path.join(base_url, item)
                file_name = os.path.basename(path_to_upload)
                upload_dir_path = os.path.dirname(path_to_upload)
                upload_path = ArtifactoryPath(upload_dir_path, auth=(user_info["userName"], user_info["api_key"]))
                try:
                    upload_path.mkdir()  # Create the directory path if it doesn't exist
                    upload_path.deploy_file(file_name)  # Deploy the file
                except FileExistsError:
                    upload_path.deploy_file(file_name)  # If directory already exists, deploy the file
        except Exception as e:
            print(f"Failed to upload files. Error: {str(e)}")
        self.user_config_manager.update_repo_list()


    def find_repository(self, repo_name: str, user: str) -> None:
        try:
            users_info = self.user_config_manager.load_data()
            user_info = users_info[user]
            url = user_info["url"]
            user_name = user_info["userName"]
            api_key = user_info["api_key"]

            artifactory_path = ArtifactoryPath(url, auth=(user_name, api_key))

            # Check if repo is present
            repo = artifactory_path.find_repository_local(repo_name)

            # if repo is not present
            if repo is None:
                repo = RepositoryLocal(artifactory_path, repo_name, packageType=RepositoryLocal.RPM)
                repo.create()  # Create the repository in Artifactory if it doesn't exist
        except Exception as e:
            print(f"Failed to find or create repository: {repo_name}. Error: {str(e)}")


    def extract_string(self, path_str: str) -> str:
        K = "/"
        N = 4
        try:
            index = 0
            for i in range(N):
                index = path_str.index(K, index) + 1
            return path_str[index:]  # Extract required string from the given path
        except Exception as e:
            print(f"Failed to extract string from path: {path_str}. Error: {str(e)}")
            return -1


    def sync_one_to_two(self, user1: str, user2: str, repo1: str, repo2: str) -> None:
        try:
            self.find_repository(repo2, user2)
            users_info = self.user_config_manager.load_data()

            user1_info = users_info[user1]
            user2_info = users_info[user2]

            user1_base_url = user1_info["url"]
            user2_base_url = user2_info["url"]

            # Create repository URLs for user1 and user2
            repo1_url = os.path.join(user1_base_url, repo1)
            repo2_url = os.path.join(user2_base_url, repo2)

            repo1_path = ArtifactoryPath(repo1_url, auth=(user1_info["userName"], user1_info["api_key"]))
            repo2_path = ArtifactoryPath(repo2_url, auth=(user2_info["userName"], user2_info["api_key"]))

            user2_rpms = []
            rpms_to_upload = []

            for item in repo2_path.glob("**/*.rpm"):
                temp = self.extract_string(str(item))
                user2_rpms.append(temp)  # Collect RPM filenames from repo2

            for item in repo1_path.glob("**/*.rpm"):
                temp = self.extract_string(str(item))
                if temp not in user2_rpms:
                    rpms_to_upload.append(temp)  # Filter RPMs not present in repo2

            self.download(user1, rpms_to_upload)  # Download filtered RPMs from repo1
            self.upload(user2, rpms_to_upload)  # Upload downloaded RPMs to repo2
        except Exception as e:
            print(f"Failed to sync repositories. Error: {str(e)}")

            
    def sync_artifacts_since(self, user2: str, user1: str, repo: str, delta_time: datetime.timedelta,
                         date_time_now: datetime.timedelta) -> None:
        try:
            self.find_repository(repo, user2)

            users_info = self.user_config_manager.load_data()

            user1_info = users_info[user1]
            user2_info = users_info[user2]

            user1_base_url = user1_info["url"]
            user2_base_url = user2_info["url"]

            # Create repository URLs for user1 and user2
            user1_repo_url = os.path.join(user1_base_url, repo)
            user2_repo_url = os.path.join(user2_base_url, repo)

            user1_path = ArtifactoryPath(user1_repo_url, auth=(user1_info["userName"], user1_info["api_key"]))
            user2_path = ArtifactoryPath(user2_repo_url, auth=(user2_info["userName"], user2_info["api_key"]))

            user2_rpms = []
            upload_to_user2 = []

            # Get list of RPMs in user2's repository
            for item in user2_path.glob("**/*.rpm"):
                temp = self.extract_string(str(item))
                user2_rpms.append(temp)

            # Find RPMs in user1's repository that were modified within the specified delta_time
            for item in user1_path.glob("**/*.rpm"):
                try:
                    # Calculate time difference between current time and item's modification time
                    diff: datetime.timedelta = (date_time_now - item.stat().mtime)

                    # Check if the item was modified within the delta_time
                    if diff < delta_time:
                        temp = self.extract_string(str(item))
                        if temp not in user2_rpms:
                            upload_to_user2.append(temp)
                except Exception as e:
                    print(f"Failed to process item: {str(item)}. Error: {str(e)}")

            # Download RPMs that were modified within the delta_time from user1 and upload them to user2
            self.download(user1, upload_to_user2)
            self.upload(user2, upload_to_user2)

        except Exception as e:
            print(f"Error occurred during artifact synchronization: {str(e)}")

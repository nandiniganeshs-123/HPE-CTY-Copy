import logging
from users_config_manager import UsersConfigManager
from artifactory_manager import ArtifactoryManager
import datetime
import pytz

class ArtifactorySync:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.users_config_manager = UsersConfigManager(file_path)
        self.sync_manager = ArtifactoryManager(file_path)
        self.setup_logging()


    def setup_logging(self):
        logging.basicConfig(filename='sync.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def sync_repo_in_two_users(self, user1: str, user2: str, repo1: str, repo2: str) -> None:
        try:
            logging.info(f"Syncing repositories {repo1} and {repo2} between {user1} and {user2}")
            self.sync_manager.sync_one_to_two(user1, user2, repo1, repo2)
            self.sync_manager.sync_one_to_two(user2, user1, repo2, repo1)
            logging.info(f"Sync completed for repositories {repo1} and {repo2} between {user1} and {user2}")
        except Exception as e:
            logging.error(f"Failed to sync repositories {repo1} and {repo2} between {user1} and {user2}. Error: {str(e)}")


    def sync_two_users(self, user1: str, user2: str) -> None:
        try:
            logging.info(f"Syncing all repositories between {user1} and {user2}")
            self.users_config_manager.update_repo_list()
            users_info = self.users_config_manager.load_data()

            user1_info = users_info[user1]
            user2_info = users_info[user2]

            user1_repos = user1_info["repos"]
            user2_repos = user2_info["repos"]

            all_repos = set(user1_repos + user2_repos)

            for repo in all_repos:
                self.sync_repo_in_two_users(user1, user2, repo, repo)

            self.users_config_manager.update_repo_list()
            logging.info(f"Sync all repositories completed between {user1} and {user2}")
        except Exception as e:
            logging.error(f"Failed to sync all repositories between {user1} and {user2}. Error: {str(e)}")


    def sync_all(self) -> None:
        try:
            logging.info("Syncing all repositories among all users")
            self.users_config_manager.update_repo_list()
            users_info = self.users_config_manager.load_data()
            users = list(users_info.keys())

            root = users[0]

            for user in users[1:]:
                user_info = users_info[user]
                user_repos = user_info["repos"]
                for repo in user_repos:
                    self.sync_manager.sync_one_to_two(user, root, repo, repo)

            self.users_config_manager.update_repo_list()

            root_info = users_info[root]
            root_repos = root_info["repos"]

            for user in users[1:]:
                for repo in root_repos:
                    self.sync_manager.sync_one_to_two(root, user, repo, repo)

            self.users_config_manager.update_repo_list()
            logging.info("Sync completed for all repositories among all users")
        except Exception as e:
            logging.error(f"Failed to sync all repositories among all users. Error: {str(e)}")


    def sync_repo_btw_users(self, user1: str, user2: str, repo_name: str) -> None:
        try:
            logging.info(f"Syncing repository {repo_name} between {user1} and {user2}")
            self.users_config_manager.update_repo_list()
            self.sync_repo_in_two_users(user1, user2, repo_name, repo_name)
            self.users_config_manager.update_repo_list()
            logging.info(f"Sync completed for repository {repo_name} between {user1} and {user2}")
        except Exception as e:
            logging.error(f"Failed to sync repository {repo_name} between {user1} and {user2}. Error: {str(e)}")


    def delta_sync_all(self, threshold: int):
        try:
            logging.info(f"Performing delta synchronization(threshold = {threshold}mins) of all repositories among all users")
            self.users_config_manager.update_repo_list()
            delta_time = datetime.timedelta(minutes=threshold)
            date_time_now = datetime.datetime.now(pytz.timezone("GMT"))
            self.users_config_manager.update_repo_list()
            users_info = self.users_config_manager.load_data()
            users = list(users_info.keys())
            root = users[0]

            for user in users[1:]:
                user_info = users_info[user]
                user_repos = user_info["repos"]
                for repo in user_repos:
                    self.sync_manager.sync_artifacts_since(root, user, repo, delta_time, date_time_now)

            self.users_config_manager.update_repo_list()
            root_info = users_info[root]
            root_repos = root_info["repos"]

            for user in users[1:]:
                for repo in root_repos:
                    self.sync_manager.sync_artifacts_since(user, root, repo, delta_time, date_time_now)

            self.users_config_manager.update_repo_list()
            logging.info(f"Delta synchronization(threshold = {threshold}mins) completed for all repositories among all users")
        except Exception as e:
            logging.error(f"Error occurred during delta synchronization of all repositories among all users: {str(e)}")


    def delta_sync_two_users(self, user1: str, user2: str, threshold: int):
        try:
            logging.info(f"Performing delta synchronization(threshold = {threshold}mins) for all repositories between {user1} and {user2}")
            self.users_config_manager.update_repo_list()
            delta_time = datetime.timedelta(minutes=threshold)
            date_time_now = datetime.datetime.now(pytz.timezone("GMT"))
            self.users_config_manager.update_repo_list()
            users_info = self.users_config_manager.load_data()
            user1_info = users_info[user1]
            user2_info = users_info[user2]
            user1_repos = user1_info["repos"]
            user2_repos = user2_info["repos"]
            all_repos = set(user1_repos + user2_repos)

            for repo in all_repos:
                self.sync_manager.sync_artifacts_since(user1, user2, repo, delta_time, date_time_now)
                self.sync_manager.sync_artifacts_since(user2, user1, repo, delta_time, date_time_now)

            self.users_config_manager.update_repo_list()
            logging.info(f"Delta synchronization(threshold = {threshold}mins) for all repositories completed between {user1} and {user2}")
        except Exception as e:
            logging.error(f"Error occurred during delta synchronization of all repositories between {user1} and {user2}: {str(e)}")


    def delta_sync_repo_btw_users(self, user1: str, user2: str, repo_name: str, threshold: int):
        try:
            logging.info(f"Performing delta synchronization(threshold = {threshold}mins) of repository {repo_name} between {user1} and {user2}")
            self.users_config_manager.update_repo_list()
            delta_time = datetime.timedelta(minutes=threshold)
            date_time_now = datetime.datetime.now(pytz.timezone("GMT"))
            self.sync_manager.sync_artifacts_since(user1, user2, repo_name, delta_time, date_time_now)
            self.sync_manager.sync_artifacts_since(user2, user1, repo_name, delta_time, date_time_now)
            self.users_config_manager.update_repo_list()
            logging.info(f"Delta synchronization(threshold = {threshold}mins) completed for repository {repo_name} between {user1} and {user2}")
        except Exception as e:
            logging.error(f"Error occurred during delta synchronization of repository {repo_name} between {user1} and {user2}: {str(e)}")


    def sync_all_sp_repos(self, repos):
        try:
            logging.info("Syncing specified repositories among all users")
            self.users_config_manager.update_repo_list()
            users_info = self.users_config_manager.load_data()
            users = list(users_info.keys())
            root = users[0]

            for user in users[1:]:
                for repo in repos:
                    self.sync_manager.sync_one_to_two(user, root, repo, repo)
                    logging.info(f"Sync repository {repo} from {user} to {root} completed")

            self.users_config_manager.update_repo_list()

            for user in users[1:]:
                for repo in repos:
                    self.sync_manager.sync_one_to_two(root, user, repo, repo)
                    logging.info(f"Sync repository {repo} from {root} to {user} completed")

            self.users_config_manager.update_repo_list()
            logging.info("Sync completed for specified repositories among all users")
        except Exception as e:
            logging.error(f"Failed to sync specified repositories among all users. Error: {str(e)}")

    
    def delta_sync_all_sp(self, threshold: int, repos):
        try:
            logging.info(f"Performing delta synchronization(threshold = {threshold}mins) of specified repositories among all users")
            self.users_config_manager.update_repo_list()
            delta_time = datetime.timedelta(minutes=threshold)
            date_time_now = datetime.datetime.now(pytz.timezone("GMT"))
            self.users_config_manager.update_repo_list()
            users_info = self.users_config_manager.load_data()
            users = list(users_info.keys())
            root = users[0]

            for user in users[1:]:
                for repo in repos:
                    self.sync_manager.sync_artifacts_since(root, user, repo, delta_time, date_time_now)
                    logging.info(f"Delta sync(threshold={threshold}mins) repository {repo} from {user} to {root}")

            self.users_config_manager.update_repo_list()

            for user in users[1:]:
                for repo in repos:
                    self.sync_manager.sync_artifacts_since(user, root, repo, delta_time, date_time_now)
                    logging.info(f"Delta sync(threshold={threshold}mins) repository {repo} from {root} to {user}")

            self.users_config_manager.update_repo_list()
            logging.info(f"Delta synchronization(threshold = {threshold}mins) completed for specified repositories among all users")
        except Exception as e:
            logging.error(f"Error occurred during delta synchronization of specified repositories among all users: {str(e)}")

import os
import argparse
import glob
from sync_logger import ArtifactorySync


def main():
    parser = argparse.ArgumentParser(description="Artifactory Sync")

    group = parser.add_mutually_exclusive_group()

    parser.add_argument("-c", "--config", help="path to the configuration file. If not specified, default is 'config.json'")

    group.add_argument("-au", "--add-user", nargs=4, metavar=("USER", "URL", "USERNAME", "API_KEY"),
                       help="add user to config file")

    group.add_argument("-du", "--delete-user", nargs=1, metavar=("USER"),
                       help="delete user from config file")

    group.add_argument("-sa", "--sync-all", action="store_true", help="sync all repositories between all users")

    group.add_argument("-sar", "--sync-all-repos", nargs="+", metavar=("REPO"),
                       help="sync specified repositories among all users. Atleast one repository must be specified")

    group.add_argument("-su", "--sync-users", nargs="+", metavar="USER1 USER2 REPO1 REPO2",
                       help="sync specified repositories between two users. If repositories not specified, by default all repositories are synchronized.")

    group.add_argument("-dlsa", "--delta-sync-all", nargs=1, metavar=("THRESHOLD"),
                       help="delta sync all users (threshold in minutes)")
    
    group.add_argument("-dlsar", "--delta-sync-all-repos", nargs="+", metavar=("THRESHOLD REPO"),
                       help="delta sync specified repositories among all users. Atleast one repository must be specified")

    group.add_argument("-dlsu", "--delta-sync-users", nargs="*", metavar="USER1 USER2 THRESHOLD REPO1 REPO2",
                       help="delta sync specified repositories between two users (threshold in minutes). If repositories not specified, by default all repositories are synchronized.")

    args = parser.parse_args()

    config_file = args.config if args.config else "config.json"

    sync = ArtifactorySync(config_file)

    if args.sync_all:
        sync.sync_all()

    elif args.sync_all_repos:
        repos = args.sync_all_repos[:]
        sync.sync_all_sp_repos(repos)

    elif args.sync_users:
        user1, user2 = args.sync_users[:2]
        repos = args.sync_users[2:]
        if not repos:
            sync.sync_two_users(user1, user2)
        else:
            for repo in repos:
                sync.sync_repo_btw_users(user1, user2, repo)

    elif args.add_user:
        user, url, user_name, api_key = args.add_user
        sync.users_config_manager.add_user(user, url, user_name, api_key)

    elif args.delete_user:
        user = args.delete_user[0]
        sync.users_config_manager.delete_user(user)

    elif args.delta_sync_all:
        threshold = args.delta_sync_all[0]
        sync.delta_sync_all(int(threshold))

    elif args.delta_sync_all_repos:
        threshold = args.delta_sync_all_repos[0]
        repos = args.delta_sync_all_repos[1:]
        if not repos:
            error_msg = "No repository specified"
            parser.error(error_msg)
        sync.delta_sync_all_sp(int(threshold), repos)

    elif args.delta_sync_users:
        user1, user2 = args.delta_sync_users[:2]
        threshold = args.delta_sync_users[2]
        try:
            repos = args.delta_sync_users[3:]
        except:
            pass
        if not repos:
            sync.delta_sync_two_users(user1, user2, int(threshold))
        else:
            for repo in repos:
                sync.delta_sync_repo_btw_users(user1, user2, repo, int(threshold))

    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
        rpm_files = glob.glob("*.rpm")
        if rpm_files:
            os.system("rm *.rpm")
    except Exception as e:
        print("An error occurred:", str(e))

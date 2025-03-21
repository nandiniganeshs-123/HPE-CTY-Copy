# HPE-CTY-Artifactory-Sync

# Artifactory Sync with additional options

## Artifactory Sync is a Python script that synchronizes artifacts from multiple JFrog Artifactory repositories and logs the synchronization process.

### Installation:

Clone the repository:

  ```bash
  git clone https://github.com/your-username/artifactory-sync-logger.git
  ```
  

### Usage:

The script provides a command line interface to perform various operations. Here are the available options:

  ```bash
  usage: command_line_parser.py [-h] [-c CONFIG] [-au USER URL USERNAME API_KEY | -du USER | -sa | -sar REPO [REPO ...] | -su USER1 USER2 REPO1 REPO2
                              [USER1 USER2 REPO1 REPO2 ...] | -dlsa THRESHOLD | -dlsar THRESHOLD REPO [THRESHOLD REPO ...] | -dlsu
                              [USER1 USER2 THRESHOLD REPO1 REPO2 ...]]

  Artifactory Sync

  options:
    -h, --help                    show this help message and exit
    -c CONFIG, --config CONFIG    path to the configuration file. If not specified, default is 'config.json'
    -au USER URL USERNAME API_KEY, --add-user USER URL USERNAME API_KEY
                                  add user to config file
    -du USER, --delete-user USER  delete user from config file
    -sa, --sync-all               sync all repositories between all users
    -sar REPO [REPO ...], --sync-all-repos REPO [REPO ...]
                                  sync specified repositories among all users. Atleast one repository must be specified
    -su USER1 USER2 REPO1 REPO2 [USER1 USER2 REPO1 REPO2 ...], --sync-users USER1 USER2 REPO1 REPO2 [USER1 USER2 REPO1 REPO2 ...]
                                  sync specified repositories between two users. If repositories not specified, by default all repositories are synchronized.
    -dlsa THRESHOLD, --delta-sync-all THRESHOLD
                                  delta sync all users (threshold in minutes)
    -dlsar THRESHOLD REPO [THRESHOLD REPO ...], --delta-sync-all-repos THRESHOLD REPO [THRESHOLD REPO ...]
                                  delta sync specified repositories among all users. Atleast one repository must be specified
    -dlsu [USER1 USER2 THRESHOLD REPO1 REPO2 ...], --delta-sync-users [USER1 USER2 THRESHOLD REPO1 REPO2 ...]
                                  delta sync specified repositories between two users (threshold in minutes). If repositories not specified, by default all repositories are synchronized.
  ```

To perform an operation with these options, open a terminal and navigate to the directory containing the script. Then, run the script with the desired options.

Here is an example to sync all repositories among all users:

  ```bash
  python3 command_line_parser.py -sa
  ```

Note: Make sure to configure the config.json file with the necessary Artifactory server URLs, user credentials, and repository lists before running the script.

### File Descriptions:

#### user_config_manager.py: 
- This file contains the UsersConfigManager class, which handles the loading and saving of user configuration data from a file.
- It provides methods for adding users, deleting users, listing repositories, and updating the repository list for each user.
- It uses the requests library to make HTTP requests for retrieving repository information from an Artifactory server.

#### artifactory_manager.py:
- This file contains the ArtifactoryManager class, which interacts with the Artifactory server and performs operations such as downloading and uploading files, finding and creating repositories, and synchronizing repositories between users.
- It uses the dohq_artifactory and artifactory libraries to interact with the Artifactory server.
- It relies on the UsersConfigManager class from user_config_manager.py to load user configuration data and update repository lists.

#### sync_logger.py: 
- This file contains the ArtifactorySync class, which provides methods for synchronizing repositories between users and logging the synchronization process.
- It uses the UsersConfigManager and ArtifactoryManager classes from the other files to perform repository synchronization and manage user configuration data.
- It uses the logging module to log synchronization events to a file.

#### Configuration File (config.json):

The `config.json` file is used to store the configuration settings for the `sync_logger.py` script. It contains the following information for each user:

- `url`: The URL of the JFrog Artifactory server.
- `userName`: The username of the user.
- `api_key`: The API key or token associated with the user.
- `repos`: A list of repositories to be synchronized for the user.

Here's an example of the structure of the config.json file:

  ```json
  {
      "x": {
          "url": "https://your-artifactory-server/artifactory",
          "userName": "your-username@gmail.com",
          "api_key": "your-api-key",
          "repos": []
      },
      "y": {

      },
  }
  ```


# Folders sync
Synchronizes two folders: source and replica.



### How to Run It 

Using python:

``python sync.py source_folder replica_folder 60 sync.log``

Using uv:

``uv run python sync.py source_folder replica_folder 60 sync.log``

### What Happens?

>Every 60 seconds (or whatever interval you set), the script:
Compares source_folder and replica_folder.
Copies missing or changed files from source to replica.
Removes extra files from replica that are not in source.
Logs all actions to sync.log.

### How to Get Help

To display the help message with available arguments, run:

``python sync.py --help``

or

``uv run python sync.py --help``
This will show details about required parameters and usage instructions.

<img width="623" alt="Help" src="https://github.com/user-attachments/assets/02bbf3aa-68c6-462f-8f2e-ead609d8c381" />


### Action Flow

Each commit triggers an automated action flow that includes:

- Running pytest to execute unit tests and verify code integrity.

- Ensuring all tests pass before merging changes.
  
<img width="1344" alt="testrun" src="https://github.com/user-attachments/assets/32e1cc1a-37ad-4a2f-bc28-922b08ab8216" />


### Demo

https://github.com/user-attachments/assets/a89e9a5a-55bf-40fc-8b97-3774c4566dba




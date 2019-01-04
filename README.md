# IRIDA Retrieve

Gets stuff from the NAS, and tosses it onto an external drive.

To use:

- Make sure you have the BBMap suite installed and accessible via your $PATH - this script needs `reformat.sh` and
`kmercountexact.sh`, and will complain at you and refuse to run if it can't find them.

- Clone this repository.

- `source /mnt/nas2/redmine/applications/.virtualenvs/OLCRedmineAutomator/bin/activate`

- `python Irida_Retrieve.py`

- Enter your Redmine API key and the path to the drive you want to copy the files to when prompted.


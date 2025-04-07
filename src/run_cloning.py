from core.cloning import clone_or_update_all_projects
import urllib3


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    clone_or_update_all_projects()

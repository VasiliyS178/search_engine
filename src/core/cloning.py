import os
from time import sleep
import logging
import gitlab
import git
from .config import settings


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s", datefmt=None)
logger = logging.getLogger(__name__)


GITLAB_HOST = settings.GITLAB_HOST
GITLAB_TOKEN = settings.GITLAB_TOKEN
GROUP_ID = int(settings.GROUP_ID)
REPOSITORIES_ROOT_DIR = settings.REPOSITORIES_ROOT_DIR

gl = gitlab.Gitlab(GITLAB_HOST, private_token=GITLAB_TOKEN, ssl_verify=False, api_version="4")


def get_subgroups_ids(gr_id: int):
    all_groups_ids = [gr_id]
    group = gl.groups.get(gr_id)
    subgroups = group.subgroups.list(as_list=False)
    sleep(0.1)
    if subgroups:
        subgroups_ids = [subgroup.id for subgroup in subgroups]
        all_groups_ids.extend(subgroups_ids)
        for subgroup_id in subgroups_ids:
            get_subgroups_ids(subgroup_id)
    return all_groups_ids


def update_projects_by_group(gr_id):
    projects_info = []
    group = gl.groups.get(gr_id)
    projects = group.projects.list(as_list=False, get_all=True)
    for project in projects:
        clone_path = os.path.join(REPOSITORIES_ROOT_DIR, project.namespace["full_path"])
        project_path = os.path.join(clone_path, project.path)
        projects_info.append(f'{group.full_path};{project.path}')

        if os.path.exists(project_path):
            logger.info(f"Update project: '{project_path}'")
            repo = git.Repo(project_path)
            repo.git.fetch()  # Обновляем список веток
            branches = repo.git.branch('-a')
            # print(branches)
            target_branch = None
            for branch in branches:
                if 'HEAD' in branch:
                    target_branch = branch.split("/")[1]
                    break
            if len(branches) > 0:
                target_branch = branches[0]
            if target_branch:
                try:
                    repo.git.checkout(target_branch)
                    repo.git.pull()
                except:
                    logger.exception(f"Error updating project: '{project_path}'")
            else:
                logger.warning(f"No branches in project: '{project_path}'")
        else:
            if not os.path.exists(clone_path):
                os.makedirs(clone_path)
            url = f'https://oauth2:{GITLAB_TOKEN}@{project.http_url_to_repo.split("https://")[1]}'
            logger.info(f"Cloning project: '{url}'")
            try:
                git.Git(clone_path).clone(url)
            except git.GitCommandError:
                logger.exception(f"Error cloning project: '{url}'")
        sleep(0.1)
    return projects_info


def clone_or_update_all_projects():
    all_groups_ids = get_subgroups_ids(GROUP_ID)
    for group_id in all_groups_ids:
        projects_info = update_projects_by_group(group_id)
        with open(os.path.join(settings.LOGS_PATH, "projects.txt"), "a", encoding="utf-8") as f:
            f.write("\n".join(projects_info))


if __name__ == '__main__':
    clone_or_update_all_projects()

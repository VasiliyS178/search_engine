import os
from time import sleep
import logging
import gitlab
import git
from .config import settings


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s", datefmt=None)
logger = logging.getLogger(__name__)


gitlab_host = settings.GITLAB_HOST
gitlab_token = settings.GITLAB_TOKEN
GROUP_ID = settings.GROUP_ID
repositories_root_dir = settings.REPOSITORIES_ROOT_DIR
cloning_mode = settings.CLONING_MODE

gl = gitlab.Gitlab(gitlab_host, private_token=gitlab_token, ssl_verify=False, api_version="4")


def get_subgroups_ids(gr_id):
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
    group = gl.groups.get(gr_id)
    projects = group.projects.list(as_list=False, get_all=True)
    for project in projects:
        clone_path = os.path.join(repositories_root_dir, project.namespace["full_path"])
        project_path = os.path.join(clone_path, project.path)

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
            url = f'https://oauth2:{gitlab_token}@{project.http_url_to_repo.split("https://")[1]}'
            logger.info(f"Cloning project: '{url}'")
            try:
                git.Git(clone_path).clone(url)
            except git.GitCommandError:
                logger.exception(f"Error cloning project: '{url}'")
        sleep(0.1)


def clone_or_update_all_projects():
    all_groups_ids = get_subgroups_ids(GROUP_ID)
    for group_id in all_groups_ids:
        update_projects_by_group(group_id)


if __name__ == '__main__':
    clone_or_update_all_projects()

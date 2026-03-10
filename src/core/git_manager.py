import git
import os
from datetime import datetime


class GitLabManager:
    def __init__(self, repo_path):
        """
        Инициализация менеджера репозитория

        Args:
            repo_path (str): Путь к локальному репозиторию
        """
        self.repo_path = repo_path
        self.repo = None
        self._load_repo()

    def _load_repo(self):
        """Загрузка репозитория"""
        try:
            self.repo = git.Repo(self.repo_path)
            print("Репозиторий успешно загружен")
        except git.InvalidGitRepositoryError:
            print("Указанный путь не является репозиторием Git")

    def get_repo_info(self):
        """Получение информации о репозитории"""
        if not self.repo:
            return None

        info = {
            'branch': self.repo.active_branch.name,
            'head_commit': str(self.repo.head.commit)[:8],
            'commit_message': self.repo.head.commit.message.strip(),
            'commit_author': self.repo.head.commit.author.name,
            'commit_date': self.repo.head.commit.committed_datetime.isoformat(),
            'remote_url': None
        }

        # Получаем URL удаленного репозитория
        try:
            info['remote_url'] = self.repo.remotes.origin.url
        except:
            pass

        return info

    def get_branches(self):
        """Получение списка веток"""
        if not self.repo:
            return []

        branches = []
        for branch in self.repo.branches:
            branches.append({
                'name': branch.name,
                'is_active': branch.name == self.repo.active_branch.name,
                'commit': str(branch.commit)[:8]
            })
        return branches

    def create_branch(self, branch_name):
        """Создание новой ветки"""
        if not self.repo:
            return False

        try:
            self.repo.create_head(branch_name)
            print(f"Ветка '{branch_name}' создана успешно")
            return True
        except Exception as e:
            print(f"Ошибка создания ветки: {e}")
            return False

    def switch_branch(self, branch_name):
        """Переключение на ветку"""
        if not self.repo:
            return False

        try:
            branch = self.repo.heads[branch_name]
            branch.checkout()
            print(f"Переключено на ветку '{branch_name}'")
            return True
        except Exception as e:
            print(f"Ошибка переключения ветки: {e}")
            return False

    def add_files(self, paths):
        """Добавление файлов в индекс"""
        if not self.repo:
            return False

        try:
            if isinstance(paths, str):
                paths = [paths]

            self.repo.index.add(paths)
            print(f"Файлы добавлены в индекс: {paths}")
            return True
        except Exception as e:
            print(f"Ошибка добавления файлов: {e}")
            return False

    def commit_changes(self, message):
        """Коммит изменений"""
        if not self.repo:
            return False

        try:
            # Проверяем наличие изменений
            if not self.repo.is_dirty():
                print("Нет изменений для коммита")
                return False

            # Коммитим все изменения
            self.repo.index.commit(message)
            print(f"Изменения закоммичены: {message}")
            return True
        except Exception as e:
            print(f"Ошибка коммита: {e}")
            return False

    def push_changes(self, remote_name='origin', branch_name=None):
        """Отправка изменений на сервер"""
        if not self.repo:
            return False

        try:
            if branch_name is None:
                branch_name = self.repo.active_branch.name

            origin = self.repo.remotes[remote_name]
            origin.push(refspec=f'{branch_name}:{branch_name}')
            print(f"Изменения отправлены на {remote_name}/{branch_name}")
            return True
        except Exception as e:
            print(f"Ошибка отправки изменений: {e}")
            return False

    def pull_changes(self, remote_name='origin', branch_name=None):
        """Получение изменений с сервера"""
        if not self.repo:
            return False

        try:
            if branch_name is None:
                branch_name = self.repo.active_branch.name

            origin = self.repo.remotes[remote_name]
            origin.pull(refspec=f'{branch_name}:{branch_name}')
            print(f"Изменения получены с {remote_name}/{branch_name}")
            return True
        except Exception as e:
            print(f"Ошибка получения изменений: {e}")
            return False

    def get_status(self):
        """Получение статуса репозитория"""
        if not self.repo:
            return None

        status = self.repo.git.status(porcelain=True)
        lines = status.split('\n') if status else []

        files = []
        for line in lines:
            if line:
                status_code = line[:2]
                file_path = line[3:]
                files.append({
                    'status': status_code,
                    'path': file_path,
                    'description': self._get_status_description(status_code)
                })

        return files

    def _get_status_description(self, status_code):
        """Получение описания статуса файла"""
        descriptions = {
            '??': 'Новый файл',
            ' M': 'Измененный файл',
            ' D': 'Удаленный файл',
            ' A': 'Добавленный файл',
            ' R': 'Переименованный файл'
        }
        return descriptions.get(status_code, 'Неизвестный статус')

    def get_recent_commits(self, count=10):
        """Получение последних коммитов"""
        if not self.repo:
            return []

        commits = []
        for commit in self.repo.iter_commits(limit=count):
            commits.append({
                'hash': str(commit)[:8],
                'message': commit.message.strip(),
                'author': commit.author.name,
                'date': commit.committed_datetime.isoformat(),
                'parents': [str(parent)[:8] for parent in commit.parents]
            })
        return commits

    def get_diff(self, commit_a=None, commit_b='HEAD'):
        """Получение различий между коммитами"""
        if not self.repo:
            return None

        try:
            if commit_a is None:
                diff = self.repo.git.diff(commit_b)
            else:
                diff = self.repo.git.diff(commit_a, commit_b)

            return diff
        except Exception as e:
            print(f"Ошибка получения diff: {e}")
            return None


# Примеры использования:

def example_usage():
    """Примеры использования класса GitLabManager"""

    # 1. Создание и инициализация репозитория
    repo_path = "./test_repo"
    manager = GitLabManager(repo_path)

    # 2. Получение информации о репозитории
    info = manager.get_repo_info()
    if info:
        print("Информация о репозитории:")
        for key, value in info.items():
            print(f"  {key}: {value}")

    # 3. Получение списка веток
    branches = manager.get_branches()
    print("\nВетки:")
    for branch in branches:
        print(f"  {branch['name']} ({'активна' if branch['is_active'] else 'не активна'})")

    # 4. Создание новой ветки
    # manager.create_branch("feature/new-feature")

    # 5. Переключение на ветку
    # manager.switch_branch("feature/new-feature")

    # 6. Получение статуса репозитория
    status = manager.get_status()
    if status:
        print("\nСтатус файлов:")
        for file in status:
            print(f"  {file['status']} {file['path']} ({file['description']})")

    # 7. Получение последних коммитов
    recent_commits = manager.get_recent_commits(5)
    print("\nПоследние коммиты:")
    for commit in recent_commits:
        print(f"  {commit['hash']} - {commit['message'][:50]}...")

    # 8. Коммит и отправка изменений
    # manager.add_files(["file1.txt", "file2.py"])
    # manager.commit_changes("Добавлены новые файлы")
    # manager.push_changes()


# Примеры работы с удаленным репозиторием через HTTPS
def clone_and_work_with_gitlab():
    """
    Пример клонирования репозитория GitLab и работы с ним
    """
    try:
        # Клонирование репозитория
        repo_url = "https://gitlab.com/your_username/your_repo.git"
        local_path = "./cloned_repo"

        # Клонируем репозиторий
        repo = git.Repo.clone_from(repo_url, local_path)
        print("Репозиторий клонирован успешно")

        # Работаем с клонированным репозиторием
        manager = GitLabManager(local_path)

        # Получаем информацию
        info = manager.get_repo_info()
        print(f"Активная ветка: {info['branch']}")

        # Добавляем файл и коммитим
        with open(os.path.join(local_path, "test_file.txt"), "w") as f:
            f.write("Тестовый файл")

        manager.add_files("test_file.txt")
        manager.commit_changes("Добавлен тестовый файл")

        # Отправляем на сервер
        # manager.push_changes()

        return repo

    except Exception as e:
        print(f"Ошибка: {e}")
        return None


# Пример работы с SSH (если у вас SSH ключи)
def clone_with_ssh():
    """
    Пример клонирования через SSH
    """
    try:
        repo_url = "git@gitlab.com:your_username/your_repo.git"
        local_path = "./ssh_cloned_repo"

        # Установка SSH конфигурации
        os.environ['GIT_SSH_COMMAND'] = 'ssh -i ~/.ssh/id_rsa'

        repo = git.Repo.clone_from(repo_url, local_path)
        print("Репозиторий клонирован через SSH")

        return repo

    except Exception as e:
        print(f"Ошибка SSH клонирования: {e}")
        return None


if __name__ == "__main__":
    # Запустить примеры
    example_usage()
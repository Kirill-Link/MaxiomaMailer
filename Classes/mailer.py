import imaplib
import shlex

from imap_tools.imap_utf7 import encode, decode


class Mailer:

    def __init__(self, server, user_email, password):
        self.mail = imaplib.IMAP4_SSL(server)
        self.mail.login(user_email, password)
        self.mail.select('inbox')

    def create_folder(self, parent_folder, folder_name):
        self.mail.create(f'{parent_folder}/{folder_name}')

    def get_parent_folders(self):
        find_folder = []
        for folder in self.mail.list(directory='.')[1]:
            folder_name = shlex.split(decode(folder))[-1]
            if '/' not in folder_name:
                find_folder.append(folder_name)

        return find_folder

    def create_client_folder(self, folder_name):
        self.mail.create(folder_name)

    def get_client_folders(self, parent_folder):
        find_folders = []
        status, folder_list = self.mail.list(directory=f'"{parent_folder}"')

        if status == "OK":
            for folder in folder_list:
                folder_name = shlex.split(folder.decode())[-1]

                if '/' in folder_name and folder_name.startswith(parent_folder):
                    child_folder = folder_name[len(parent_folder) + 1:]
                    find_folders.append(child_folder)

        # Проверка наличия папки и создание, если её нет
        if not find_folders:
            self.create_client_folder(parent_folder)  # Метод create_folder должен быть определен в вашем классе

        return find_folders

    def is_folder_exists(self, parent_folder, folder_name, create_if_not_exists=True):
        # Получаем список всех доступных папок
        status, folder_list = self.mail.list()

        # Проверяем, существует ли указанная папка
        for folder_info in folder_list:
            _, _, current_folder = folder_info.decode().partition(' "/" ')
            if current_folder == folder_name:
                return True

        # Если папка не найдена и create_if_not_exists=True, создаем папку
        if create_if_not_exists:
            self.mail.create(f'{parent_folder}/{folder_name}')
            return True

        return False

    def delete_folder(self, folder_name):
        pass

    def close_mail_connect(self):
        self.mail.close()
        self.mail.logout()

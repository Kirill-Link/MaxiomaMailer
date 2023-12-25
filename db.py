import mysql.connector


class BotDB:

    def __init__(self, host, port, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            port=port,
            password=password,
            database=database
        )
        self.cursor: mysql.connector.cursor.MySQLCursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Создаем таблицы, если они не существуют"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT UNIQUE,
                status BOOLEAN DEFAULT FALSE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS filters (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                email VARCHAR(255),
                parent_folder VARCHAR(255),
                client_folder VARCHAR(255),
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        self.conn.commit()

    def fetchone(self):
        """Возвращает одну запись из результата выполнения запроса"""
        return self.cursor.fetchone()

    def user_exists(self, user_id):
        """Проверяем, есть ли юзер в базе"""
        self.cursor.execute("SELECT id FROM users WHERE user_id = %s", (user_id,))
        result = self.cursor.fetchone()
        return bool(result)

    def user_status_exists(self, user_id):
        """Проверяем, существует ли статус True для юзера в базе"""
        self.cursor.execute("SELECT id FROM users WHERE user_id = %s AND status = TRUE", (user_id,))
        result = self.cursor.fetchone()
        return bool(result)

    def get_user_id(self, user_id):
        """Достаем id юзера в базе по его user_id"""
        self.cursor.execute("SELECT id FROM users WHERE user_id = %s", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_user_info(self):
        self.cursor.execute("SELECT id FROM users WHERE status = 0")
        results = self.cursor.fetchall()
        return [result[0] for result in results] if results else []

    def update_user_status(self, new_status):

        user_ids = self.get_user_info()

        if user_ids:
            # Список кортежей параметров для каждого пользователя
            params = [(new_status, user_id) for user_id in user_ids]

            # Используем executemany для передачи списка кортежей
            self.cursor.executemany("UPDATE users SET status = %s WHERE id = %s", params)
            self.conn.commit()

    def add_user(self, user_id):
        """Добавляем юзера в базу"""
        self.cursor.execute("INSERT IGNORE INTO users (user_id) VALUES (%s)", (user_id,))
        self.conn.commit()

    def add_filter(self, user_id, email, parent_folder, client_folder):
        """Добавляем фильтр в базу данных"""
        self.cursor.execute("""
            INSERT INTO filters (user_id, email, parent_folder, client_folder) 
            VALUES (%s, %s, %s, %s)""",
                            (self.get_user_id(user_id), email, parent_folder, client_folder))
        self.conn.commit()

    def get_all_filter_data(self):
        """Получаем все данные из таблицы filters"""
        query = "SELECT email, parent_folder, client_folder FROM filters"
        self.cursor.execute(query)
        results = self.cursor.fetchall()

        # Возвращаем список словарей с данными фильтров
        filter_data_list = []
        for result in results:
            filter_data_list.append({
                'email': result[0],
                'parent_folder': result[1],
                'client_folder': result[2]
            })

        return filter_data_list

    def close(self):
        """Закрываем соединение с БД"""
        self.conn.close()

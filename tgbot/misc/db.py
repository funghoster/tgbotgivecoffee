import sqlite3

def sql_start():
    global conn, cursor
    conn = sqlite3.connect('coffeetest.db')
    cursor = conn.cursor()
    if conn:
        print('Database connected, OK!')

async def user_exists(user_id):
    """Проверяем, есть ли юзер в базе"""
    result = cursor.execute("SELECT * FROM `user` WHERE `user_id` = ?", (user_id,)).fetchall()
    return bool(len(result))

async def get_user_id(user_id):
    """Достаем id юзера в базе по его user_id"""
    result = cursor.execute("SELECT `id` FROM `user` WHERE `user_id` = ?", (user_id,))
    return result.fetchone()[0]

def get_user_info(user_id):
    """Достаем информацию о юзере в базе по его user_id"""
    result = cursor.execute("SELECT user_center, user_descr, user_name, user_date FROM `user` WHERE user_id = ?", (user_id,))
    return result.fetchone()

async def add_user(state):
    """Добавляем юзера в базу"""
    async with state.proxy() as data:
        cursor.execute("INSERT INTO user(user_id, user_center, user_descr, user_name) VALUES (?, ?, ?, ?)", tuple(data.values()))
        return conn.commit()

def add_record_center(user_center, user_id):
    """Изменяем запись о торговом центре"""
    cursor.execute("UPDATE user SET user_center = ? WHERE user_id = ?", (user_center, user_id))
    return conn.commit()

def add_record_description(user_descr, user_id):
    """Изменяем запись информации о пользователе"""
    cursor.execute("UPDATE user SET user_descr = ? WHERE user_id = ?", (user_descr, user_id,))
    return conn.commit()

def add_record_name(user_name, user_id):
    """Изменяем запись имени о пользователе"""
    cursor.execute("UPDATE 'user' SET user_name = ? WHERE user_id = ?", (user_name, user_id,))
    return conn.commit()

async def add_order(state):
    """Добавляем заказ"""
    async with state.proxy() as data:
        cursor.execute("INSERT INTO 'order'(user_id, order_type, order_name, order_number, order_descr, order_ready) VALUES (?, ?, ?, ?, ?, ?)", tuple(data.values()))
        return conn.commit()
    
def set_new_order_status(set_order, id):
    """Изменяем статус заказа"""
    cursor.execute("UPDATE 'order' SET order_ready = ? WHERE id = ?", (set_order, id,))
    return conn.commit()

async def user_order_exists(user_id, complete_order):
    """Проверяем, наличие заказов у юзера"""
    result = cursor.execute("SELECT * FROM `order` WHERE `user_id` = ? AND order_ready = ?", (user_id, complete_order,)).fetchall()
    return bool(len(result))

def get_count_order_ready_for_admin(complete_order):
    """Достаем колличество заказов юзеров для админа"""
    result = cursor.execute("SELECT COUNT(id) FROM `order` WHERE order_ready = ?", (complete_order,))
    return result.fetchone()

def get_count_order_ready(user_id, complete_order):
    """Достаем колличество заказов юзера по его user_id"""
    result = cursor.execute("SELECT COUNT(id) FROM `order` WHERE user_id = ? AND order_ready = ?", (user_id, complete_order,))
    return result.fetchone()

def get_count_all_order_ready(complete_order):
    """Достаем колличество заказов юзера по его user_id"""
    result = cursor.execute("SELECT COUNT(id) FROM `order` WHERE order_ready = ?", (complete_order,))
    return result.fetchone()

def get_order(user_id, complete_order, limit_skip, limit_set):
    """Получаем список заказов юзера"""
    result = cursor.execute("SELECT id, order_type, order_name, order_number, order_descr FROM 'order' WHERE user_id = ? AND order_ready = ? ORDER BY id DESC LIMIT ?, ?", (user_id, complete_order, limit_skip, limit_set, ))
    return result.fetchone()

def get_all_order(complete_order, limit_skip, limit_set):
    """Получаем все списки заказов"""
    result = cursor.execute("SELECT id, user_id, order_type, order_name, order_number, order_descr, order_date FROM 'order' WHERE order_ready = ? ORDER BY id DESC LIMIT ?, ?", (complete_order, limit_skip, limit_set, ))
    return result.fetchone()

def delete(id: int):
    """Удаляем заказ из бд""" 
    cursor.execute("DELETE FROM 'order' WHERE id = ?", (id, ))
    cursor.connection.commit()

def add_worker(user_id, worker_name):
    """Добавляем работника в базу"""
    cursor.execute("INSERT INTO worker(user_id, worker_name) VALUES (?, ?)", (user_id, worker_name, ))
    return conn.commit()

async def worker_exists(user_id):
    """Проверяем, есть ли работник в базе"""
    result = cursor.execute("SELECT * FROM `worker` WHERE `user_id` = ?", (user_id,)).fetchall()
    return bool(len(result))

async def working_exists(working: bool):
    """Проверяем, наличие работающих"""
    result = cursor.execute("SELECT * FROM `worker` WHERE `working` = ?", (working, )).fetchall()
    return bool(len(result))

def get_count_working():
    """Достаем колличество работников"""
    result = cursor.execute("SELECT COUNT(id) FROM `worker` ", )
    return result.fetchone()

def get_worker():
    """Достаем работников из бд"""
    result = cursor.execute("SELECT id, worker_name FROM `worker`",)
    return result.fetchall()

def edit_worker_status(set_working, user_id):
    """Изменяем статус работника"""
    cursor.execute("UPDATE 'worker' SET working = ? WHERE user_id = ?", (set_working, user_id,))
    return conn.commit()

def get_worker_working(working):
    """Достаем работников с открытой сменой"""
    result = cursor.execute("SELECT user_id, worker_name FROM `worker` WHERE working = ?", (working,))
    return result.fetchone()

def get_status_exists(user_id):
    """Проверяем статус работы"""
    result = cursor.execute("SELECT working FROM `worker` WHERE user_id = ?", (user_id, ))
    return result.fetchone()

def set_edit_worker_status(status, user_id):
    """Открываем смену"""
    cursor.execute("UPDATE 'worker' SET working = ? WHERE user_id = ?", (status, user_id,))
    return conn.commit()

def get_stock_list():
    """Получаем список кофе для создания кнопок"""
    result = cursor.execute("SELECT stock_name FROM `stock` WHERE `stock_type` = 'Кофе'",)
    return result.fetchall()



def close(self):
    """Закрываем соединение с БД"""
    self.connection.close()

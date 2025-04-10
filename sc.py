import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import os
import oracledb
import re

def get_db_connection():
    return oracledb.connect(
        user="register",
        password="P@ssw0rd",
        dsn="localhost:1521/orcl"
    )

class GameApp:

    def __init__(self, root):
        self.current_user = None
        self.current_password = None
        self.user_connection = None

        self.root = root
        self.root.title("Слова из слова")
        self.root.geometry("1200x675")
        self.root.resizable(False, False)

        self.root.update_idletasks()
        self.root.geometry(self.root.geometry())

        self.canvas = tk.Canvas(self.root, width=1200, height=675)
        self.canvas.pack(fill="both", expand=True)

        self.set_background_image()
        self.create_interface()

    def set_background_image(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(current_dir, "background.png")

            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Файл не найден: {image_path}")

            self.bg_image = Image.open(image_path).resize((1500, 845))
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        except Exception as e:
            print(f"Ошибка загрузки фона: {e}")
            self.canvas.configure(bg="#2c3e50")

    def create_interface(self):
        self.canvas.create_text(
            50, 30,
            text="🏆 ТОП-10 ИГРОКОВ",
            font=("Arial", 20),
            fill="white",
            anchor="nw"
        )

        self.update_leaderboard()

        self.auth_btn = self.create_button(self.canvas, "Авторизация", self.login)
        self.auth_btn.place(x=1200, y=30)

        self.reg_btn = self.create_button(self.canvas, "Регистрация", self.register)
        self.reg_btn.place(x=1200, y=100)

        self.user_label = None
        self.logout_btn = None
        self.find_game_btn = None

    def show_user_controls(self):
        if self.auth_btn: 
            self.auth_btn.place_forget()
        if self.reg_btn: 
            self.reg_btn.place_forget()

        # Получаем количество очков пользователя из таблицы leaderboard от имени пользователя register
        try:
            # Создаем подключение от имени пользователя register
            register_connection = get_db_connection()  # Это ваше подключение от имени пользователя register
            
            with register_connection.cursor() as cursor:
                cursor.execute("SELECT score FROM REGISTER.leaderboard WHERE username = :username", {"username": self.current_user})
                score = cursor.fetchone()
                if score:
                    score_text = f" — Очки: {score[0]}"
                else:
                    score_text = " — Очки: 0"

            register_connection.close()  # Закрываем подключение после использования
        except oracledb.DatabaseError as e:
            score_text = " — Ошибка при получении очков"

        # Создаем метку с именем пользователя и его очками
        self.user_label = tk.Label(
            self.canvas,
            text=f"👤 {self.current_user}{score_text}",
            font=("Arial", 14, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        self.user_label.place(x=1200, y=30)

        self.find_game_btn = self.create_button(self.canvas, "Найти игру", self.open_game_window)
        self.find_game_btn.place(x=1200, y=70)

        self.logout_btn = self.create_button(self.canvas, "Выход", self.logout)
        self.logout_btn.place(x=1200, y=110)



    def logout(self):
        self.current_user = None
        self.current_password = None
        self.user_connection = None

        if self.user_label:
            self.user_label.destroy()
        if self.logout_btn:
            self.logout_btn.destroy()
        if self.find_game_btn:
            self.find_game_btn.destroy()

        self.auth_btn.place(x=1200, y=30)
        self.reg_btn.place(x=1200, y=100)

    def update_leaderboard(self):
        leaderboard_data = self.get_leaderboard_data()
        for i, (name, score) in enumerate(leaderboard_data, 1):
            self.canvas.create_text(
                50, 80 + i * 40,
                text=f"{i}. {name} — {score}",
                font=("Arial", 14),
                fill="white",
                anchor="nw"
            )


    def get_leaderboard_data(self):
        leaderboard_data = []
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                # Ограничиваем вывод только топ-10 игроков
                cursor.execute("""
                    SELECT username, score
                    FROM (
                        SELECT username, score
                        FROM leaderboard
                        ORDER BY score DESC
                    )
                    WHERE ROWNUM <= 10
                """)
                leaderboard_data = cursor.fetchall()
        except oracledb.DatabaseError as e:
            print(f"Ошибка подключения к базе данных: {e}")
        finally:
            connection.close()
        return leaderboard_data


    def create_button(self, parent, text, command):
        button = tk.Button(
            parent,
            text=text,
            font=("Arial", 14),
            width=25,
            command=command,
            bg="#3498db",
            fg="white",
            bd=0,
            highlightthickness=0,
            activebackground="#5dade2",
            cursor="hand2"
        )
        def on_enter(e): button.config(bg="#5dade2")
        def on_leave(e): button.config(bg="#3498db")
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        return button













    def login(self):
        try:
            connection = get_db_connection()

            login_window = tk.Toplevel(self.root)
            login_window.title("Авторизация")
            width = 400
            height = 300
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = int((screen_width / 2) - (width / 2) + 130)
            y = int((screen_height / 2) - (height / 2) + 20)
            login_window.geometry(f"{width}x{height}+{x}+{y}")

            login_window.configure(bg="#271b2f")
            login_window.transient(self.root)
            login_window.grab_set()
            login_window.focus_force()
            login_window.lift()

            container = tk.Frame(login_window, bg="#271b2f")
            container.pack(expand=True, fill="both")

            inner_frame = tk.Frame(container, bg="#271b2f")
            inner_frame.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(inner_frame, text="Имя пользователя:", fg="white", bg="#271b2f", font=("Arial", 12)).pack(pady=(0, 5))
            username_entry = tk.Entry(inner_frame, font=("Arial", 12))
            username_entry.pack(pady=(0, 10), ipadx=5, ipady=2)

            tk.Label(inner_frame, text="Пароль:", fg="white", bg="#271b2f", font=("Arial", 12)).pack(pady=(0, 5))
            password_entry = tk.Entry(inner_frame, show="*", font=("Arial", 12))
            password_entry.pack(pady=(0, 20), ipadx=5, ipady=2)

            def execute_login():
                username = username_entry.get().strip()
                password = password_entry.get().strip()

                if not username or not password:
                    messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
                    return

                try:
                    with connection.cursor() as cursor:
                        cursor.callproc("LOGIN", [username, password])
                    connection.commit()

                    self.current_user = username
                    self.current_password = password
                    self.user_connection = oracledb.connect(
                        user=username,
                        password=password,
                        dsn="localhost:1521/orcl"
                    )

                    messagebox.showinfo("Успех", "Вы успешно вошли в систему!")

                    # Закрыть окно авторизации
                    login_window.destroy()

                    # Скрыть кнопки авторизации и регистрации, показать кнопки управления
                    self.show_user_controls()

                    # Показываем правила игры
                    self.show_game_rules()

                except oracledb.DatabaseError as e:
                    try:
                        error_obj, = e.args
                        raw_message = getattr(error_obj, "message", str(e))
                    except Exception:
                        raw_message = str(e)

                    raw_message = re.sub(r"ORA-\d+:\s*", "", raw_message)
                    cleaned_lines = [
                        line for line in raw_message.splitlines()
                        if "line" not in line.lower() and not line.strip().startswith("на \"")
                    ]

                    error_message = "\n".join(cleaned_lines).strip()
                    messagebox.showerror("Ошибка", error_message or "Произошла неизвестная ошибка.")

            self.create_button(inner_frame, "Войти", execute_login).pack(pady=(10, 0))
            login_window.protocol("WM_DELETE_WINDOW", lambda: [connection.close(), login_window.destroy()])

        except Exception as e:
            messagebox.showerror("Ошибка подключения", str(e))

    def show_game_rules(self):
        try:
            # Создаем переменную для хранения правил игры
            game_rules = self.user_connection.cursor().var(oracledb.CLOB)

            # Вызов процедуры, которая возвращает правила игры
            with self.user_connection.cursor() as cursor:
                cursor.callproc("REGISTER.GET_GAME_RULES", [self.current_user, game_rules])

            # Извлекаем значение из CLOB переменной
            rules = game_rules.getvalue()

            # Создаем окно с правилами
            rules_window = tk.Toplevel(self.root)
            rules_window.title("Правила игры")
            width = 650
            height = 250
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            # Вычисляем координаты для окна с правилами
            x = int((screen_width / 2) - (width / 2) + 130)
            y = int((screen_height / 2) - (height / 2) + 20)

            # Устанавливаем размеры и положение окна
            rules_window.geometry(f"{width}x{height}+{x}+{y}")

            rules_window.configure(bg="#271b2f")

            # Устанавливаем родительское окно
            rules_window.transient(self.root)
            rules_window.grab_set()
            rules_window.focus_force()
            rules_window.lift()

            container = tk.Frame(rules_window, bg="#271b2f")
            container.pack(fill="both", expand=True, padx=20, pady=20)

            rules_label = tk.Label(container, text=rules, fg="white", bg="#271b2f", font=("Arial", 12), justify="left")
            rules_label.pack(pady=10)

            close_btn = tk.Button(container, text="Закрыть", font=("Arial", 12), command=lambda: self.on_rules_closed(rules_window))
            close_btn.pack(pady=10)

            # Привязываем обработчик закрытия окна с правилами
            rules_window.protocol("WM_DELETE_WINDOW", lambda: self.on_rules_closed(rules_window))

        except oracledb.DatabaseError as e:
            messagebox.showerror("Ошибка", f"Не удалось получить правила игры: {e}")

    def on_rules_closed(self, rules_window):
        # Закрываем окно с правилами
        rules_window.destroy()
        
        # Открываем окно с выбором режима игры
        self.open_game_window()


























    def register(self):
        try:
            connection = get_db_connection()

            reg_window = tk.Toplevel(self.root)
            reg_window.title("Регистрация")
            width = 400
            height = 300
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = int((screen_width / 2) - (width / 2)+130)
            y = int((screen_height / 2) - (height / 2)+20)
            reg_window.geometry(f"{width}x{height}+{x}+{y}")

            reg_window.configure(bg="#271b2f")
            reg_window.transient(self.root)
            reg_window.grab_set()
            reg_window.focus_force()
            reg_window.lift()

            container = tk.Frame(reg_window, bg="#271b2f")
            container.pack(expand=True, fill="both", pady=20)

            tk.Label(container, text="Имя пользователя:", fg="white", bg="#271b2f", font=("Arial", 12)).pack(pady=(0, 5))
            username_entry = tk.Entry(container, font=("Arial", 12))
            username_entry.pack(pady=(0, 10), ipadx=5, ipady=2)

            tk.Label(container, text="Пароль:", fg="white", bg="#271b2f", font=("Arial", 12)).pack(pady=(0, 5))
            password_entry = tk.Entry(container, show="*", font=("Arial", 12))
            password_entry.pack(pady=(0, 10), ipadx=5, ipady=2)

            tk.Label(container, text="Повторите пароль:", fg="white", bg="#271b2f", font=("Arial", 12)).pack(pady=(0, 5))
            confirm_entry = tk.Entry(container, show="*", font=("Arial", 12))
            confirm_entry.pack(pady=(0, 20), ipadx=5, ipady=2)

            def execute_register():
                try:
                    with connection.cursor() as cursor:
                        cursor.callproc("REGISTER", [
                            username_entry.get(),
                            password_entry.get(),
                            confirm_entry.get()
                        ])
                    connection.commit()
                    messagebox.showinfo("Успех", "Регистрация завершена!")
                    reg_window.destroy()
                except oracledb.DatabaseError as e:
                    try:
                        error_obj, = e.args
                        raw_message = getattr(error_obj, "message", str(e))
                    except Exception:
                        raw_message = str(e)

                    # Удаляем префиксы ORA-xxxxx:
                    raw_message = re.sub(r"ORA-\d+:\s*", "", raw_message)

                    # Удаляем строки, содержащие трассировку или слово "line"
                    cleaned_lines = [
                        line for line in raw_message.splitlines()
                        if "line" not in line.lower() and not line.strip().startswith("на \"")
                    ]

                    error_message = "\n".join(cleaned_lines).strip()
                    messagebox.showerror("Ошибка", error_message or "Произошла неизвестная ошибка.")






            self.create_button(container, "Зарегистрироваться", execute_register).pack(pady=(10, 0))
            reg_window.protocol("WM_DELETE_WINDOW", lambda: [connection.close(), reg_window.destroy()])

        except Exception as e:
            messagebox.showerror("Ошибка подключения", str(e))

    def open_game_window(self):
        game_window = tk.Toplevel(self.root)
        game_window.title("Выберите действие")
        width = 400
        height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2)+130)
        y = int((screen_height / 2) - (height / 2)+20)
        game_window.geometry(f"{width}x{height}+{x}+{y}")

        game_window.configure(bg="#271b2f")
        game_window.transient(self.root)
        game_window.grab_set()
        game_window.focus_force()
        game_window.lift()

        container = tk.Frame(game_window, bg="#271b2f")
        container.pack(expand=True, fill="both")

        inner_frame = tk.Frame(container, bg="#271b2f")
        inner_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            inner_frame,
            text="Что вы хотите сделать?",
            fg="white",
            bg="#271b2f",
            font=("Arial", 18, "bold")
        ).pack(pady=(0, 10))

        for text, command in [
            ("Присоединиться к игре", self.join_game),
            ("Создать новую игру", self.create_game),
            ("Одиночная игра", self.start_game_with_bot)
        ]:
            self.create_button(inner_frame, text, command).pack(pady=5)

        game_window.protocol("WM_DELETE_WINDOW", lambda: game_window.destroy())





























    def join_game(self, room_name=None, password=None):
        try:
            with self.user_connection.cursor() as cursor:
                # Проверяем, не находится ли пользователь уже в этой игре
                cursor.execute("""
                    SELECT COUNT(*) FROM register.players
                    WHERE game_id = (
                        SELECT game_id FROM register.games 
                        WHERE room_name = :room_name
                    ) AND player_username = :username
                """, {'room_name': room_name, 'username': self.current_user})
                
                if cursor.fetchone()[0] > 0:
                    messagebox.showwarning("Ошибка", "Вы уже находитесь в этой игре!")
                    return
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось присоединиться: {str(e)}")
        if not self.user_connection:
            messagebox.showerror("Ошибка", "Нет подключения от имени пользователя.")
            return

        # Если room_name не передан, показываем окно выбора игры
        if room_name is None:
            self.show_game_selection_window()
            return

        try:
            with self.user_connection.cursor() as cursor:
                # Получаем информацию об игре
                cursor.execute("""
                    SELECT game_id, initial_word, max_players, password_hash 
                    FROM register.games 
                    WHERE room_name = :room_name AND status = 'waiting'
                """, {"room_name": room_name})
                game_info = cursor.fetchone()
                
                if not game_info:
                    messagebox.showerror("Ошибка", "Игра не найдена или уже началась.")
                    return
                    
                game_id, initial_word, max_players, stored_password = game_info
                
                # Проверяем пароль, если он требуется
                if stored_password and password != stored_password:
                    messagebox.showerror("Ошибка", "Неверный пароль.")
                    return
                
                # Проверяем, есть ли место в игре
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM register.players 
                    WHERE game_id = :game_id
                """, {"game_id": game_id})
                current_players = cursor.fetchone()[0]
                
                if current_players >= max_players:
                    messagebox.showerror("Ошибка", "В игре нет свободных мест.")
                    return
                
                # Добавляем игрока
                cursor.execute("""
                    INSERT INTO register.players (game_id, player_username, status, move_order)
                    VALUES (:game_id, :username, 'waiting', :move_order)
                """, {
                    "game_id": game_id,
                    "username": self.current_user,
                    "move_order": current_players + 1
                })
                
                self.user_connection.commit()
                
                messagebox.showinfo("Успех", f"Вы успешно присоединились к игре: {room_name}")
                
                # Открываем комнату ожидания
                self.show_waiting_room(game_id, room_name, max_players)
                
        except oracledb.DatabaseError as e:
            error_obj, = e.args
            messagebox.showerror("Ошибка", error_obj.message)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def show_game_selection_window(self):
        # Создаем окно для списка игр
        join_window = tk.Toplevel(self.root)
        join_window.title("Присоединиться к игре")
        join_window.geometry("600x500")
        join_window.configure(bg="#271b2f")
        join_window.transient(self.root)
        join_window.grab_set()

        container = tk.Frame(join_window, bg="#271b2f")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(container, text="Поиск по названию:", font=("Arial", 12), bg="#271b2f", fg="white").pack(anchor="w")
        search_entry = tk.Entry(container, font=("Arial", 12))
        search_entry.pack(fill="x", pady=(0, 10))

        game_listbox = tk.Listbox(container, font=("Arial", 12), height=15, width=70)
        game_listbox.pack(pady=(0, 10))

        # Функция для обновления списка игр
        def update_game_list():
            filter_text = search_entry.get().strip()

            game_listbox.delete(0, tk.END)
            try:
                with self.user_connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT room_name, current_players, max_players, turn_time_minutes, password_hash
                        FROM register.games
                        WHERE status = 'waiting'
                        AND (room_name LIKE :filter OR :filter IS NULL)
                    """, {"filter": f"%{filter_text}%" if filter_text else None})

                    games = cursor.fetchall()
                    for room, current, max_, time, password_hash in games:
                        display = f"{room} — {current}/{max_} игроков, {time} мин. на ход"
                        game_listbox.insert(tk.END, (display, room, password_hash))  # Добавляем название комнаты и хэш пароля
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить список игр: {e}")

        def on_search(*_):
            update_game_list()

        # Обновляем список игр, когда текст меняется в поиске
        search_entry.bind("<KeyRelease>", on_search)

        update_game_list()

        # Функция для обработки двойного клика по игре в списке
        def on_double_click(event):
            selected_game = game_listbox.curselection()
            if selected_game:
                game_info = game_listbox.get(selected_game[0])
                display, room_name, password_hash = game_info  # Извлекаем данные

                # Закрываем текущее окно со списком игр
                join_window.destroy()

                if not password_hash:
                    self.join_game(room_name)
                else:
                    self.prompt_for_password(room_name)

        game_listbox.bind("<Double-1>", on_double_click)

    def prompt_for_password(self, room_name):
        password_window = tk.Toplevel(self.root)
        password_window.title("Введите пароль")
        password_window.geometry("300x150")
        password_window.configure(bg="#271b2f")

        tk.Label(password_window, text="Введите пароль:", font=("Arial", 12), bg="#271b2f", fg="white").pack(anchor="w")
        password_entry = tk.Entry(password_window, font=("Arial", 12), show="*")
        password_entry.pack(fill="x", pady=(0, 10))

        def submit_password():
            password = password_entry.get()
            password_window.destroy()
            self.join_game(room_name, password)

        submit_btn = tk.Button(password_window, text="Подтвердить", font=("Arial", 12), bg="#3498db", fg="white", command=submit_password)
        submit_btn.pack(pady=(10, 0))






















    



    def create_game(self):
        if self.user_connection:
            try:
                window = tk.Toplevel(self.root)
                window.title("Создание игры")
                window.geometry("400x450")
                window.configure(bg="#271b2f")
                window.transient(self.root)
                window.grab_set()
                window.focus_force()
                window.lift()

                container = tk.Frame(window, bg="#271b2f")
                container.pack(expand=True, fill="both", padx=20, pady=20)

                tk.Label(container, text="Название комнаты:", fg="white", bg="#271b2f", font=("Arial", 12)).pack(anchor="w")
                room_name_entry = tk.Entry(container, font=("Arial", 12))
                room_name_entry.pack(fill="x", pady=(0, 10))

                tk.Label(container, text="Количество игроков:", fg="white", bg="#271b2f", font=("Arial", 12)).pack(anchor="w")
                player_count_spinbox = tk.Spinbox(container, from_=2, to=4, font=("Arial", 12), width=5)
                player_count_spinbox.pack(pady=(0, 10), fill="x")

                tk.Label(container, text="Время на ход (мин):", fg="white", bg="#271b2f", font=("Arial", 12)).pack(anchor="w")
                turn_time_spinbox = tk.Spinbox(container, from_=1, to=5, font=("Arial", 12), width=5)
                turn_time_spinbox.pack(pady=(0, 10), fill="x")

                use_password_var = tk.BooleanVar()
                use_password_check = tk.Checkbutton(
                    container, text="Использовать пароль", variable=use_password_var,
                    bg="#271b2f", fg="white", font=("Arial", 12), selectcolor="#271b2f",
                    activebackground="#271b2f", activeforeground="white"
                )
                use_password_check.pack(anchor="w", pady=(10, 0))

                password_entry = tk.Entry(container, font=("Arial", 12), show="*")

                def toggle_password():
                    if use_password_var.get():
                        password_entry.pack(pady=(0, 10), fill="x", before=create_btn)
                    else:
                        password_entry.pack_forget()

                use_password_var.trace_add("write", lambda *args: toggle_password())

                def submit_create_game():
                    room_name = room_name_entry.get().strip()
                    player_count = player_count_spinbox.get()
                    turn_time = turn_time_spinbox.get()
                    password = password_entry.get().strip() if use_password_var.get() else None
                    is_vs_bot = 0

                    if not room_name:
                        messagebox.showerror("Ошибка", "Название комнаты не может быть пустым.")
                        return

                    try:
                        # Вызываем процедуру с выходным параметром
                        with self.user_connection.cursor() as cursor:
                            result_var = cursor.var(int)
                            cursor.callproc("REGISTER.CREATE_GAME", [
                                self.current_user, room_name,
                                int(player_count), password,
                                int(turn_time), is_vs_bot,
                                result_var
                            ])
                            
                            result = result_var.getvalue()
                            if result == 0:
                                messagebox.showerror("Ошибка", "Игра с таким названием уже существует")
                                return
                            elif result == -1:
                                raise Exception("Неизвестная ошибка при создании игры")
                            
                            # Получаем game_id созданной игры
                            cursor.execute("""
                                SELECT game_id FROM register.games 
                                WHERE room_name = :room_name
                            """, {'room_name': room_name})
                            game_id = cursor.fetchone()[0]
                            
                            messagebox.showinfo("Успех", "Игра успешно создана!")
                            window.destroy()
                            self.show_waiting_room(game_id, room_name, int(player_count))

                    except oracledb.DatabaseError as e:
                        error_obj, = e.args
                        messagebox.showerror("Ошибка", error_obj.message)
                    except Exception as e:
                        messagebox.showerror("Ошибка", str(e))

                create_btn = self.create_button(container, "Создать игру", submit_create_game)
                create_btn.pack(pady=(20, 10))

            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        else:
            messagebox.showerror("Ошибка", "Нет подключения от имени пользователя.")





    def show_waiting_room(self, game_id, room_name, max_players):
        waiting_window = tk.Toplevel(self.root)
        waiting_window.title(f"Комната: {room_name}")
        waiting_window.geometry("500x400")
        waiting_window.configure(bg="#271b2f")
        waiting_window.resizable(False, False)
        
        # Функция для полного выхода из комнаты
        def complete_exit():
            try:
                with self.user_connection.cursor() as cursor:
                    # 1. Удаляем текущего игрока
                    cursor.execute("""
                        DELETE FROM register.players 
                        WHERE game_id = :game_id AND player_username = :username
                    """, {'game_id': game_id, 'username': self.current_user})
                    
                    # 2. Проверяем, остались ли игроки
                    cursor.execute("""
                        SELECT COUNT(*) FROM register.players 
                        WHERE game_id = :game_id
                    """, {'game_id': game_id})
                    players_left = cursor.fetchone()[0]
                    
                    # 3. Если игроков не осталось - удаляем саму игру
                    if players_left == 0:
                        cursor.execute("""
                            DELETE FROM register.games 
                            WHERE game_id = :game_id AND status = 'waiting'
                        """, {'game_id': game_id})
                    
                    self.user_connection.commit()
                    
            except Exception as e:
                print(f"Ошибка при выходе из комнаты: {e}")
            finally:
                waiting_window.destroy()
        
        # Обработчик закрытия окна
        def on_closing():
            if messagebox.askokcancel("Подтверждение", "Вы действительно хотите покинуть комнату?"):
                complete_exit()
        
        waiting_window.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Основной контейнер
        container = tk.Frame(waiting_window, bg="#271b2f")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        # Заголовок с названием комнаты
        header_frame = tk.Frame(container, bg="#271b2f")
        header_frame.pack(fill="x", pady=(0, 15))
        tk.Label(header_frame, 
                text=f"Комната: {room_name}", 
                fg="#f39c12", bg="#271b2f", 
                font=("Arial", 14, "bold")).pack()

        # Блок со списком игроков
        players_frame = tk.Frame(container, bg="#271b2f")
        players_frame.pack(fill="x", pady=(0, 20))
        
        # Создаем переменную для заголовка
        players_label = tk.Label(players_frame, 
                text="Игроки (0/0):",  # Временно, будет обновлено
                fg="white", bg="#271b2f", 
                font=("Arial", 12))
        players_label.pack(anchor="w")
        
        # Список игроков
        players_listbox = tk.Listbox(players_frame, 
                                font=("Arial", 12), 
                                height=5, 
                                width=40, 
                                bg="#3d3242", 
                                fg="white",
                                selectbackground="#f39c12")
        players_listbox.pack(fill="x", pady=(5, 0))

        # Блок с кнопками
        buttons_frame = tk.Frame(container, bg="#271b2f")
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Кнопка начала игры (только для создателя)
        start_btn = tk.Button(buttons_frame,
                            text="Начать игру",
                            font=("Arial", 12),
                            bg="#3498db",
                            fg="white",
                            state="disabled",
                            command=lambda: self.start_game(game_id))
        start_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        # Кнопка выхода
        leave_btn = tk.Button(buttons_frame,
                            text="Покинуть комнату",
                            font=("Arial", 12),
                            bg="#e74c3c",
                            fg="white",
                            command=on_closing)
        leave_btn.pack(side="right", fill="x", expand=True)

        # Функция обновления списка игроков
        def update_players_list():
            try:
                players = self.get_players_in_room(game_id)
                players_listbox.delete(0, tk.END)
                
                for player in players:
                    players_listbox.insert(tk.END, player)
                
                # Обновляем заголовок
                players_label.config(text=f"Игроки ({len(players)}/{max_players}):")
                
                # Проверяем, является ли текущий пользователь создателем
                is_owner = self.is_room_owner(game_id, self.current_user)
                if is_owner:
                    start_btn.config(state="normal" if len(players) >= max_players else "disabled")
                else:
                    start_btn.pack_forget()
                
            except Exception as e:
                print(f"Ошибка обновления списка: {e}")
            finally:
                waiting_window.after(2000, update_players_list)

        # Первоначальное обновление (вынесено из функции)
        update_players_list()


# Вспомогательные методы (добавьте их в класс):
    def get_players_in_room(self, game_id):
        with self.user_connection.cursor() as cursor:
            cursor.execute("""
                SELECT player_username FROM register.players 
                WHERE game_id = :game_id ORDER BY move_order
            """, {'game_id': game_id})
            return [row[0] for row in cursor.fetchall()]
        
    def is_room_owner(self, game_id, username):
        with self.user_connection.cursor() as cursor:
            cursor.execute("""
                SELECT owner_username FROM register.games 
                WHERE game_id = :game_id
            """, {'game_id': game_id})
            result = cursor.fetchone()
            return result and result[0] == username















    def leave_game(self, window, game_id):
        try:
            with self.user_connection.cursor() as cursor:
                # Удаляем игрока
                cursor.execute("""
                    DELETE FROM register.players 
                    WHERE game_id = :game_id AND player_username = :username
                """, {'game_id': game_id, 'username': self.current_user})
                
                # Проверяем оставшихся игроков
                cursor.execute("""
                    SELECT COUNT(*) FROM register.players 
                    WHERE game_id = :game_id
                """, {'game_id': game_id})
                players_left = cursor.fetchone()[0]
                
                # Если игроков не осталось, удаляем игру
                if players_left == 0:
                    cursor.execute("""
                        DELETE FROM register.games 
                        WHERE game_id = :game_id
                    """, {'game_id': game_id})
                
                self.user_connection.commit()
                window.destroy()
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось покинуть комнату: {str(e)}")

    def start_game(self, game_id):
        try:
            with self.user_connection.cursor() as cursor:
                # Проверяем, является ли пользователь создателем игры
                cursor.execute("""
                    SELECT owner_username 
                    FROM register.games 
                    WHERE game_id = :game_id
                """, {'game_id': game_id})
                owner = cursor.fetchone()[0]
                
                if owner != self.current_user:
                    messagebox.showerror("Ошибка", "Только создатель комнаты может начать игру.")
                    return
                
                # Проверяем, что комната заполнена
                cursor.execute("""
                    SELECT COUNT(*), max_players 
                    FROM register.players p
                    JOIN register.games g ON p.game_id = g.game_id
                    WHERE p.game_id = :game_id
                    GROUP BY max_players
                """, {'game_id': game_id})
                result = cursor.fetchone()
                
                if not result or result[0] < result[1]:
                    messagebox.showerror("Ошибка", "Комната не заполнена!")
                    return
                
                # Обновляем статус игры на "в процессе"
                cursor.execute("""
                    UPDATE register.games 
                    SET status = 'in_progress' 
                    WHERE game_id = :game_id
                """, {'game_id': game_id})
                
                # Обновляем статус игроков на "playing"
                cursor.execute("""
                    UPDATE register.players 
                    SET status = 'playing' 
                    WHERE game_id = :game_id
                """, {'game_id': game_id})
                
                self.user_connection.commit()
                
                # Закрываем окно ожидания и открываем игровое поле
                # (эту функцию вам нужно будет реализовать)
                self.show_game_field(game_id)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось начать игру: {str(e)}")








    def start_game_with_bot(self):
        if self.user_connection:
            try:
                with self.user_connection.cursor() as cursor:
                    print(f"Пользователь {self.current_user} начал игру с ботом.")
            except oracledb.DatabaseError as e:
                messagebox.showerror("Ошибка", str(e))








if __name__ == "__main__":
    root = ctk.CTk()

    window_width = 1200
    window_height = 675
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    app = GameApp(root)
    root.mainloop()

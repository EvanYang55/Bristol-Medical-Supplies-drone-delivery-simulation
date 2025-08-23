import tkinter as tk
from tkinter import ttk, messagebox


class PathPlannerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Medical Resource Path Planning System")
        self.root.geometry("900x700")  # Reduced window size
        self.root.resizable(True, True)

        # Initialize return values
        self.submitted = False
        self.selected_targets = []
        self.selected_tasks = []
        self.selected_strategy = []
        self.selected_charge_strategy = []  # 新增充电策略选择
        self.temperature = 25.0  # 默认温度值

        # Create styles with larger fonts
        self.style = ttk.Style()
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#e0f0ff', foreground='#0066cc')
        self.style.configure('Section.TFrame', background='#f0f8ff', relief=tk.RAISED, borderwidth=1)
        self.style.configure('Section.TLabel', font=('Arial', 12, 'bold'), background='#f0f8ff', foreground='#336699')
        self.style.configure('Check.TCheckbutton', background='#f0f8ff', font=('Arial', 10))
        self.style.configure('Radio.TRadiobutton', background='#f0f8ff', font=('Arial', 10))
        self.style.configure('Input.TLabel', font=('Arial', 9), background='#f0f8ff', foreground='#444444')

        # Configure scale style correctly
        self.style.configure('Horizontal.TScale', troughcolor='#c0d0e0')

        # Update button style: green background with BLACK text
        self.style.configure('Submit.TButton', font=('Arial', 12, 'bold'),
                             background='#4CAF50', foreground='black')
        self.style.configure('Instruction.TLabel', font=('Arial', 9), foreground="#666666")
        self.style.configure('Footer.TLabel', font=('Arial', 8), foreground="#999999")

        # Initialize weight variables
        self.target_weight_vars = {}  # {target_id: weight_var}
        self.task_weight_vars = {}  # {task_id: weight_var}

        self.create_widgets()

    def create_widgets(self):
        # Create main container with scrollbar
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)

        # Create a canvas for scrolling
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Title with larger font
        title = ttk.Label(self.scrollable_frame,
                          text="Medical Resource Path Planning System",
                          style='Title.TLabel')
        title.pack(fill=tk.X, pady=(10, 15))

        # Target selection section with weight sliders
        self.create_target_section()

        # Task points selection section with weight sliders
        self.create_task_section()

        # Path strategy selection section
        self.create_strategy_section()

        # Charge strategy selection section (新增部分)
        self.create_charge_strategy_section()

        # Temperature selection section
        self.create_temperature_section()

        # Button section
        self.create_button_section()

        # Footer with program version
        footer = ttk.Label(self.scrollable_frame,
                           text="Medical Resource Path Planning System v2.0 | Payload Weight Sliders & Temperature Setting",
                           style='Footer.TLabel')
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 5))

    def create_target_section(self):
        target_frame = ttk.LabelFrame(self.scrollable_frame,
                                      text="Select Target Locations (Multiple Choice) with Payload Weights",
                                      style='Section.TFrame')
        target_frame.pack(fill=tk.X, padx=10, pady=5, ipadx=10, ipady=10)

        self.target_vars = {}
        targets = {
            1: "NHS Blood Centre (Filton)",
            2: "South Bristol NHS Community Hospital",
            3: "UWE Health Tech Hub"
        }

        # Create columns for targets
        columns_frame = ttk.Frame(target_frame)
        columns_frame.pack(fill=tk.BOTH, expand=True)

        for key, value in targets.items():
            target_item_frame = ttk.Frame(columns_frame, padding="5")
            target_item_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)

            # Checkbox for target selection
            var = tk.BooleanVar(value=False)
            self.target_vars[key] = var
            cb = ttk.Checkbutton(target_item_frame,
                                 text=value,
                                 variable=var,
                                 style='Check.TCheckbutton')
            cb.pack(anchor='w', pady=(0, 5))

            # Payload weight slider
            slider_frame = ttk.Frame(target_item_frame)
            slider_frame.pack(fill=tk.X, pady=(0, 5))

            weight_label = ttk.Label(slider_frame,
                                     text="Payload Weight (kg):",
                                     style='Input.TLabel')
            weight_label.pack(side=tk.LEFT)

            # Weight slider (0-15.06kg)
            weight_var = tk.DoubleVar(value=0.0)
            self.target_weight_vars[key] = weight_var

            weight_slider = ttk.Scale(slider_frame,
                                      from_=0,
                                      to=15.06,
                                      variable=weight_var,
                                      orient=tk.HORIZONTAL,
                                      style='Horizontal.TScale',
                                      length=150)
            weight_slider.pack(side=tk.LEFT, padx=(5, 0))

            # Display current value
            value_label = ttk.Label(slider_frame,
                                    text=f"{weight_var.get():.2f} kg",
                                    style='Input.TLabel')
            value_label.pack(side=tk.LEFT, padx=5)

            # Update value display when slider moves
            def update_label(val, lbl=value_label):
                lbl.config(text=f"{float(val):.2f} kg")

            weight_slider.config(command=update_label)

    def create_task_section(self):
        task_frame = ttk.LabelFrame(self.scrollable_frame,
                                    text="Select Task Points (Multiple Choice) with Payload Weights",
                                    style='Section.TFrame')
        task_frame.pack(fill=tk.X, padx=10, pady=5, ipadx=10, ipady=10)

        self.task_vars = {}
        tasks = {
            1: "Southmead Hospital",
            2: "Bristol Royal Infirmary (BRI)",
            3: "St Michael's Hospital",
            4: "Eastville Medical Centre",
            5: "Fishponds Primary Care Centre",
            6: "Bristol Haematology and Oncology Centre (BHOC)",
            7: "Emersons Green NHS Treatment Centre",
            8: "Lawrence Hill Health Centre",
            9: "Montpelier Health Centre"
        }

        # Create columns for tasks
        columns_frame = ttk.Frame(task_frame)
        columns_frame.pack(fill=tk.BOTH, expand=True)

        # Create 3 columns
        columns = []
        for i in range(3):
            col_frame = ttk.Frame(columns_frame)
            col_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            columns.append(col_frame)

        # Add tasks to columns
        for idx, (key, value) in enumerate(tasks.items()):
            col_idx = idx % 3
            col_frame = columns[col_idx]

            # Frame for each task
            task_item_frame = ttk.Frame(col_frame, padding="5")
            task_item_frame.pack(fill=tk.X, pady=2)

            # Checkbox for task selection
            var = tk.BooleanVar(value=False)
            self.task_vars[key] = var
            cb = ttk.Checkbutton(task_item_frame,
                                 text=f"{key}: {value}",
                                 variable=var,
                                 style='Check.TCheckbutton')
            cb.pack(anchor='w')

            # Payload weight slider
            slider_frame = ttk.Frame(task_item_frame)
            slider_frame.pack(fill=tk.X, padx=(10, 0), pady=(2, 0))

            weight_label = ttk.Label(slider_frame,
                                     text="Weight (kg):",
                                     style='Input.TLabel')
            weight_label.pack(side=tk.LEFT, padx=(0, 5))

            # Weight slider (0-15.06kg)
            weight_var = tk.DoubleVar(value=0.0)
            self.task_weight_vars[key] = weight_var

            weight_slider = ttk.Scale(slider_frame,
                                      from_=0,
                                      to=15.06,
                                      variable=weight_var,
                                      orient=tk.HORIZONTAL,
                                      style='Horizontal.TScale',
                                      length=120)
            weight_slider.pack(side=tk.LEFT, padx=(0, 5))

            # Display current value
            value_label = ttk.Label(slider_frame,
                                    text=f"{weight_var.get():.2f} kg",
                                    style='Input.TLabel')
            value_label.pack(side=tk.LEFT)

            # Update value display when slider moves
            def update_label(val, lbl=value_label):
                lbl.config(text=f"{float(val):.2f} kg")

            weight_slider.config(command=update_label)

    def create_strategy_section(self):
        strategy_frame = ttk.LabelFrame(self.scrollable_frame,
                                        text="Select Path Optimization Strategy (Single Choice)",
                                        style='Section.TFrame')
        strategy_frame.pack(fill=tk.X, padx=10, pady=5, ipadx=10, ipady=10)

        self.strategy_var = tk.IntVar(value=1)

        strategies = {
            1: "A* Path Planning Algorithm",
            2: "Dijkstra Algorithm"
        }

        # Strategy options
        strategy_cols = ttk.Frame(strategy_frame)
        strategy_cols.pack(fill=tk.X, expand=True, padx=10, pady=5)

        for i, (key, value) in enumerate(strategies.items()):
            # Create a frame for each strategy option
            strategy_item_frame = ttk.Frame(strategy_cols)
            strategy_item_frame.pack(side=tk.LEFT, expand=True, padx=5, pady=5)

            # Add the radio button
            rb = ttk.Radiobutton(strategy_item_frame,
                                 text=value,
                                 variable=self.strategy_var,
                                 value=key,
                                 style='Radio.TRadiobutton')
            rb.pack(anchor='w')

    def create_charge_strategy_section(self):
        """新增充电策略选择部分"""
        charge_frame = ttk.LabelFrame(self.scrollable_frame,
                                      text="Select Charge Solution (Single Choice)",
                                      style='Section.TFrame')
        charge_frame.pack(fill=tk.X, padx=10, pady=5, ipadx=10, ipady=10)

        self.charge_strategy_var = tk.IntVar(value=1)

        charge_strategies = {
            1: "Strategy A: Return to charge after each mission, then depart with a full battery.",
            2: "Strategy B: Return to charge after completing two missions, then depart with a full battery."
        }

        # 充电策略选项
        charge_cols = ttk.Frame(charge_frame)
        charge_cols.pack(fill=tk.X, expand=True, padx=10, pady=5)

        # 创建单选按钮
        for key, value in charge_strategies.items():
            # 创建框架
            charge_item_frame = ttk.Frame(charge_cols)
            charge_item_frame.pack(fill=tk.X, pady=5, padx=5)

            # 添加单选按钮
            rb = ttk.Radiobutton(charge_item_frame,
                                 text=value,
                                 variable=self.charge_strategy_var,
                                 value=key,
                                 style='Radio.TRadiobutton')
            rb.pack(anchor='w')

    def create_temperature_section(self):
        """创建温度选择部分"""
        temp_frame = ttk.LabelFrame(self.scrollable_frame,
                                    text="Environment Temperature Setting (°C)",
                                    style='Section.TFrame')
        temp_frame.pack(fill=tk.X, padx=10, pady=5, ipadx=10, ipady=10)

        # 创建主框架
        main_frame = ttk.Frame(temp_frame)
        main_frame.pack(fill=tk.X, padx=10, pady=10)

        # 温度说明标签
        explanation = ttk.Label(main_frame,
                                text="Set environment temperature for battery performance calculation (0°C to 50°C):",
                                style='Input.TLabel')
        explanation.pack(anchor='w', pady=(0, 10))

        # 创建滑动条框架
        slider_frame = ttk.Frame(main_frame)
        slider_frame.pack(fill=tk.X)

        # 最小值标签
        min_label = ttk.Label(slider_frame, text="0°C", style='Input.TLabel')
        min_label.pack(side=tk.LEFT, padx=(0, 10))

        # 温度滑动条 (0-50°C)
        self.temperature_var = tk.DoubleVar(value=self.temperature)
        temp_slider = ttk.Scale(slider_frame,
                                from_=0,
                                to=50,
                                variable=self.temperature_var,
                                orient=tk.HORIZONTAL,
                                style='Horizontal.TScale',
                                length=300)
        temp_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 最大值标签
        max_label = ttk.Label(slider_frame, text="50°C", style='Input.TLabel')
        max_label.pack(side=tk.LEFT, padx=(10, 0))

        # 当前值显示框架
        value_frame = ttk.Frame(main_frame)
        value_frame.pack(fill=tk.X, pady=(10, 0))

        value_label = ttk.Label(value_frame,
                                text=f"Current Temperature: {self.temperature_var.get():.1f}°C",
                                font=('Arial', 10, 'bold'),
                                foreground='#336699')
        value_label.pack()

        # 更新显示值
        def update_temp(val):
            temp = float(val)
            self.temperature = temp
            value_label.config(text=f"Current Temperature: {temp:.1f}°C")

        temp_slider.config(command=update_temp)

    def create_button_section(self):
        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 5))

        # Submit button with larger font and BLACK text
        submit_btn = ttk.Button(button_frame,
                                text="Run Path Planning",
                                command=self.submit,
                                style='Submit.TButton')
        submit_btn.pack(side=tk.TOP, padx=20, pady=10, ipadx=20, ipady=5)

        # Instructions
        instructions = ttk.Label(button_frame,
                                 text="Note: Select target locations and multiple task points. Adjust payload weights using sliders.",
                                 style='Instruction.TLabel')
        instructions.pack(side=tk.TOP, pady=(5, 0))

    def submit(self):
        # Process selected targets and weights
        self.selected_targets = []
        for target_id, var in self.target_vars.items():
            if var.get():
                weight = round(self.target_weight_vars[target_id].get(), 2)
                self.selected_targets.append((target_id, weight))

        if not self.selected_targets:
            messagebox.showwarning("Input Error", "Please select at least one target location")
            return

        # Process selected tasks and weights
        self.selected_tasks = []
        for task_id, var in self.task_vars.items():
            if var.get():
                weight = round(self.task_weight_vars[task_id].get(), 2)
                self.selected_tasks.append((task_id, weight))

        if not self.selected_tasks:
            messagebox.showwarning("Input Error", "Please select at least one task point")
            return

        # Process selected strategy
        self.selected_strategy = [self.strategy_var.get()]

        # Process selected charge strategy (新增部分)
        self.selected_charge_strategy = [self.charge_strategy_var.get()]

        # 获取温度值
        self.temperature = round(self.temperature_var.get(), 1)

        # Set submitted flag and close window
        self.submitted = True
        self.root.destroy()

    def run(self):
        self.root.mainloop()
        return self.submitted, self.selected_targets, self.selected_tasks, self.selected_strategy, self.selected_charge_strategy, self.temperature


def interactive_path_planner():
    app = PathPlannerApp()
    submitted, targets, tasks, strategy, charge_strategy, temperature = app.run()

    if submitted:
        # Return the required values with temperature
        return (targets, tasks, strategy, charge_strategy, temperature)
    else:
        # User closed the window without submitting
        return ([], [], [], [], 25.0)  # 返回默认温度值


# For testing
if __name__ == "__main__":
    result = interactive_path_planner()
    if result:
        targets, tasks, strategy, charge_strategy, temperature = result
        print("Return Value 1 (Targets with Weights):", targets)
        print("Return Value 2 (Tasks with Weights):", tasks)
        print("Return Value 3 (Strategy):", strategy)
        print("Return Value 4 (Charge Strategy):", charge_strategy)
        print("Return Value 5 (Temperature):", temperature, "°C")
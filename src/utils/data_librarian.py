import os
import pandas as pd

class DataLibrarian:
    def __init__(self, params):
        self.params = params
        self.cur_dir = self.get_project_root()
        self.result_dir = os.path.join(self.cur_dir, "data", "results")

        # パラメータセットのディレクトリ
        set_dir_name = params["param set"]
        self.set_dir = os.path.join(self.result_dir, set_dir_name)
        os.makedirs(self.set_dir, exist_ok=True)

        # モデル名のディレクトリ
        self.model_name = self.params['model']
        self.model_dir = os.path.join(self.set_dir, self.model_name)
        os.makedirs(self.model_dir, exist_ok=True)

        if self.model_name in ['fem', 'rk4', 'ode45']:
            self._setup_ode_simulation()
        elif self.model_name in ['SynCA', 'ErCA']:
            self._setup_ca_simulation()

    def _setup_ode_simulation(self):
        """ODE 系のシミュレーションディレクトリを作成"""
        self.simulation_dir = os.path.join(self.model_dir, 'simulation')
        os.makedirs(self.simulation_dir, exist_ok=True)

        # 結果の保存用ファイルパス
        base_filename = self.get_filename()
        self.save_path = self.get_filename_with_suffix(base_filename, self.simulation_dir)

    def _setup_ca_simulation(self):
        """CA 系の条件ごとのディレクトリを管理"""
        self.condition_dir = self.get_ca_condition_dir()
        os.makedirs(self.condition_dir, exist_ok=True)

        self.simulation_dir = os.path.join(self.condition_dir, 'simulation')
        os.makedirs(self.simulation_dir, exist_ok=True)

        # 結果の保存用ファイルパス
        base_filename = self.get_filename()
        self.save_path = self.get_filename_with_suffix(base_filename, self.simulation_dir)

    def get_project_root(self):
        """プロジェクトルートディレクトリを取得"""
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.abspath(os.path.join(cur_dir, "..", ".."))

    def get_ca_condition_dir(self):
        """
        CA パラメータごとに一意の 'condition_{i}' ディレクトリを生成
        """
        ca_params_keys = ['N', 'M', 's1', 's2', 'gamma_X', 'gamma_Y',
                          'Tc', 'Tx_rat', 'Tx_sqrt', 'Ty_rat', 'Ty_sqrt']
        ca_params = {key: self.params.get(key) for key in ca_params_keys}

        existing_conditions = [d for d in os.listdir(self.model_dir) if d.startswith('condition_')]

        for cond in existing_conditions:
            cond_dir = os.path.join(self.model_dir, cond)
            params_file = os.path.join(cond_dir, 'params.csv')

            if os.path.exists(params_file):
                try:
                    existing_params = pd.read_csv(params_file, index_col=0, header=None).to_dict()
                    if self.compare_params(existing_params, ca_params):
                        print(f"Reusing existing directory: {cond_dir}")
                        return cond_dir
                except Exception as e:
                    print(f"Warning: Failed to read params.csv in {cond_dir}: {e}")

        # 新しい条件のディレクトリを作成
        next_index = len(existing_conditions) + 1
        condition_name = f'condition_{next_index}'
        condition_dir = os.path.join(self.model_dir, condition_name)

        # 必要なディレクトリを作成
        os.makedirs(condition_dir, exist_ok=True)

        # パラメータを保存
        params_file = os.path.join(condition_dir, 'params.csv')
        try:
            pd.DataFrame.from_dict(ca_params, orient='index').to_csv(params_file, header=False)
            print(f"Saved params.csv in {condition_dir}")
        except Exception as e:
            print(f"Error saving params.csv in {condition_dir}: {e}")

        return condition_dir

    def compare_params(self, existing_params, new_params):
        """既存のパラメータと新しいパラメータを比較"""
        for key in new_params.keys():
            if key not in existing_params:
                return False
            if str(existing_params[key]) != str(new_params[key]):  # 型を文字列に統一して比較
                return False
        return True

    def get_filename(self):
        """シミュレーションタイプとパラメータに基づいてファイル名を決定"""
        simulation_type = self.params.get('simulation')
        set_number = self.params.get('param set', 1)
        Q = self.params.get('Q', '')
        S = self.params.get('S', '')

        if simulation_type == 'bif':
            return f'bif_set{set_number}_Q{Q}.csv'
        elif simulation_type == 'attraction basin':
            return f'ab_set{set_number}_Q{Q}_S{S}.csv'
        elif simulation_type:
            return f'simulation_{set_number}.csv'
        else:
            raise ValueError("Unknown simulation type in params.")

    def get_filename_with_suffix(self, base_filename, directory):
        """同名ファイルが存在する場合に添え字を付加"""
        filename = base_filename
        file_path = os.path.join(directory, filename)
        suffix = 1

        while os.path.exists(file_path):
            filename = f"{os.path.splitext(base_filename)[0]}_{suffix}.csv"
            file_path = os.path.join(directory, filename)
            suffix += 1

        return file_path

    def save_data(self, data):
        """データを保存"""
        try:
            data.to_csv(self.save_path, index=False)
            print(f"Data saved to {self.save_path}")
        except Exception as e:
            print(f"Error saving data to {self.save_path}: {e}")

        params_file = os.path.join(self.simulation_type_dir, 'params.csv')
        try:
            pd.DataFrame.from_dict(self.params, orient='index').to_csv(params_file, header=False)
            print(f"Params saved to {params_file}")
        except Exception as e:
            print(f"Error saving params to {params_file}: {e}")

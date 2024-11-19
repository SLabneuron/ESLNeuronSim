import os
import pandas as pd

class DataLibrarian:

    def __init__(self, params):
        self.params = params
        self.cur_dir = self.get_project_root()
        self.result_dir = os.path.join(self.cur_dir, "data", "results")

        # get param set
        set_dir_name = params["param set"]
        self.set_dir = os.path.join(self.result_dir, set_dir_name)
        os.makedirs(self.set_dir, exist_ok=True)

        # get model name
        self.model_name = self.params['model']
        self.model_dir = os.path.join(self.set_dir, self.model_name)
        os.makedirs(self.model_dir, exist_ok=True)

        # file organization for ode
        if self.model_name in ['fem', 'rk4', 'ode45']:

            # create simulation directory
            self.simulation_dir = os.path.join(self.model_dir, 'simulation')
            os.makedirs(self.simulation_dir, exist_ok=True)

            # get simulation type
            self.simulation_type = self.params["simulation"]
            self.simulation_type_dir = os.path.join(self.simulation_dir, self.simulation_type)
            os.makedirs(self.simulation_type_dir, exist_ok=True)

            # save file
            self.save_filename = self.get_filename()
            self.save_path = os.path.join(self.simulation_type_dir, self.save_filename)

        elif self.model_name in ['SynCA', 'ErCA']:
            # create ca results file
            self.condition_dir = self.get_ca_condition_dir()
            os.makedirs(self.condition_dir, exist_ok=True)

            # create simulation direcctory
            self.simulation_dir = os.path.join(self.condition_dir, 'simulation')
            os.makedirs(self.simulation_dir, exist_ok=True)

            # get simulation type
            self.simulation_type = self.params["simulation"]
            self.simulation_type_dir = os.path.join(self.simulation_dir, self.simulation_type)
            os.makedirs(self.simulation_type_dir, exist_ok=True)

            # savefile
            self.save_filename = self.get_filename()
            self.save_path = os.path.join(self.simulation_type_dir, self.save_filename)
        else:
            print("Error")


    def get_project_root(self):

         # get current dir
        cur_dir = os.path.dirname(os.path.abspath(__file__))

        # up to root dir
        project_root = os.path.abspath(os.path.join(cur_dir, "..", ".."))

        return project_root


    def get_ca_condition_dir(self):
        """
        CA パラメータごとに一意の 'condition_{i}' ディレクトリを生成します。
        """
        # 定義された CA パラメータのキー
        ca_params_keys = ['N', 'M', 's1', 's2', 'gamma_X', 'gamma_Y',
                        'Tc', 'Tx_rat', 'Tx_sqrt', 'Ty_rat', 'Ty_sqrt']

        # 現在の CA パラメータを取得
        ca_params = {key: self.params.get(key) for key in ca_params_keys}

        # 既存の 'condition_{i}' ディレクトリを確認
        existing_conditions = [d for d in os.listdir(self.model_dir) if d.startswith('condition_')]

        # 既存の条件と比較
        for cond in existing_conditions:
            cond_dir = os.path.join(self.model_dir, cond)
            params_file = os.path.join(cond_dir, 'params.csv')

            if os.path.exists(params_file):
                try:
                    existing_params = pd.read_csv(params_file, index_col=0, header=None, squeeze=True).to_dict()
                    if self.compare_params(existing_params, ca_params):
                        return cond_dir  # 同じパラメータのディレクトリが見つかった
                except Exception as e:
                    print(f"Error reading params.csv in {cond_dir}: {e}")

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
        except Exception as e:
            print(f"Error saving params.csv in {condition_dir}: {e}")

        return condition_dir

    def compare_params(self, existing_params, new_params):
        """
        既存のパラメータと新しいパラメータを比較します。
        """

        return existing_params == new_params

    def get_filename(self):
        """
        シミュレーションタイプとパラメータに基づいてファイル名を決定します。
        """
        simulation_type = self.params.get('simulation_type')
        set_number = self.params.get('param set', 1)
        Q = self.params.get('Q', '')
        S = self.params.get('S', '')

        if simulation_type == 'bif':
            filename = f'bif_set{set_number}_Q{Q}.csv'
        elif simulation_type == 'attraction basin':
            filename = f'ab_set{set_number}_Q{Q}_S{S}.csv'
        else:
            filename = f'simulation_set{set_number}.csv'

        return filename

    def save_data(self, data):
        """
        データを保存します。
        """
        # データを保存
        try:
            data.to_csv(self.save_path, index=False)
            print(f"Data saved to {self.save_path}")
        except Exception as e:
            print(f"Error saving data to {self.save_path}: {e}")

        # パラメータを保存
        params_file = os.path.join(self.simulation_type_dir, 'params.csv')
        try:
            pd.DataFrame.from_dict(self.params, orient='index').to_csv(params_file, header=False)
            print(f"Params saved to {params_file}")
        except Exception as e:
            print(f"Error saving params to {params_file}: {e}")

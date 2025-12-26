# -*- coding: utf-8 -*-
"""
Created on: 2024-11-25
Updated on: 2024-11-25

@author: shirafujilab

Construction:

    results
        |
        |- set 1, set 2, set 3, set 4
            |
            |- fem, rk4, ode45
                |
                |
                |-results
                        |
                        |-------- 2-para bif (parameter region), 1-para bif, atraction basin, return map
            |
            |
            |- ErCA, SynCA
                |
                |- condition_1, condition_2, ...
                        |
                        |--------- 2-para bif (parameter region), 1-para bif, atraction basin, return map
        |
        |- data_lib.json


"""

import os
import pandas as pd
import json
import datetime



class DataLibrarian:
    def __init__(self, params):

        # get parameter
        self.params = params

        self.set_dir_and_jname()
        self.set_result_path()

    def set_dir_and_jname(self):

        # get results dir
        self.get_results_dir()

        # get param set dir (set 1, set 2, set 3, set 4)
        self.get_param_set_dir()

        # get model dir (ode, ..., ErCA, SynCA)
        self.get_model_dir()

        # get detailed dir (for each ca parameter and ode pass)
        self.get_detailed_dir()

        # get simulation dir
        self.get_sim_type()

    def get_results_dir(self):

        """get project root directory """

        # get root dir
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.abspath(os.path.join(cur_dir, "..", ".."))

        # return dir
        self.result_dir = os.path.join(root_dir, "data", "results")
        os.makedirs(self.result_dir, exist_ok=True)

    def get_param_set_dir(self):

        """ get param set directory """

        # get select param set
        param_set = self.params["param set"]

        # return dir
        self.set_dir = os.path.join(self.result_dir, param_set)
        os.makedirs(self.set_dir, exist_ok=True)

        # return name
        self.set_jname = param_set

    def get_model_dir(self):

        """ get model directory """

        # get select model
        model = self.params["model"]

        # return dir
        self.model_dir = os.path.join(self.set_dir, model)
        os.makedirs(self.model_dir, exist_ok=True)

        # return name
        self.model_jname = model

    def get_detailed_dir(self):

        """ get detailed dir """

        if self.model_jname in ["ErCA", "SynCA"]:

            """ check identity """

            ca_params_key = ['N', 'M', 's1', 's2', 'gamma_X', 'gamma_Y',
                             'Tc', 'Tx_rat', 'Tx_sqrt', 'Ty_rat', 'Ty_sqrt']

            ca_params = {key: self.params[key] for key in ca_params_key}

            # self.results_dir 内の data_lib.json の中身を確認
            data_lib_json_path = os.path.join(self.result_dir, 'data_lib.json')

            #if os.path.exists(data_lib_json_path):
            #    with open(data_lib_json_path, 'r') as f:
            #        data_lib = json.load(f)
            #else:
            #    data_lib = {}
            
            data_lib = safe_load_json(data_lib_json_path)

            # モデルごとのデータを取得
            model_data = data_lib.get(self.model_jname, {})

            # 一致する条件を検索
            condition_found = False
            for condition_name, condition_info in model_data.items():
                if condition_info.get('ca_params') == ca_params:
                    # 一致する条件が見つかった場合
                    self.condition_dir = os.path.join(self.model_dir, condition_name)
                    self.condition_jname = condition_name
                    condition_found = True
                    break

            if not condition_found:
                # 一致する条件が無かった場合、新しいディレクトリを作成
                existing_conditions = [name for name in model_data.keys() if name.startswith('condition_')]
                existing_numbers = [int(name.replace('condition_', '')) for name in existing_conditions]
                next_number = max(existing_numbers) + 1 if existing_numbers else 1
                condition_i = f'condition_{next_number}'
                self.condition_dir = os.path.join(self.model_dir, condition_i)
                os.makedirs(self.condition_dir, exist_ok=True)
                self.condition_jname = condition_i

                # data_lib.json を更新
                if self.model_jname not in data_lib:
                    data_lib[self.model_jname] = {}
                data_lib[self.model_jname][condition_i] = {'ca_params': ca_params}

                # 更新内容を保存
                with open(data_lib_json_path, 'w') as f:
                    json.dump(data_lib, f, indent=4)

        else:
            """ pass operation """

            # return dir
            self.condition_dir = os.path.join(self.model_dir, "results")
            os.makedirs(self.condition_dir, exist_ok=True)

            # return name
            self.condition_jname = "results"

    def get_sim_type(self):

        """ get sim type directory """

        # get sim type
        simulation = self.params["simulation"]

        # return dir
        self.sim_dir = os.path.join(self.condition_dir, simulation)
        os.makedirs(self.sim_dir, exist_ok=True)

        # return name
        self.sim_jname = simulation

    def set_result_path(self):

        # self.sim_dir のディレクトリに現在の日時を名前とした CSV ファイルを作成
        now_Q = self.params["Q"]
        now_S = self.params["S"]
        now_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        if self.sim_jname == "time evolution":
            csv_filename = f'{now_str}.csv'
        elif self.sim_jname == "bifurcation":
            csv_filename = f'bif_Q_{now_Q}_xaxisS_{now_S}_time_{now_str}.csv'
        elif self.sim_jname == "parameter region":
            csv_filename = f'parameter_region_time_{now_str}.csv'
        elif self.sim_jname == "attraction basin":
            csv_filename = f'attraction_basin_Q_{now_Q}_S_{now_S}_time_{now_str}.csv'
        elif self.sim_jname == "ReturnMap":
            csv_filename = f'return_map_{now_str}.csv'
        csv_filepath = os.path.join(self.sim_dir, csv_filename)

        # CSV ファイルを作成（ここでは空のファイルを作成）
        with open(csv_filepath, 'w') as f:
            pass

        self.result_path = csv_filepath

        # data_lib.json にディレクトリ構造と CSV ファイル名を保存
        data_lib_json_path = os.path.join(self.result_dir, 'data_lib.json')

        #if os.path.exists(data_lib_json_path):
        #    with open(data_lib_json_path, 'r') as f:
        #        data_lib = json.load(f)
        #else:
        #    data_lib = {}
        
        data_lib = safe_load_json(data_lib_json_path)

        # ディレクトリ構造を更新
        set_jname = self.set_jname
        model_jname = self.model_jname
        condition_jname = self.condition_jname
        sim_jname = self.sim_jname

        data_lib.setdefault(set_jname, {}).setdefault(model_jname, {}).setdefault(condition_jname, {}).setdefault(sim_jname, []).append(csv_filename)

        # 更新内容を保存
        with open(data_lib_json_path, 'w') as f:
            json.dump(data_lib, f, indent=4)

        # data_lib.csv に操作を記録
        data_lib_csv_path = os.path.join(self.result_dir, 'data_lib.csv')

        # カラムを定義
        columns = ['no.', 'filename', 'set', 'model', 'condition_dir', 'N', 'M', 's1', 's2', 'gamma_X', 'gamma_Y',
                   'Tc', 'Tx_rat', 'Tx_sqrt', 'Ty_rat', 'Ty_sqrt', 'simulation']

        # 既存のデータを読み込み
        if os.path.exists(data_lib_csv_path):
            df = pd.read_csv(data_lib_csv_path)
            no = int(df['no.'].max()) + 1 if not df.empty else 1
        else:
            df = pd.DataFrame(columns=columns)
            no = 1

        # 新しい行を作成
        row = {
            'no.': no,
            'filename': csv_filename,
            'set': set_jname,
            'model': model_jname,
            'condition_dir': condition_jname,
            'N': '', 'M': '', 's1': '', 's2': '', 'gamma_X': '', 'gamma_Y': '',
            'Tc': '', 'Tx_rat': '', 'Tx_sqrt': '', 'Ty_rat': '', 'Ty_sqrt': '',
            'simulation': self.params["simulation"]
        }

        # only ErCA, SynCA の場合はパラメータを埋める
        if model_jname in ["ErCA", "SynCA"]:
            ca_params_key = ['N', 'M', 's1', 's2', 'gamma_X', 'gamma_Y',
                             'Tc', 'Tx_rat', 'Tx_sqrt', 'Ty_rat', 'Ty_sqrt']
            for key in ca_params_key:
                row[key] = self.params.get(key, '')


        # return self.save_path
        self.save_path = csv_filepath

        # add a row in dataframe
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        df.to_csv(data_lib_csv_path, index=False)


def safe_load_json(file_path):
    """
    ファイルが存在し、サイズが 0 でなければ JSON を読み込み、
    それ以外は 空の dict を返す
    """
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}
# -*- coding: utf-8 -*-
"""
Created on: 2024-11-25
Updated on: 2026-02-26

@author: shirafujilab

Called from:
    - main window


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

        # root
        self.get_root_dir()

        # root - model
        self.get_sub_dir()

        # root - model - ca parameters
        self.get_subsub_dir()

        # get simulation dir
        self.get_sim_type()


    def get_root_dir(self):

        # get root dir
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.abspath(os.path.join(cur_dir, "..", ".."))

        # return dir (set root directory for results)
        self.result_dir = os.path.join(root_dir, "data", "results")
        os.makedirs(self.result_dir, exist_ok=True)


    def get_sub_dir(self):

        # get select model
        model = self.params["model"]

        # return dir
        self.model_dir = os.path.join(self.result_dir, model)
        os.makedirs(self.model_dir, exist_ok=True)

        # return name
        self.model_jname = model


    def get_subsub_dir(self):

        """ Define file path for restoring data """

        if self.model_jname in ["esl"]:

            # classify by identical parameters
            ca_params_key = ['M', 'N1', 'N2', 'N3', 's1', 's2', 's3',
                             'Tc', 'Tx_rat', 'Tx_sqrt', 'Ty_rat', 'Ty_sqrt', 'Tz_rat', 'Tz_sqrt']

            ca_params = {key: self.params[key] for key in ca_params_key}

            # self.results_dir 内の data_lib.json の中身を確認
            data_lib_json_path = os.path.join(self.result_dir, 'data_lib.json')
            data_lib = safe_load_json(data_lib_json_path)

            # get data
            model_data = data_lib.get(self.model_jname, {})

            # If match
            condition_found = False
            for condition_name, condition_info in model_data.items():
                if condition_info.get('esl_params') == ca_params:

                    self.condition_dir = os.path.join(self.model_dir, condition_name)
                    self.condition_jname = condition_name
                    condition_found = True
                    break

            # Not match
            if not condition_found:

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

        now_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        if self.sim_jname == "time evolution" or "lut":
            csv_filename = f'{now_str}.csv'
        elif self.sim_jname == "bifurcation":
            csv_filename = f'bifurcation_time_{now_str}.csv'

        csv_filepath = os.path.join(self.sim_dir, csv_filename)

        # make blank csv
        with open(csv_filepath, 'w') as f:
            pass

        self.result_path = csv_filepath

        # data_lib.json にディレクトリ構造と CSV ファイル名を保存
        data_lib_json_path = os.path.join(self.result_dir, 'data_lib.json')

        data_lib = safe_load_json(data_lib_json_path)

        # update construction of directory
        model_jname = self.model_jname
        condition_jname = self.condition_jname
        sim_jname = self.sim_jname

        data_lib.setdefault(model_jname, {}).setdefault(condition_jname, {}).setdefault(sim_jname, []).append(csv_filename)

        # Store results
        with open(data_lib_json_path, 'w') as f:
            json.dump(data_lib, f, indent=4)

        # data_lib.csv に操作を記録
        data_lib_csv_path = os.path.join(self.result_dir, 'data_lib.csv')

        # define columns
        columns = ['no.', 'filename', 'model', 'condition_dir',
                   'M', 'N1', 'N2', 'N3', 's1', 's2', 's3',
                   'Tc', 'Tx_rat', 'Tx_sqrt', 'Ty_rat', 'Ty_sqrt', 'Tz_rat', 'Tz_sqrt',
                   'simulation']

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
            'model': model_jname,
            'condition_dir': condition_jname,
            'M': '',
            'N1': '', 'N2': '', 'N3': '',
            's1': '', 's2': '', 's3': '',
            'Tc': '', 'Tx_rat': '', 'Tx_sqrt': '', 'Ty_rat': '', 'Ty_sqrt': '', 'Tz_rat': '', 'Tz_sqrt': '',
            'simulation': self.params["simulation"]
        }

        # only ErCA, SynCA の場合はパラメータを埋める
        if model_jname in ["esl"]:
            ca_params_key = ['M',
                             'N1', 'N2', 'N3',
                             's1', 's2', 's3',
                             'Tc', 'Tx_rat', 'Tx_sqrt', 'Ty_rat', 'Ty_sqrt', 'Tz_rat', 'Tz_sqrt']
            for key in ca_params_key:
                row[key] = self.params.get(key, '')

        self.save_path = csv_filepath

        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        df.to_csv(data_lib_csv_path, index=False)


def safe_load_json(file_path):

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}
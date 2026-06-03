import argparse
import importlib
import sys
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

'''
Script to generate synthetic data sets from a config file.
This is called with the following variables:
    --n_med : Number of medical entries
    --n_id : Number of identity entries
    --n_overlap : Number of overlapping entries
    --destination : Where you would like to save data (optional)
        - Defaults to 'data/temp.csv'
    --config : File that describes the parameter setup (optional)
        - Defaults to 'config/config_fields.py'
'''

def _determine_functions(fields: list):
    names: list[str] = []
    function: list = []

    for field in fields:
        if field.choice not in field.options:
            raise ValueError(
                f'Choice not in list of options for {field.name}. Review configuration file.'
            )
        
        names.append(field.name)

        index = field.options.index(field.choice)
        function.append(field.functions[index])

    return dict(zip(names, function))


def make_data(
        n_med: int,
        n_id: int,
        n_overlap: int,
        config: str = 'config_fields'
):
    module = importlib.import_module(f'configs.{config}')
    fields = module.fields

    functions = _determine_functions(fields)
    med_data = pd.DataFrame()
    id_data = pd.DataFrame()

    for field in fields:
        med_data[field.name] = functions[field.name](n_med)
        id_data[field.name] = functions[field.name](n_id - n_overlap)

    overlap_data = med_data.sample(n = n_overlap)
    id_data = pd.concat([id_data, overlap_data]).sample(frac=1).reset_index(drop=True)

    data = pd.concat([id_data, med_data], keys=['id_data', 'med_data'])
    data.index.name = 'id'

    return data


def main():
    parser = argparse.ArgumentParser(description='Generate medical and ID data')
    parser.add_argument('--n_med', type = int, required = True, 
                        help = 'Number of medical records')
    parser.add_argument('--n_id', type = int, required = True, 
                        help = 'Number of ID records')
    parser.add_argument('--n_overlap', type = int, required = True, 
                        help = 'Number of overlapping records')
    parser.add_argument('--destination', type = str,
                        default = ROOT / 'data' / 'temp.csv',
                        help = 'Output CSV file path (default: ../data/temp.csv)')
    parser.add_argument('--config', type = str,
                        default = 'config_fields',
                        help = 'Config module name from configs/ (default: config_fields)')

    args = parser.parse_args()
    data = make_data(
        n_med=args.n_med,
        n_id=args.n_id,
        n_overlap=args.n_overlap,
        config=args.config
    )

    data.to_csv(args.destination, index = True)
    print(f'Data saved to {args.destination}')

if __name__ == '__main__':
    main()
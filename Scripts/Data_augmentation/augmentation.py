import os
import json
import random
import argparse
from tqdm import tqdm

def augmentation(num, ratio, file_name):
    # Load the data
    with open("../../PCBs/" + file_name + "/final.json", 'r') as f:
        data = json.load(f)
        for i in tqdm(range(num)):
            # print(type(data['nets']))
            # print(len(data['nets']))
            # Select random nets
            random_nets_indices = random.sample(range(len(data['nets'])-1), int((len(data['nets'])-1)*ratio))  # select 5 random nets
            random_nets = [data['nets'][str(index+1)] for index in random_nets_indices]

            # Select corresponding wires
            random_wires = [wire for wire in data['solution']['wires'] if wire['net']-1 in random_nets_indices]
            # Prepare the data to be written
            output_data = {
                'layers': data['layers'],
                'unit': data['unit'],
                'border': data['border'],
                'rules': data['rules'],
                # 'loss': data['loss'],
                'nets': random_nets,
                'solution': {
                    'wires': random_wires,
                    'vias': data['solution']['vias']
                }
            }

            # Define the output directory and file
            output_dir = "../../PCBs/" + file_name + "/augmented_data/"
            output_file = str(i) + ".json"

            # Create the directory if it does not exist
            os.makedirs(output_dir, exist_ok=True)

            # Define the full path to the file
            full_path = os.path.join(output_dir, output_file)

            # Write to a new JSON file
            with open(full_path, 'w') as f:
                json.dump(output_data, f, indent=4)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process JSON files.')
    parser.add_argument('num', type=int, help='The number of sampled data.')
    parser.add_argument('ratio', type=float, help='The proportion you want to randomly select.')
    parser.add_argument('file_name', type=str, help='The name of the dataset.')

    args = parser.parse_args()
    augmentation(args.num, args.ratio, args.file_name)

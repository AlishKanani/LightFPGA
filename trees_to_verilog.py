import json, math
from light_logic import write_logic
f = open('m.json','r')
data = json.load(f)
tree_input = []
leaf_arr = []
norm_leaf = []
leaf_fact = 10**6
end_count = 0

def find_feature(tree_struc):
    if 'split_feature' in tree_struc:
        if tree_struc['split_feature'] not in total_input:
            total_input.append(tree_struc['split_feature']) 

    if 'left_child' in tree_struc:
        left = tree_struc['left_child']
        right = tree_struc['right_child']
        find_feature(left)
        find_feature(right)

def leaf_min(tree_struc):
    if 'leaf_value' in tree_struc:
        leaf_arr.append(tree_struc['leaf_value'])
    
    if 'left_child' in tree_struc:
        left = tree_struc['left_child']
        right = tree_struc['right_child']
        leaf_min(left)
        leaf_min(right)

feature_name = data['feature_names']
max_input = 0

for feature in feature_name:
    if data.get('feature_infos').get(feature) != None:
        if data.get('feature_infos').get(feature).get('max_value') > max_input:
            max_input = data.get('feature_infos').get(feature).get('max_value')
input_size = math.ceil(math.log(max_input+1,2)) -1

for tr in data['tree_info']:
    tree_struc = tr['tree_structure']
    leaf_min(tree_struc)

minimum_leaf = min(leaf_arr)

for i in leaf_arr:
    norm_leaf.append((i-minimum_leaf)*leaf_fact)

for tree in data['tree_info']:
    tree_structure = tree['tree_structure']
    num_leaves = tree['num_leaves']
    
    max_norm = max(norm_leaf[end_count:end_count+num_leaves])
    output_size = math.ceil(math.log(max_norm , 2))-1
    end_count = end_count + num_leaves 

    tree_file = open('tree/tree_{}.v'.format(tree['tree_index']),'w')

    total_input = []
    find_feature(tree_structure)
    tree_input.append(total_input)

    tree_file.write('`timescale 1ns / 1ps\n')
    tree_file.write('module tree_{} (\n'.format(tree['tree_index']))
    tree_file.write('input wire clk,\n')
    for feature in total_input:
        tree_file.write('input wire [{}:0] feature_{}, \n'.format(input_size,feature))
    tree_file.write('output reg [{}:0] tree_out );\n\n'.format(output_size))
    tree_file.write('always@(posedge clk) \nbegin\n')

    write_logic(tree_file, tree_structure, minimum_leaf, leaf_fact)

    tree_file.write('\nend\n')
    tree_file.write('endmodule')
    tree_file.close()

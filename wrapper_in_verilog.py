import math, os, json

f = open('m.json','r')
data = json.load(f)

n_class=data['num_class']
n_iterations = int(len(data.get('tree_info'))/n_class)
n_trees=n_class*n_iterations
n_features=data['max_feature_idx']+1

sum_size=0
cycles_required=0
sums_array=[]
tree_number=0
sum_index=0
sum_index_rhs=0
old_sum_index_rhs=0

n_itr = n_iterations
while (n_itr!=1):
    n_itr = math.ceil((n_itr/2))
    cycles_required=cycles_required+1
    sums_array.append(n_itr)

output_wire_bits=[]
      
forest_name="lightGBM"
output_filename= 'tree/{}.v'.format(forest_name)

w_file = open(output_filename, 'w')

#Printing Headers
w_file.write('`timescale 1ns / 1ps\n')
w_file.write('module {}(\n'.format(forest_name))
w_file.write('input wire clk,\n')
           
for tree_number in range(n_trees):
    verilog_tree_name = 'tree_{}'.format(tree_number)
    file = open('tree/{}.v'.format(verilog_tree_name),"r")
    file_lines=file.readlines()

    current_line=file_lines[3]
    input_wire_size = current_line[current_line.find('['):current_line.find(']')+1]

    for line in file_lines:
        if 'output' in line:
            output_wire_size = line[line.find('['):line.find(']')+1]
            output_wire_bits.append(int(output_wire_size[output_wire_size.find('[')+1:output_wire_size.find(':')]))

reg_bits = max(output_wire_bits) + cycles_required    

for x in range(n_features):
    w_file.write('input wire {} feature_{},\n'.format(input_wire_size,x))

for leaf_number in range(n_class):
    if leaf_number == n_class-1:
        w_file.write('output wire [{}:0] Leaf_{});\n\n'.format(reg_bits,leaf_number))
    else:
        w_file.write('output wire [{}:0] Leaf_{},\n'.format(reg_bits,leaf_number))

tree_number=0
for tree_number in range(n_trees):
    w_file.write('wire [{}:0] tree_out_{}_{};\n'.format(output_wire_bits[tree_number], int(tree_number/n_class),tree_number%n_class))

w_file.write('\n')

reg_ver = max(output_wire_bits)

for i in range(cycles_required):
    reg_ver = reg_ver+1
    for leaf_number in range(n_class):
        for j in range(sums_array[i]):
            w_file.write('reg [{}:0] leaf_{}_{}_sum_{};\n'.format(reg_ver,i,leaf_number,j))

print(sums_array)
w_file.write('\n')

for leaf_number in range(n_class):
    w_file.write('assign Leaf_{} = leaf_{}_{}_sum_{};\n'.format(leaf_number,cycles_required-1,leaf_number,sums_array[cycles_required-1]-1))

w_file.write('\n')

for tree_number in range(n_trees):
    verilog_tree_name = 'tree_{}'.format(tree_number)
    file = open("tree/{}.v".format(verilog_tree_name),"r+")
    file_lines=file.readlines()
        
    #instances
    w_file.write('{}  inst_{}(\n'.format(verilog_tree_name,tree_number))
    w_file.write('.clk(clk),\n')
    for i in range (len(file_lines)):
        if(file_lines[i].find('input wire')>=0 and file_lines[i].find('feature')>=0):
            current_line=file_lines[i]
            current_line= current_line[current_line.find('f'):current_line.find(',')]
            w_file.write('.{}({}),\n'.format(current_line,current_line))
                
        elif(file_lines[i].find('output')>=0):
            current_line=file_lines[i]
            w_file.write('.tree_out(tree_out_{}_{})'.format(int(tree_number/n_class),tree_number%n_class))
    w_file.write('\n);\n\n')              

                    
tree_number=0
sum_index=0
sum_index_rhs=0
old_sum_index_rhs=0

for i in range(cycles_required):
    w_file.write('\n\nalways@(posedge clk)\n')
    w_file.write('begin\n')

    if(i==0):
        for leaf_number in range(n_class):
            for j in range(sums_array[i]):
                w_file.write('leaf_{}_{}_sum_{} <= tree_out_{}_{}'.format(i, leaf_number, j, 2*j, leaf_number))

                if((2*j+1) <n_iterations):
                    w_file.write(' + tree_out_{}_{};\n'.format(2*j+1, leaf_number))
                else:
                    w_file.write(';\n')
    
            w_file.write('\n')
    else:
        for leaf_number in range(n_class):
            for j in range(sums_array[i]):
                w_file.write('leaf_{}_{}_sum_{} <= leaf_{}_{}_sum_{}'.format(i,leaf_number,j,i-1,leaf_number,2*j))

                if ((2*j+1) <sums_array[i-1]):
                    w_file.write(' + leaf_{}_{}_sum_{};\n'.format(i-1,leaf_number,2*j+1))
                else:
                    w_file.write(';\n')
            
            w_file.write('\n')

    w_file.write('end\n')
    old_sum_index = sum_index
    old_sum_index_rhs = sum_index_rhs

w_file.write('endmodule')        

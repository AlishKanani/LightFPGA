import json, lightgbm, os
from sklearn.datasets import load_digits

tree_number = 0
n_test = 5
f = open('m.json','r')
data = json.load(f)

digits = load_digits()
X = digits.data
X_test = X[0:n_test]

model = lightgbm.Booster(model_file='m.txt')
pred_X = model.predict(X_test, num_iteration=model.best_iteration,pred_leaf=True)

def find_feature(tree_struc):
    if 'split_feature' in tree_struc:
        if tree_struc['split_feature'] not in total_input:
            total_input.append(tree_struc['split_feature']) 

    if 'left_child' in tree_struc:
        left = tree_struc['left_child']
        right = tree_struc['right_child']
        find_feature(left)
        find_feature(right)

for tree in data['tree_info']:
    if tree['tree_index'] == tree_number:
        tree_structure = tree['tree_structure']
        
        total_input = []
        find_feature(tree_structure)
        
        v_file = open('tree/tree_{}.v'.format(tree_number),'r')
        lines = v_file.readlines()
        
        for line in lines:
            if 'input wire [' in line:
                input_size = line[line.find('['):line.find(']')+1]
            if 'output' in line:
                output_size = line[line.find('['):line.find(']')+1]

        test_file = open('tree/tree_{}tb.v'.format(tree_number),'w')
        test_file.write('module tree_{}tb;\n'.format(tree_number))
        test_file.write('reg clk;\n')
        for feature in total_input:
            test_file.write('reg {} feature_{};\n'.format(input_size,feature))
        test_file.write('wire {} tree_out;\n\n'.format(output_size))

        test_file.write('tree_{} uut(\n.clk(clk),\n'.format(tree_number))
        for feature in total_input:
            test_file.write('.feature_{}(feature_{}),\n'.format(feature,feature))
        test_file.write('.tree_out(tree_out));\n\n')

        test_file.write('initial begin \nclk = 0; \nend\n\n')
        test_file.write('always \n#5 clk = ~clk; \n\ninitial begin\n')

        for test in range(n_test):
            for feature in total_input:
                test_file.write('feature_{} = {};\n'.format(feature,int(X_test[test][feature])))
            test_file.write('\n#10\n')

        test_file.write('$finish; \nend\n\n')
        test_file.write('initial\n$monitor( "simetime = %g, out=%d, ", $time, tree_out);\n')
        test_file.write('\nendmodule')
        test_file.close()
        

for i in range(n_test):
    print(pred_X[i][tree_number])

os.system("rm a.out")
os.system("iverilog tree/tree_{}.v tree/tree_{}tb.v".format(tree_number,tree_number))
os.system("vvp a.out")
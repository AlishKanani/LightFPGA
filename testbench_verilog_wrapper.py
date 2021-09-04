import json, os, time,re
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

# n_test = 5
f = open('m.json','r')
data = json.load(f)
n_feature = data.get('max_feature_idx')+1
n_class = data.get('num_class')
n_tree = len(data.get('tree_info'))

digits = load_digits()
X = digits.data
y = digits.target
X_tr, X_test, y_tr, y_te = train_test_split(X, y, test_size=0.4)

n_test = len(X_test)


import lightgbm
model = lightgbm.Booster(model_file='m.txt')
t = time.time()

pred_X = model.predict(X_test, num_iteration=model.best_iteration)
print(time.time()-t)

v_file = open('tree/lightGBM.v','r')
lines = v_file.readlines()

line = lines[3]
input_size = line[line.find('['):line.find(']')+1]

for line in lines:
    if 'output' in line:
        output_size = line[line.find('['):line.find(']')+1]

test_file = open('tree/lightGBM_tb.v','w')
test_file.write('module lightGBM_tb;\n')
test_file.write('reg clk;\n')

for feature in range(n_feature):
    test_file.write('reg {} feature_{};\n'.format(input_size,feature))

for output in range(n_class):
    test_file.write('wire {} Leaf_{};\n'.format(output_size,output))

test_file.write('\nlightGBM uut(\n.clk(clk),\n')
for feature in range(n_feature):
    test_file.write('.feature_{}(feature_{}),\n'.format(feature,feature))
for output in range(n_class):
    if output == n_class-1:
        test_file.write('.Leaf_{}(Leaf_{}));\n\n'.format(output,output))
    else:
        test_file.write('.Leaf_{}(Leaf_{}), \n'.format(output,output))


test_file.write('initial begin \nclk = 0; \nend\n\nalways \n#5 clk = ~clk; \n\ninitial begin\n')

for test in range(n_test):
    for feature in range(n_feature):
        test_file.write('feature_{} = {};\n'.format(feature,int(X_test[test][feature])))
    test_file.write('\n#10\n')

test_file.write('#1000\n$finish; \nend\n\n')
test_file.write('initial\n$monitor( "simetime = %g, ')
for output in range(n_class):
    if output == n_class-1:
        test_file.write('%d')
    else:
        test_file.write('%d,')

test_file.write('", $time, ')
for output in range(n_class):
    if output == n_class-1:
        test_file.write('Leaf_{}'.format(output))
    else:
        test_file.write('Leaf_{},'.format(output))
test_file.write(');\n')

test_file.write('\nendmodule')
test_file.close()

# os.system("rm a.out")

# link = 'iverilog tree/lightGBM.v tree/lightGBM_tb.v '

# for i in range(n_tree):
#     line = 'tree/tree_{}.v '.format(i)
#     link = link + line

link = 'iverilog tree/*.v'
os.system(link)

result_p = []
for i in range(n_test):
    pred = list(pred_X[i])
    result_p.append(pred.index(max(pred)))

os.system("vvp a.out > temp.txt")

file = open('temp.txt')
file_lines=file.readlines()

result_v=[]
for i in range (len(file_lines)):
    if(i>0):
        line=file_lines[i]
        x=line.find(',')
        line=line[x+2:]
        temp = re.findall(r'\d+', line)
        res = list(map(int, temp))
        result_v.append(res.index(max(res)))

result_p = np.array(result_p)
result_v = np.array(result_v)
error = result_p - result_v

print(np.mean(np.abs(error)))
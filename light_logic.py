import math

def write_logic(tree_file, tree_struc, minimum_leaf, leaf_fact):
    if 'split_feature' in tree_struc:
        tree_file.write("if (feature_{}{}{}) \nbegin \n".format(tree_struc['split_feature'],tree_struc['decision_type'],math.floor(tree_struc['threshold'])))
    else :
        tree_file.write("   tree_out <= {};\n".format(round((tree_struc['leaf_value'] - minimum_leaf)*leaf_fact))) # outputs are scaled leaf value
        # tree_file.write("   tree_out <= {};\n".format(tree_struc['leaf_index'])) # for testing(outputs are leaf index)
    
    if 'left_child' in tree_struc:
        left = tree_struc['left_child']
        write_logic(tree_file, left, minimum_leaf, leaf_fact)
        tree_file.write("end \n" )
       
    if 'right_child' in tree_struc:
        tree_file.write("else \nbegin \n")
        right = tree_struc['right_child']
        write_logic(tree_file, right, minimum_leaf, leaf_fact)
        tree_file.write("end \n" )


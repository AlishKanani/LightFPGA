import json, time
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


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

result_p = []
for i in range(n_test):
    pred = list(pred_X[i])
    result_p.append(pred.index(max(pred)))

y_test = list(y_te)

accuracy = accuracy_score(y_true=y_test, y_pred=result_p)
print('accuracy : {}%'.format(accuracy*100))
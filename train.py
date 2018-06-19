import pandas as pd
import sys, pickle
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction import FeatureHasher

enc = OneHotEncoder()

train = False if len(sys.argv) < 2 else True

from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report


	# from sklearn.tree import DecisionTreeClassifier

from sklearn.neighbors import KNeighborsClassifier
# from sklearn.naive_bayes import GaussianNB
# from sklearn.linear_model import LogisticRegression
# from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier


def converte_categorias(df):
	pd.options.mode.chained_assignment = None  # default='warn'
	df.cfop = pd.Categorical(df.cfop)
	df['cfop'] = df.cfop.cat.codes
	df.ncm = pd.Categorical(df.ncm)
	df['ncm'] = df.ncm.cat.codes
	df.natureza_frete = pd.Categorical(df.natureza_frete)
	df['natureza_frete'] = df.natureza_frete.cat.codes
	return df

dataset = pd.read_csv("./dataset2.csv", delimiter=";")

trainset = dataset[:int(len(dataset)*0.7)]
testset = dataset[int(len(dataset)*0.7):]

X_train = trainset.loc[:, trainset.columns != "y"]
y_train = trainset.loc[:, trainset.columns == "y"]
y_train = y_train.values.ravel()


X_test = testset.loc[:, testset.columns != "y"]
y_test = testset.loc[:, testset.columns == "y"]
y_test = y_test.values.ravel()

# X_train = converte_categorias(X_train)
# X_test = converte_categorias(X_test)
X_train = pd.get_dummies(X_train)
print(X_train)
enc.fit(X_train.as_matrix()).transform(X_train.as_matrix()).toarray()
enc.transform(X_train).toarray()

folds = 3

knn = KNeighborsClassifier()
knn_params = {
	"n_neighbors": [2, 3, 5, 10],
	"weights": ["uniform", "distance"],
	"p": [1, 2]
}

pcptron = MLPClassifier()
pcptron_params = {
	"hidden_layer_sizes": [1,2],    
	"max_iter": [50,100,200]    
}

rf = RandomForestClassifier()
rf_params = {
	"n_estimators": [5,10],
	"criterion": ["entropy"],
	"max_features": ["auto","sqrt"]
}

classifiers = [knn]
grids = [knn_params]

grid_params = zip(classifiers, grids)

filename = 'model.sav'
if train:
	for _, (classifier, params) in enumerate(grid_params):

		print("Buscando para algoritmo: {0}\n".format(classifier.__class__))
		
		
		clf = GridSearchCV(estimator=classifier,  # algoritmo em teste
								   param_grid=params,  # parâmetros de busca
								   cv=folds,  # objeto que vai gerar as divisões
								   n_jobs=-1, #processamento
								   scoring='accuracy')  # score que será utilizado
			
		
		clf.fit(X_train, y_train.ravel())

		print("Melhor seleção de hyperparâmetros:\n")
		print(clf.best_params_)
		print("\nScores (% de acertos) nos folds de validação:\n")
		means = clf.cv_results_['mean_test_score'] 
		stds = clf.cv_results_['std_test_score']
		for mean, std, params in zip(means, stds, clf.cv_results_['params']):
			print("{:.3f} (+/-{:.3f}) for {}".format(mean, std * 2, params))
		print("\nResultado detalhado para o melhor modelo:\n")
		y_true, y_pred = y_test, clf.predict(X_test)
		print(classification_report(y_true, y_pred))
		pickle.dump(clf, open(filename, 'wb'))
else:
	loaded_model = pickle.load(open(filename, 'rb'))

	evaluate = pd.read_csv('./dataset3.csv', delimiter=";")
	
	X_eval = evaluate.loc[:, evaluate.columns != "y"]
	y_eval = evaluate.loc[:, evaluate.columns == "y"]
	y_eval = y_eval.values.ravel()
	# X_eval_cat = converte_categorias(X_eval)
	X_eval = pd.get_dummies(X_eval)
	y_true, y_pred = y_test, loaded_model.predict(X_eval)
	print(classification_report(y_true, y_pred))


import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ml.retrain import train_model

if __name__ == '__main__':
    print('Training initial Random Forest model...')
    success, auc, version = train_model(auc_threshold=0.60)
    if success:
        print(f'Initial model ready. Version: {version}')
    else:
        print('Training failed threshold check. Try lowering auc_threshold.')
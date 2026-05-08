# yasin_ahmed_final-project_sp26



How to run: Use these commands in terminal  




pip install -r requirements.txt  

python ml/train_initial_model.py    # trains + saves the RF model  

python init_db.py                   # creates tables + seeds demo data  

python run.py                       # starts app at localhost:5000  



To use:  


Go to localhost:5000  

Click New Quote  

Enter Customer ID C-DEMO01 (or C-DEMO02 for a high-risk patient), Account ID ACC-001, Company Code COL  

You'll see risk scores from the ML model and an adjusted premium  

Click Accept to issue the policy and see it written to the DB  


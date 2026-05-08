import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from db.session import init_db, Session
from app.models import (Account, Associate, Customer, AccountMember,
                         DocumentMetadata)
from datetime import date


def seed():
    db = Session()
    try:
        # Account
        if not db.query(Account).filter_by(AccountID='ACC-001', CompanyCode='COL').first():
            db.add(Account(
                AccountID='ACC-001', CompanyCode='COL',
                AccountName="Keith's Garage", AccountType='GroupMaster',
                Address='123 Main St, Columbus OH', Status='Active'
            ))

        if not db.query(Account).filter_by(AccountID='ACC-002', CompanyCode='NY').first():
            db.add(Account(
                AccountID='ACC-002', CompanyCode='NY',
                AccountName="Dana's Dry Cleaning", AccountType='Standard',
                Address='456 Park Ave, New York NY', Status='Active'
            ))

        # Associate
        if not db.query(Associate).filter_by(AssociateID='ASC-001').first():
            db.add(Associate(
                AssociateID='ASC-001', Name='John Smith',
                LicenseState='OH', SitCode0='DSC-001'
            ))

        # Customers
        customers = [
            ('C-DEMO01', 'Alice Johnson',   date(1975, 3, 12), 'Female', 'OH', '43215'),
            ('C-DEMO02', 'Bob Martinez',    date(1960, 8, 25), 'Male',   'MS', '39401'),
            ('C-DEMO03', 'Carol Williams',  date(1990, 1, 5),  'Female', 'NY', '10001'),
            ('C-DEMO04', 'David Lee',       date(1955, 11, 30),'Male',   'TX', '77001'),
        ]
        for cid, name, dob, gender, state, zipcode in customers:
            if not db.query(Customer).filter_by(CustomerID=cid).first():
                db.add(Customer(
                    CustomerID=cid, Name=name, CustomerType='Person',
                    DateOfBirth=dob, Gender=gender,
                    StateCode=state, ZipCode=zipcode
                ))

        # Account memberships
        memberships = [
            ('MBR-001', 'C-DEMO01', 'ACC-001', 'COL', date(2022, 1, 1)),
            ('MBR-002', 'C-DEMO02', 'ACC-001', 'COL', date(2021, 6, 15)),
            ('MBR-003', 'C-DEMO03', 'ACC-002', 'NY',  date(2023, 3, 1)),
            ('MBR-004', 'C-DEMO04', 'ACC-001', 'COL', date(2020, 9, 10)),
        ]
        for mid, cid, aid, cc, start in memberships:
            if not db.query(AccountMember).filter_by(MemberID=mid).first():
                db.add(AccountMember(
                    MemberID=mid, CustomerID=cid,
                    AccountID=aid, CompanyCode=cc,
                    StartDate=start, EndDate=None, Status='Active'
                ))

        # Document metadata
        if not db.query(DocumentMetadata).filter_by(DocumentID='DOC-001').first():
            db.add(DocumentMetadata(
                DocumentID='DOC-001',
                DocumentTitle='CDC BRFSS 2023 State Survey',
                DocumentSource='CDC',
                DocumentType='CSV',
                StorageURL='https://storage.blob.core.windows.net/raw/brfss_2023.csv',
                UploadDate=date(2024, 1, 15),
                StateCode=None,
                BenefitType=None,
                KeywordTags='["diabetes","cardiovascular","obesity"]'
            ))

        db.commit()
        print('Seed data inserted successfully.')
    except Exception as e:
        db.rollback()
        print(f'Seeding error: {e}')
    finally:
        db.close()


if __name__ == '__main__':
    print('Initializing database...')
    init_db()
    print('Tables created.')
    seed()
    print('Done. Run: python run.py')

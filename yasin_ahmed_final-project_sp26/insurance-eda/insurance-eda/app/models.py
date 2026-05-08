from sqlalchemy import (
    Column, String, Date, Numeric, Boolean, Text,
    ForeignKey, ForeignKeyConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from db.session import Base
from datetime import date, datetime, timedelta
from config import Config

# ── ACCOUNT DOMAIN ──────────────────────────────────────────

class Account(Base):
    __tablename__ = 'ACCOUNT'
    AccountID      = Column(String(20), primary_key=True)
    CompanyCode    = Column(String(10), primary_key=True)
    AccountName    = Column(String(100), nullable=False)
    AccountType    = Column(String(20), nullable=False)
    ParentAccountID = Column(String(20), nullable=True)
    Address        = Column(String(200), nullable=True)
    Status         = Column(String(10), nullable=False, default='Active')

    __table_args__ = (
        UniqueConstraint('AccountName', 'CompanyCode', name='UQ_ACCOUNT_NAME_CODE'),
    )

    members   = relationship('AccountMember', back_populates='account')
    contracts = relationship('Contract', back_populates='account')


class BillingAccount(Base):
    __tablename__ = 'BILLING_ACCOUNT'
    BillingAccountID = Column(String(20), primary_key=True)
    POBox            = Column(String(50), nullable=True)
    BillingType      = Column(String(20), nullable=False)
    EmployeeType     = Column(String(20), nullable=False, default='All')


class AccountBilling(Base):
    __tablename__ = 'ACCOUNT_BILLING'
    AccountID        = Column(String(20), primary_key=True)
    CompanyCode      = Column(String(10), primary_key=True)
    BillingAccountID = Column(String(20), ForeignKey('BILLING_ACCOUNT.BillingAccountID'), primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(['AccountID', 'CompanyCode'],
                             ['ACCOUNT.AccountID', 'ACCOUNT.CompanyCode']),
    )


class AccountAdmin(Base):
    __tablename__ = 'ACCOUNT_ADMIN'
    AdminID       = Column(String(20), primary_key=True)
    Name          = Column(String(100), nullable=False)
    ExpertiseType = Column(String(30), nullable=True)


class AccountAdminLink(Base):
    __tablename__ = 'ACCOUNT_ADMIN_LINK'
    AccountID   = Column(String(20), primary_key=True)
    CompanyCode = Column(String(10), primary_key=True)
    AdminID     = Column(String(20), ForeignKey('ACCOUNT_ADMIN.AdminID'), primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(['AccountID', 'CompanyCode'],
                             ['ACCOUNT.AccountID', 'ACCOUNT.CompanyCode']),
    )


class AccountMember(Base):
    __tablename__ = 'ACCOUNT_MEMBER'
    MemberID    = Column(String(20), primary_key=True)
    CustomerID  = Column(String(20), ForeignKey('CUSTOMER.CustomerID'), nullable=False)
    AccountID   = Column(String(20), nullable=False)
    CompanyCode = Column(String(10), nullable=False)
    StartDate   = Column(Date, nullable=False)
    EndDate     = Column(Date, nullable=True)
    Status      = Column(String(10), nullable=False, default='Active')

    __table_args__ = (
        ForeignKeyConstraint(['AccountID', 'CompanyCode'],
                             ['ACCOUNT.AccountID', 'ACCOUNT.CompanyCode']),
    )

    customer = relationship('Customer', back_populates='memberships')
    account  = relationship('Account', back_populates='members')


class AccountAlias(Base):
    __tablename__ = 'ACCOUNT_ALIAS'
    AliasID        = Column(String(20), primary_key=True)
    AccountID      = Column(String(20), nullable=False)
    CompanyCode    = Column(String(10), nullable=False)
    OriginalSource = Column(String(30), nullable=False)
    OriginalRecord = Column(Text, nullable=False)
    CreatedDate    = Column(Date, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(['AccountID', 'CompanyCode'],
                             ['ACCOUNT.AccountID', 'ACCOUNT.CompanyCode']),
    )


class AccountAccount(Base):
    __tablename__ = 'ACCOUNT_ACCOUNT'
    ParentAccountID  = Column(String(20), primary_key=True)
    ChildAccountID   = Column(String(20), primary_key=True)
    CompanyCode      = Column(String(10), primary_key=True)
    RelationshipType = Column(String(30), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(['ParentAccountID', 'CompanyCode'],
                             ['ACCOUNT.AccountID', 'ACCOUNT.CompanyCode']),
        ForeignKeyConstraint(['ChildAccountID', 'CompanyCode'],
                             ['ACCOUNT.AccountID', 'ACCOUNT.CompanyCode']),
    )


# ── ASSOCIATE DOMAIN ────────────────────────────────────────

class Associate(Base):
    __tablename__ = 'ASSOCIATE'
    AssociateID  = Column(String(20), primary_key=True)
    Name         = Column(String(100), nullable=False)
    LicenseState = Column(String(2), nullable=True)
    SitCode0     = Column(String(20), nullable=True)

    licenses          = relationship('AssociateLicense', back_populates='associate')
    manager_contracts = relationship('ManagerContract', back_populates='associate')


class AssociateLicense(Base):
    __tablename__ = 'ASSOCIATE_LICENSE'
    LicenseID   = Column(String(20), primary_key=True)
    AssociateID = Column(String(20), ForeignKey('ASSOCIATE.AssociateID'), nullable=False)
    StateCode   = Column(String(2), nullable=False)
    IsActive    = Column(Boolean, nullable=False, default=True)

    associate = relationship('Associate', back_populates='licenses')


class ManagerContract(Base):
    __tablename__ = 'MANAGER_CONTRACT'
    ManagerContractID = Column(String(20), primary_key=True)
    AssociateID       = Column(String(20), ForeignKey('ASSOCIATE.AssociateID'), nullable=False)
    WritingNumber     = Column(String(30), nullable=False)
    SitCode           = Column(String(20), nullable=False)
    StateCode         = Column(String(2), nullable=False)
    IsActive          = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint('WritingNumber', 'StateCode', name='UQ_WRITING_STATE'),
    )

    associate = relationship('Associate', back_populates='manager_contracts')


class AccountManagerContract(Base):
    __tablename__ = 'ACCOUNT_MANAGER_CONTRACT'
    AccountID         = Column(String(20), primary_key=True)
    CompanyCode       = Column(String(10), primary_key=True)
    ManagerContractID = Column(String(20), ForeignKey('MANAGER_CONTRACT.ManagerContractID'), primary_key=True)
    RoleType          = Column(String(30), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(['AccountID', 'CompanyCode'],
                             ['ACCOUNT.AccountID', 'ACCOUNT.CompanyCode']),
    )


class AssociateAssociate(Base):
    __tablename__ = 'ASSOCIATE_ASSOCIATE'
    AssociateID        = Column(String(20), ForeignKey('ASSOCIATE.AssociateID'), primary_key=True)
    RelatedAssociateID = Column(String(20), ForeignKey('ASSOCIATE.AssociateID'), primary_key=True)
    RelationshipType   = Column(String(30), nullable=False)


# ── CUSTOMER DOMAIN ─────────────────────────────────────────

class Customer(Base):
    __tablename__ = 'CUSTOMER'
    CustomerID   = Column(String(20), primary_key=True)
    Name         = Column(String(100), nullable=False)
    CustomerType = Column(String(20), nullable=False, default='Person')
    DateOfBirth  = Column(Date, nullable=True)
    Gender       = Column(String(10), nullable=True)
    StateCode    = Column(String(2), nullable=True)
    ZipCode      = Column(String(10), nullable=True)

    memberships       = relationship('AccountMember', back_populates='customer')
    health_risk_scores = relationship('HealthRiskScore', back_populates='customer',
                                      order_by='HealthRiskScore.ScoreDate.desc()')
    customer_contracts = relationship('CustomerContract', back_populates='customer')

    @property
    def latest_risk_score(self):
        return self.health_risk_scores[0] if self.health_risk_scores else None

    @property
    def age(self):
        if not self.DateOfBirth:
            return None
        today = date.today()
        dob = self.DateOfBirth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


class CustomerCustomer(Base):
    __tablename__ = 'CUSTOMER_CUSTOMER'
    CustomerID        = Column(String(20), ForeignKey('CUSTOMER.CustomerID'), primary_key=True)
    RelatedCustomerID = Column(String(20), ForeignKey('CUSTOMER.CustomerID'), primary_key=True)
    RelationshipType  = Column(String(30), nullable=False)


class CustomerAccount(Base):
    __tablename__ = 'CUSTOMER_ACCOUNT'
    CustomerID  = Column(String(20), ForeignKey('CUSTOMER.CustomerID'), primary_key=True)
    AccountID   = Column(String(20), primary_key=True)
    CompanyCode = Column(String(10), primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(['AccountID', 'CompanyCode'],
                             ['ACCOUNT.AccountID', 'ACCOUNT.CompanyCode']),
    )


class CustomerAssociate(Base):
    __tablename__ = 'CUSTOMER_ASSOCIATE'
    CustomerID  = Column(String(20), ForeignKey('CUSTOMER.CustomerID'), primary_key=True)
    AssociateID = Column(String(20), ForeignKey('ASSOCIATE.AssociateID'), primary_key=True)
    RoleType    = Column(String(30), nullable=False)


# ── CONTRACT DOMAIN ─────────────────────────────────────────

class Contract(Base):
    __tablename__ = 'CONTRACT'
    ContractID   = Column(String(20), primary_key=True)
    AccountID    = Column(String(20), nullable=False)
    CompanyCode  = Column(String(10), nullable=False)
    StartDate    = Column(Date, nullable=False)
    EndDate      = Column(Date, nullable=True)
    ContractType = Column(String(30), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(['AccountID', 'CompanyCode'],
                             ['ACCOUNT.AccountID', 'ACCOUNT.CompanyCode']),
    )

    account  = relationship('Account', back_populates='contracts')
    benefits = relationship('ContractBenefit', back_populates='contract')
    customer_contracts = relationship('CustomerContract', back_populates='contract')


class CustomerContract(Base):
    __tablename__ = 'CUSTOMER_CONTRACT'
    CustomerID = Column(String(20), ForeignKey('CUSTOMER.CustomerID'), primary_key=True)
    ContractID = Column(String(20), ForeignKey('CONTRACT.ContractID'), primary_key=True)
    RoleType   = Column(String(30), primary_key=True)

    customer = relationship('Customer', back_populates='customer_contracts')
    contract = relationship('Contract', back_populates='customer_contracts')


class ContractBenefit(Base):
    __tablename__ = 'CONTRACT_BENEFIT'
    BenefitID   = Column(String(20), primary_key=True)
    ContractID  = Column(String(20), ForeignKey('CONTRACT.ContractID'), nullable=False)
    AssociateID = Column(String(20), ForeignKey('ASSOCIATE.AssociateID'), nullable=False)
    BenefitType = Column(String(30), nullable=False)
    StartDate   = Column(Date, nullable=False)

    contract  = relationship('Contract', back_populates='benefits')
    premiums  = relationship('ContractPremium', back_populates='benefit')
    customer_benefits = relationship('CustomerBenefit', back_populates='benefit')

    @property
    def current_premium(self):
        return next((p for p in self.premiums if p.EndDate is None), None)


class CustomerBenefit(Base):
    __tablename__ = 'CUSTOMER_BENEFIT'
    CustomerID = Column(String(20), ForeignKey('CUSTOMER.CustomerID'), primary_key=True)
    BenefitID  = Column(String(20), ForeignKey('CONTRACT_BENEFIT.BenefitID'), primary_key=True)
    RoleType   = Column(String(30), primary_key=True)

    benefit = relationship('ContractBenefit', back_populates='customer_benefits')


class ContractPremium(Base):
    __tablename__ = 'CONTRACT_PREMIUM'
    PremiumID     = Column(String(20), primary_key=True)
    BenefitID     = Column(String(20), ForeignKey('CONTRACT_BENEFIT.BenefitID'), nullable=False)
    Amount        = Column(Numeric(10, 2), nullable=False)
    EffectiveDate = Column(Date, nullable=False)
    EndDate       = Column(Date, nullable=True)

    benefit = relationship('ContractBenefit', back_populates='premiums')


# ── EXTENSION TABLES ─────────────────────────────────────────

class DocumentMetadata(Base):
    __tablename__ = 'DOCUMENT_METADATA'
    DocumentID     = Column(String(20), primary_key=True)
    DocumentTitle  = Column(String(200), nullable=False)
    DocumentSource = Column(String(100), nullable=False)
    DocumentType   = Column(String(30), nullable=False)
    StorageURL     = Column(String(500), nullable=False)
    UploadDate     = Column(Date, nullable=False)
    StateCode      = Column(String(2), nullable=True)
    BenefitType    = Column(String(30), nullable=True)
    KeywordTags    = Column(Text, nullable=True)


class HealthRiskScore(Base):
    __tablename__ = 'HEALTH_RISK_SCORE'
    RiskScoreID     = Column(String(20), primary_key=True)
    CustomerID      = Column(String(20), ForeignKey('CUSTOMER.CustomerID'), nullable=False)
    ScoreDate       = Column(Date, nullable=False)
    DiabetesRisk    = Column(Numeric(5, 4), nullable=True)
    CardioRisk      = Column(Numeric(5, 4), nullable=True)
    ObesityRisk     = Column(Numeric(5, 4), nullable=True)
    RespiratoryRisk = Column(Numeric(5, 4), nullable=True)
    DataSourceRef   = Column(String(20), ForeignKey('DOCUMENT_METADATA.DocumentID'), nullable=True)
    ScoringModel    = Column(String(50), nullable=True)

    customer = relationship('Customer', back_populates='health_risk_scores')

    @property
    def is_stale(self):
        if not self.ScoreDate:
            return True
        return (date.today() - self.ScoreDate).days > Config.SCORE_STALE_DAYS
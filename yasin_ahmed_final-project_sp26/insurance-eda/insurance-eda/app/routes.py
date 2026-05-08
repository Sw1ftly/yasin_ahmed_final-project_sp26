import uuid
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session as flask_session
from sqlalchemy.orm import joinedload

from db.session import Session
from app.models import (Customer, Account, AccountMember, Contract, ContractBenefit,
                         ContractPremium, CustomerContract, CustomerBenefit, HealthRiskScore)
from app.forms import QuoteForm, AcceptQuoteForm
from ml.risk_scorer import get_or_refresh_score
from config import Config

main = Blueprint('main', __name__)


@main.route('/')
def index():
    db = Session()
    customers = db.query(Customer).limit(10).all()
    accounts  = db.query(Account).limit(10).all()
    return render_template('index.html', customers=customers, accounts=accounts)


@main.route('/quote', methods=['GET', 'POST'])
def quote():
    form = QuoteForm()
    if form.validate_on_submit():
        db = Session()
        try:
            # ── Step 1: lookup or create customer ──────────────────
            cid = form.customer_id.data.strip() if form.customer_id.data else ''
            if cid:
                customer = db.query(Customer).options(
                    joinedload(Customer.health_risk_scores)
                ).filter_by(CustomerID=cid).first()
                if not customer:
                    flash(f'Customer ID {cid} not found. Creating new record.', 'warning')
                    customer = None
            else:
                customer = None

            if not customer:
                if not form.name.data:
                    flash('Please enter a name for the new customer.', 'danger')
                    return render_template('quote.html', form=form)
                customer = Customer(
                    CustomerID   = 'C-' + str(uuid.uuid4())[:8].upper(),
                    Name         = form.name.data,
                    CustomerType = 'Person',
                    DateOfBirth  = form.dob.data,
                    Gender       = form.gender.data or None,
                    StateCode    = form.state_code.data or None,
                    ZipCode      = form.zip_code.data or None,
                )
                db.add(customer)
                db.flush()

            # ── Step 2: verify account exists ──────────────────────
            account = db.query(Account).filter_by(
                AccountID=form.account_id.data,
                CompanyCode=form.company_code.data
            ).first()
            if not account:
                flash('Account not found. Check Account ID and Company Code.', 'danger')
                return render_template('quote.html', form=form)

            # ── Step 3: get/refresh risk score ─────────────────────
            score = get_or_refresh_score(customer, db)

            # ── Step 4: calculate adjusted premium ────────────────
            base   = Config.BASE_PREMIUM
            surcharge = 0.0
            flags  = []
            if score.DiabetesRisk and float(score.DiabetesRisk) > Config.DIABETES_THRESHOLD:
                surcharge += Config.DIABETES_SURCHARGE
                flags.append(('Diabetes', float(score.DiabetesRisk)))
            if score.CardioRisk and float(score.CardioRisk) > Config.CARDIO_THRESHOLD:
                surcharge += Config.CARDIO_SURCHARGE
                flags.append(('Cardiovascular', float(score.CardioRisk)))
            if score.ObesityRisk and float(score.ObesityRisk) > Config.OBESITY_THRESHOLD:
                surcharge += Config.OBESITY_SURCHARGE
                flags.append(('Obesity', float(score.ObesityRisk)))
            if score.RespiratoryRisk and float(score.RespiratoryRisk) > Config.RESP_THRESHOLD:
                surcharge += Config.RESP_SURCHARGE
                flags.append(('Respiratory', float(score.RespiratoryRisk)))
            surcharge = min(surcharge, Config.MAX_SURCHARGE)
            final_premium = round(base * (1 + surcharge), 2)

            db.commit()

            # ── Step 5: render result ──────────────────────────────
            accept_form = AcceptQuoteForm(
                customer_id  = customer.CustomerID,
                account_id   = form.account_id.data,
                company_code = form.company_code.data,
                benefit_type = form.benefit_type.data,
                premium      = final_premium,
            )
            return render_template('result.html',
                customer=customer,
                account=account,
                score=score,
                base=base,
                surcharge=surcharge,
                flags=flags,
                final_premium=final_premium,
                benefit_type=form.benefit_type.data,
                form=accept_form,
            )
        except Exception as e:
            db.rollback()
            flash(f'Error generating quote: {str(e)}', 'danger')
    return render_template('quote.html', form=form)


@main.route('/issue', methods=['POST'])
def issue():
    form = AcceptQuoteForm()
    if not form.validate_on_submit():
        flash('Invalid form submission.', 'danger')
        return redirect(url_for('main.quote'))

    db = Session()
    try:
        cid          = form.customer_id.data
        account_id   = form.account_id.data
        company_code = form.company_code.data
        benefit_type = form.benefit_type.data
        premium_amt  = float(form.premium.data)

        customer = db.query(Customer).filter_by(CustomerID=cid).first()
        account  = db.query(Account).filter_by(AccountID=account_id,
                                                CompanyCode=company_code).first()
        if not customer or not account:
            flash('Customer or account not found.', 'danger')
            return redirect(url_for('main.quote'))

        today = date.today()
        contract_id = 'CON-' + str(uuid.uuid4())[:8].upper()
        benefit_id  = 'BEN-' + str(uuid.uuid4())[:8].upper()
        premium_id  = 'PRM-' + str(uuid.uuid4())[:8].upper()

        # Use default associate for seeded data
        associate_id = 'ASC-001'

        contract = Contract(
            ContractID   = contract_id,
            AccountID    = account_id,
            CompanyCode  = company_code,
            StartDate    = today,
            EndDate      = None,
            ContractType = benefit_type,
        )
        db.add(contract)

        benefit = ContractBenefit(
            BenefitID   = benefit_id,
            ContractID  = contract_id,
            AssociateID = associate_id,
            BenefitType = benefit_type,
            StartDate   = today,
        )
        db.add(benefit)

        premium = ContractPremium(
            PremiumID     = premium_id,
            BenefitID     = benefit_id,
            Amount        = premium_amt,
            EffectiveDate = today,
            EndDate       = None,
        )
        db.add(premium)

        cust_contract = CustomerContract(
            CustomerID = cid,
            ContractID = contract_id,
            RoleType   = 'Owner',
        )
        db.add(cust_contract)

        cust_benefit = CustomerBenefit(
            CustomerID = cid,
            BenefitID  = benefit_id,
            RoleType   = 'Insured',
        )
        db.add(cust_benefit)

        db.commit()
        flash('Policy issued successfully!', 'success')
        return render_template('issued.html',
            customer=customer,
            contract=contract,
            benefit=benefit,
            premium=premium,
        )
    except Exception as e:
        db.rollback()
        flash(f'Error issuing policy: {str(e)}', 'danger')
        return redirect(url_for('main.quote'))

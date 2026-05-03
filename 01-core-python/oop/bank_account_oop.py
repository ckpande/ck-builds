# bank_account_oop.py
# Chandrakant Pande - ckpande

from abc import ABC, abstractmethod
from datetime import datetime


class BankAccount(ABC):
    _total_accounts = 0

    def __init__(self, account_number, holder, balance=0.0):
        self._account_number = account_number
        self._holder = holder
        self.__balance = balance
        self._opened_on = datetime.now().strftime("%Y-%m-%d")
        BankAccount._total_accounts += 1

    @property
    def balance(self):
        return self.__balance

    @property
    def account_number(self):
        return self._account_number

    @property
    def holder(self):
        return self._holder

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.__balance += amount
        print(f"  [{self._account_number}] Deposited ₹{amount:,.2f} | Balance: ₹{self.__balance:,.2f}")

    def _deduct(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self.__balance:
            raise ValueError(f"Insufficient funds - available: ₹{self.__balance:,.2f}")
        self.__balance -= amount

    @abstractmethod
    def withdraw(self, amount):
        pass

    @abstractmethod
    def account_type(self):
        pass

    @abstractmethod
    def annual_summary(self):
        pass

    @classmethod
    def open_zero_balance(cls, account_number, holder):
        return cls(account_number, holder, 0.0)

    @staticmethod
    def validate_ifsc(ifsc_code):
        import re
        return bool(re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', ifsc_code))

    @staticmethod
    def total_accounts_opened():
        return BankAccount._total_accounts

    def __str__(self):
        return (f"{self.account_type():20s} | {self._account_number} | "
                f"{self._holder:15s} | ₹{self.balance:>12,.2f} | Opened: {self._opened_on}")

    def __repr__(self):
        return f"{self.__class__.__name__}('{self._account_number}', '{self._holder}', {self.balance})"

    def __eq__(self, other):
        if not isinstance(other, BankAccount):
            return NotImplemented
        return self._account_number == other._account_number

    def __lt__(self, other):
        if not isinstance(other, BankAccount):
            return NotImplemented
        return self.balance < other.balance


class SavingsAccount(BankAccount):
    MINIMUM_BALANCE = 1000.0

    def __init__(self, account_number, holder, balance=0.0, interest_rate=0.04):
        super().__init__(account_number, holder, balance)
        self.__interest_rate = interest_rate

    def withdraw(self, amount):
        if (self.balance - amount) < SavingsAccount.MINIMUM_BALANCE:
            raise ValueError(f"Minimum balance ₹{SavingsAccount.MINIMUM_BALANCE:,.2f} required")
        self._deduct(amount)
        print(f"  [{self._account_number}] Withdrawn ₹{amount:,.2f} | Balance: ₹{self.balance:,.2f}")

    def apply_quarterly_interest(self):
        interest = round(self.balance * (self.__interest_rate / 4), 2)
        self.deposit(interest)
        print(f"  [{self._account_number}] Quarterly interest @ {self.__interest_rate * 100:.1f}%: ₹{interest:,.2f}")

    def account_type(self):
        return "Savings Account"

    def annual_summary(self):
        return {
            "account": self._account_number,
            "type": self.account_type(),
            "holder": self._holder,
            "closing_balance": self.balance,
            "interest_rate_pa": f"{self.__interest_rate * 100:.1f}%"
        }


class LoanAccount(BankAccount):
    def __init__(self, account_number, holder, principal, annual_rate, tenure_months):
        super().__init__(account_number, holder, principal)
        self.__annual_rate = annual_rate
        self.__tenure = tenure_months
        self.__emi = self._calculate_emi(principal, annual_rate, tenure_months)
        self.__months_paid = 0

    @staticmethod
    def _calculate_emi(principal, annual_rate, tenure_months):
        r = annual_rate / (12 * 100)
        n = tenure_months
        if r == 0:
            return round(principal / n, 2)
        return round(principal * r * (1 + r) ** n / ((1 + r) ** n - 1), 2)

    def pay_emi(self):
        if self.balance <= 0:
            raise ValueError("Loan already fully repaid")
        payment = min(self.__emi, self.balance)
        self._deduct(payment)
        self.__months_paid += 1
        print(f"  [{self._account_number}] EMI paid ₹{payment:,.2f} | Outstanding: ₹{self.balance:,.2f} "
              f"| Month: {self.__months_paid}/{self.__tenure}")

    def withdraw(self, amount):
        self._deduct(amount)
        print(f"  [{self._account_number}] Disbursed ₹{amount:,.2f} | Remaining: ₹{self.balance:,.2f}")

    @property
    def emi(self):
        return self.__emi

    @property
    def months_remaining(self):
        return self.__tenure - self.__months_paid

    def account_type(self):
        return "Loan Account"

    def annual_summary(self):
        return {
            "account": self._account_number,
            "type": self.account_type(),
            "holder": self._holder,
            "outstanding_principal": self.balance,
            "monthly_emi": self.__emi,
            "months_remaining": self.months_remaining,
            "annual_rate": f"{self.__annual_rate}%"
        }


class FixedDeposit(BankAccount):
    PENALTY_RATE = 0.01

    def __init__(self, account_number, holder, principal, rate, tenure_days):
        super().__init__(account_number, holder, principal)
        self.__rate = rate
        self.__tenure_days = tenure_days
        self.__maturity_amount = round(principal * (1 + rate * tenure_days / 365), 2)
        self.__is_matured = False

    def mature(self):
        self.__is_matured = True
        bonus = self.__maturity_amount - self.balance
        self.deposit(bonus)
        print(f"  [{self._account_number}] FD matured - interest ₹{bonus:,.2f} credited")

    def withdraw(self, amount):
        if not self.__is_matured:
            penalty = round(amount * FixedDeposit.PENALTY_RATE, 2)
            self._deduct(amount + penalty)
            print(f"  [{self._account_number}] Premature withdrawal ₹{amount:,.2f} "
                  f"| Penalty ₹{penalty:,.2f} | Balance: ₹{self.balance:,.2f}")
        else:
            self._deduct(amount)
            print(f"  [{self._account_number}] FD withdrawal ₹{amount:,.2f} | Balance: ₹{self.balance:,.2f}")

    @property
    def maturity_amount(self):
        return self.__maturity_amount

    def account_type(self):
        return "Fixed Deposit"

    def annual_summary(self):
        return {
            "account": self._account_number,
            "type": self.account_type(),
            "holder": self._holder,
            "current_balance": self.balance,
            "maturity_amount": self.__maturity_amount,
            "rate": f"{self.__rate * 100:.1f}%",
            "tenure_days": self.__tenure_days
        }


class AuditMixin:
    def __init__(self):
        self._audit_log = []

    def _record(self, action, amount):
        self._audit_log.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "amount": amount
        })

    def print_statement(self):
        print(f"\n  Statement - {self._account_number}:")
        print(f"  {'Timestamp':<22} {'Action':<12} {'Amount':>14}")
        print(f"  {'-' * 52}")
        for entry in self._audit_log:
            print(f"  {entry['timestamp']:<22} {entry['action']:<12} ₹{entry['amount']:>12,.2f}")


class AuditedSavings(AuditMixin, SavingsAccount):
    def __init__(self, account_number, holder, balance=0.0):
        SavingsAccount.__init__(self, account_number, holder, balance)
        AuditMixin.__init__(self)

    def deposit(self, amount):
        super().deposit(amount)
        self._record("CREDIT", amount)

    def withdraw(self, amount):
        super().withdraw(amount)
        self._record("DEBIT", amount)


if __name__ == "__main__":
    print("=" * 65)
    print("SAVINGS ACCOUNT")
    print("=" * 65)
    sav = SavingsAccount("SB-001", "Chandrakant Pande", 50000.0, 0.06)
    print(sav)
    sav.deposit(10000)
    sav.withdraw(5000)
    sav.apply_quarterly_interest()
    print(f"\n  Annual Summary: {sav.annual_summary()}")

    print("\n" + "=" * 65)
    print("LOAN ACCOUNT - HOME LOAN")
    print("=" * 65)
    loan = LoanAccount("HL-001", "Chandrakant Pande", 2500000.0, 8.5, 240)
    print(loan)
    print(f"  Monthly EMI: ₹{loan.emi:,.2f}")
    for _ in range(3):
        loan.pay_emi()
    print(f"\n  Annual Summary: {loan.annual_summary()}")

    print("\n" + "=" * 65)
    print("FIXED DEPOSIT")
    print("=" * 65)
    fd = FixedDeposit("FD-001", "Chandrakant Pande", 100000.0, 0.072, 365)
    print(fd)
    print(f"  Maturity amount: ₹{fd.maturity_amount:,.2f}")
    fd.withdraw(10000)
    fd.mature()
    fd.withdraw(30000)

    print("\n" + "=" * 65)
    print("AUDITED SAVINGS - TRANSACTION STATEMENT")
    print("=" * 65)
    aud = AuditedSavings("SB-002", "Jayant Raut", 25000.0)
    aud.deposit(5000)
    aud.deposit(8000)
    aud.withdraw(3000)
    aud.print_statement()

    print("\n" + "=" * 65)
    print("PORTFOLIO SORT BY BALANCE (uses __lt__)")
    print("=" * 65)
    portfolio = [sav, loan, fd, aud]
    for acc in sorted(portfolio):
        print(f"  {acc}")

    print("\n" + "=" * 65)
    print("CLASS-LEVEL STATS")
    print("=" * 65)
    print(f"  Total accounts: {BankAccount.total_accounts_opened()}")
    print(f"  IFSC valid: {BankAccount.validate_ifsc('HDFC0001234')}")
    print(f"  IFSC invalid: {BankAccount.validate_ifsc('HDFC1001234')}")

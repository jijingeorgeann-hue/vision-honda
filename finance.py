class FinanceCalculator:

    def calculate_emi(
        self,
        on_road_price,
        down_payment,
        annual_interest,
        tenure_months
    ):

        price = float(on_road_price)
        down = float(down_payment)
        annual_rate = float(annual_interest)
        months = int(tenure_months)

        if price <= 0:
            raise ValueError("Enter valid vehicle price")

        if down < 0 or down >= price:
            raise ValueError("Invalid down payment")

        if annual_rate < 0:
            raise ValueError("Interest cannot be negative")

        if months <= 0:
            raise ValueError("Invalid loan tenure")

        loan_amount = price - down

        monthly_rate = annual_rate / 12 / 100

        if monthly_rate == 0:
            emi = loan_amount / months
        else:
            factor = (1 + monthly_rate) ** months

            emi = (
                loan_amount
                * monthly_rate
                * factor
                / (factor - 1)
            )

        total_payment = emi * months
        total_interest = total_payment - loan_amount

        return {
            "on_road_price": round(price, 2),
            "down_payment": round(down, 2),
            "loan_amount": round(loan_amount, 2),
            "interest_rate": annual_rate,
            "tenure_months": months,
            "monthly_emi": round(emi, 2),
            "total_interest": round(total_interest, 2),
            "total_repayment": round(total_payment, 2),
            "total_customer_payment": round(
                down + total_payment, 2
            )
        }

    def calculate_multiple(
        self,
        on_road_price,
        down_payment,
        interest_rates,
        tenure_months
    ):

        results = []

        for rate in interest_rates:

            result = self.calculate_emi(
                on_road_price,
                down_payment,
                rate,
                tenure_months
            )

            results.append(result)

        return results
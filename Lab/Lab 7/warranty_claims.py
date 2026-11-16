import math


PLANS = {"basic", "standard", "premium"}


def parse_claim(text):
    if not isinstance(text, str) or text.count(":") != 1:
        return None
    plan, months = (part.strip() for part in text.split(":"))
    if plan.lower() not in PLANS:
        return None
    try:
        age = float(months)
    except (ValueError, OverflowError):
        return None
    if not math.isfinite(age) or age < 0:
        return None
    return plan.title(), age


def age_average(ages_csv):
    if not isinstance(ages_csv, str) or not ages_csv.strip():
        return None
    try:
        values = [int(part.strip()) for part in ages_csv.split(",")]
    except (ValueError, OverflowError):
        return None
    if any(value < 0 for value in values):
        return None
    return sum(values) // len(values)


def payable_charge(text):
    if not isinstance(text, str) or text.count("|") != 1:
        return None
    try:
        charge, discount = (float(part.strip()) for part in text.split("|"))
    except (ValueError, OverflowError):
        return None
    if not all(math.isfinite(value) and value >= 0 for value in (charge, discount)):
        return None
    total = charge * 1.18 - discount
    if not math.isfinite(total):
        return None
    return max(total, 0.0)


def main():
    steps = [
        ("parse_claim", "Enter plan:age in months (e.g. standard:30): ",
         parse_claim, "Plan and Age:"),
        ("age_average", "Enter product ages as CSV (e.g. 12,24,36): ",
         age_average, "Average Age:"),
        ("payable_charge", "Enter charge|discount (e.g. 1500|200): ",
         payable_charge, "Payable Charge:"),
    ]
    for name, prompt, function, label in steps:
        print("==== Running", name, "====")
        try:
            result = function(input(prompt))
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled.")
            return
        if result is None:
            print("Invalid input. Please check the format and nonnegative values.")
        else:
            print(label, result)
        print()


if __name__ == "__main__":
    main()

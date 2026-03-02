import sys
from normalize import normalize_merchant
from user_rules import upsert_rule


def main():
    if len(sys.argv) < 3:
        print("Usage: python learn_rule.py <merchant_name> <category>")
        sys.exit(1)

    merchant = sys.argv[1].strip()
    category = sys.argv[2].strip()
    norm = normalize_merchant(merchant)
    path = upsert_rule(norm, category)
    print(f"saved rule: {norm} -> {category}")
    print(f"rules file: {path}")


if __name__ == "__main__":
    main()

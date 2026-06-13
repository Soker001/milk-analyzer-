import sys
import json

def calculate_price(data):
    try:
        state = data.get('state', '').strip()
        fat = float(data.get('fat', 0))
        snf = float(data.get('snf', 0))
        quantity = float(data.get('quantity', 0))
        quality_score = float(data.get('quality_score', 100))

        base_price_per_litre = 0

        # State-wise formulas
        if state == "Tamil Nadu":
            base_price_per_litre = (fat * 7) + (snf * 3)
        elif state == "Kerala":
            base_price_per_litre = (fat * 6.8) + (snf * 3.2)
        elif state == "Karnataka":
            base_price = 30 # Base price assumption
            fat_incentive = (fat - 3.5) * 2 if fat > 3.5 else 0
            subsidy = 5
            base_price_per_litre = base_price + fat_incentive + subsidy
        elif state == "Gujarat":
            base_price_per_litre = (fat * 6.5) + (snf * 4)
        elif state == "Maharashtra":
            base_price_per_litre = fat * 8
        elif state == "Punjab":
            base_price_per_litre = (fat * 7.5) + (snf * 2.5)
        elif state == "Haryana":
            base_price_per_litre = (fat * 7.2) + (snf * 2.8)
        else:
            # Default fallback formula
            base_price_per_litre = (fat * 6.5) + (snf * 3)

        # Apply Quality Score impact
        # If score is 100, they get 100% of the price.
        # If score is 50, they get 50% of the price.
        final_price_per_litre = base_price_per_litre * (quality_score / 100.0)
        
        total_payment = final_price_per_litre * quantity

        result = {
            "success": True,
            "state": state,
            "base_price_per_litre": round(base_price_per_litre, 2),
            "final_price_per_litre": round(final_price_per_litre, 2),
            "quality_score": quality_score,
            "quantity": quantity,
            "total_payment": round(total_payment, 2)
        }
        return result

    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Read JSON input from standard input
    try:
        input_data = sys.stdin.read()
        data = json.loads(input_data)
        result = calculate_price(data)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))

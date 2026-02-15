import operator
from typing import Callable, Any

class RulesEngine:
    """
    Deterministic Eligibility Engine.
    Evaluates structured JSON rules against user profile data.
    """
    
    OPERATORS: dict[str, Callable[[Any, Any], bool]] = {
        "eq": operator.eq,
        "ne": operator.ne,
        "lt": operator.lt,
        "lte": operator.le,
        "gt": operator.gt,
        "gte": operator.ge,
        "in": lambda a, b: a in b if isinstance(b, list) else a == b,
        "contains": lambda a, b: b in a if isinstance(a, str) else False
    }

    def evaluate(self, user_profile, rules):
        """
        Evaluates a set of rules against a user profile.
        Returns (eligible, breakdown, matching_score)
        """
        if not rules or 'mandatory' not in rules:
            return True, ["No specific rules defined for this version."], 1.0

        breakdown = []
        is_eligible = True
        matched_count = 0
        total_mandatory = len(rules.get('mandatory', []))

        for rule in rules.get('mandatory', []):
            field = rule.get('field')
            op_name = rule.get('operator')
            target_value = rule.get('value')
            label = rule.get('label', field)

            user_value = user_profile.get(field)
            
            # Basic type conversion for numbers if needed
            if isinstance(target_value, (int, float)) and isinstance(user_value, str):
                try:
                    user_value = float(user_value.replace(',', '').split()[0])
                except (ValueError, IndexError):
                    pass

            op_func = self.OPERATORS.get(op_name)
            if not op_func:
                breakdown.append(f"⚠️ Unknown operator: {op_name}")
                continue

            try:
                # Type safe check
                is_numeric = isinstance(target_value, (int, float))
                if is_numeric and user_value is not None:
                    try:
                        match = op_func(float(str(user_value).replace(',', '').split()[0]), float(target_value))
                    except (ValueError, IndexError):
                        match = op_func(user_value, target_value)
                else:
                    match = op_func(user_value, target_value)
                    
                if match:
                    breakdown.append(f"✅ {label}: Matches")
                    matched_count += 1
                else:
                    breakdown.append(f"❌ {label}: Failed (User: {user_value}, Req: {target_value})")
                    is_eligible = False
            except Exception as e:
                breakdown.append(f"⚠️ Error evaluating {label}: {str(e)}")
                is_eligible = False

        # Calculate matching score (0.0 to 1.0)
        score = matched_count / total_mandatory if total_mandatory > 0 else 1.0
        
        return is_eligible, breakdown, score

    def generate_explainability(self, results):
        """
        Converts breakdown results into a clean human summary.
        """
        eligible, breakdown, score = results
        status = "Verified Eligible 🛡️" if eligible else "Potentially Ineligible ⚠️"
        summary = f"### Eligibility Audit\n**Status**: {status} (Score: {int(score*100)}%)\n\n"
        summary += "\n".join(breakdown)
        return summary

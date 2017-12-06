import ast
from functools import reduce


def _string_formatter(input_string):
    if isinstance(input_string, str):
        return '"{input_string}"'.format(input_string=input_string)


def process_condition(instance, condition):
    lhs = reduce(getattr, condition["property"].split('.'), instance)
    rhs = ast.literal_eval(condition["value"])
    if isinstance(rhs, dict) and "property" in rhs:
        rhs = getattr(instance, rhs["property"], None)
    lhs = _string_formatter(lhs)
    rhs = _string_formatter(rhs)
    return bool(eval(" ".join([str(lhs), condition["operator"], str(rhs)])))


def conditions_evaluator(instance, conditions):
    if conditions is None:
        return True
    condition_literals = [[True]]
    for and_conditions in conditions:
        condition_literals.append([])
        for or_condition in and_conditions:
            condition_literals[-1].append(process_condition(instance, or_condition))
    return all([any(or_conditions) for or_conditions in condition_literals])

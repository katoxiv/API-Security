from flask import Blueprint, request, jsonify
from myapp import limiter
from sympy import SympifyError
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from flask_login import login_required, current_user
import sympy
import re
import os

calculate_bp = Blueprint('calculate', __name__)

ALLOWED_FUNCTIONS = {"sqrt", "sin", "cos", "tan", "log", "exp", "asin", "acos", "atan", "factorial"}
CALCULATE_LIMIT = os.environ.get('CALCULATE_LIMIT') or "100/hour"
transformations = (standard_transformations + (implicit_multiplication_application,))

def evaluate_expression(expression):
    try:
        sympy_expression = parse_expr(expression, transformations=transformations)
        result = sympy_expression.evalf()

        # Format the result in scientific notation if it's too small or too large
        if isinstance(result, (float, complex)) and (result > 1e5 or (0 < result < 1e-2)):
            result = "{:.2e}".format(result)  # use scientific notation with 2 decimal places
        elif isinstance(result, (sympy.Float, sympy.Integer, float, int, complex)):
            result = round(float(result), 2)  # convert sympy Float to Python float and round off to 2 decimal places
        return True, result
    
    except (SympifyError, ZeroDivisionError, ValueError, OverflowError) as e:
        return False, str(e)
    
    except Exception as e:
        return False, 'An unexpected error occurred: ' + str(e)


@limiter.limit(CALCULATE_LIMIT)
@calculate_bp.route("/calculate", methods=["POST"])
@login_required
def perform_calculation():
    expression = request.json.get("expression", "")

    if not expression:
        return jsonify({'error': 'Expression is required'}), 400
    
    if len(expression) > 1000:
        return jsonify({'error': 'Expression is too long'}), 400
    
    # Expression content validation
    if not re.match("^[0-9a-zA-Z.,()/*+\-^ ]+$", expression):
        return jsonify({'error': 'Invalid expression'}), 400

    success, result = evaluate_expression(expression)
    if success:
        return jsonify({'result': result, 'username': current_user.username}), 200
    else:
        return jsonify({'error': result}), 400

@calculate_bp.app_errorhandler(500)
def handle_error(e):
    return jsonify({'error': 'An unexpected error occurred'}), 500

@calculate_bp.app_errorhandler(400)
def handle_bad_request(e):
    return jsonify({'error': 'Bad request'}), 400

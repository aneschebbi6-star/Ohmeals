"""
Accounting controller - REST API for accounting module.
Prefix: /api/accounting
"""
import csv
import io
from datetime import date, datetime, timedelta

from flask import Blueprint, jsonify, request, make_response
from flask_login import login_required

from app.extensions import db
from app.models.expense import Expense, EXPENSE_CATEGORIES
from app.services.accounting_service import (
    get_financial_summary,
    get_revenue_chart_data,
    get_expenses_by_category,
    get_expenses_list,
    get_transactions_list,
    get_export_data,
    create_expense,
    update_expense,
    delete_expense
)

accounting_bp = Blueprint('accounting', __name__, url_prefix='/api/accounting')


# ============================================
# FINANCIAL SUMMARY
# ============================================

@accounting_bp.route('/summary', methods=['GET'])
@login_required
def summary():
    """Get financial summary for a period (today, week, month)."""
    period = request.args.get('period', 'month')
    if period not in ('today', 'week', 'month'):
        period = 'month'

    data = get_financial_summary(period)
    return jsonify(data)


# ============================================
# CHARTS
# ============================================

@accounting_bp.route('/revenue-chart', methods=['GET'])
@login_required
def revenue_chart():
    """Get revenue chart data."""
    start = request.args.get('start')
    end = request.args.get('end')
    granularity = request.args.get('granularity', 'daily')

    today = date.today()
    if start:
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
    else:
        start_date = today.replace(day=1)

    if end:
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
    else:
        end_date = today

    data = get_revenue_chart_data(start_date, end_date, granularity)
    return jsonify(data)


@accounting_bp.route('/expenses-chart', methods=['GET'])
@login_required
def expenses_chart():
    """Get expenses by category for pie chart."""
    start = request.args.get('start')
    end = request.args.get('end')

    today = date.today()
    if start:
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
    else:
        start_date = today.replace(day=1)

    if end:
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
    else:
        end_date = today

    data = get_expenses_by_category(start_date, end_date)
    return jsonify(data)


# ============================================
# EXPENSE CRUD
# ============================================

@accounting_bp.route('/expenses', methods=['GET'])
@login_required
def list_expenses():
    """List expenses with optional date filter and pagination."""
    start = request.args.get('start')
    end = request.args.get('end')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    start_date = datetime.strptime(start, '%Y-%m-%d').date() if start else None
    end_date = datetime.strptime(end, '%Y-%m-%d').date() if end else None

    data = get_expenses_list(start_date, end_date, page, per_page)
    return jsonify(data)


@accounting_bp.route('/transactions', methods=['GET'])
@login_required
def list_transactions():
    """List merged transactions (Orders + Expenses)."""
    period = request.args.get('period', 'month')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    today = date.today()
    if period == 'today':
        start_date = today
        end_date = today
    elif period == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    else:  # month
        start_date = today.replace(day=1)
        end_date = today

    data = get_transactions_list(start_date, end_date, page, per_page)
    return jsonify(data)


@accounting_bp.route('/expenses', methods=['POST'])
@login_required
def add_expense_route():
    """Create a new expense."""
    data = request.get_json()
    try:
        expense = create_expense(data)
        return jsonify(expense.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@accounting_bp.route('/expenses/<int:id>', methods=['PUT'])
@login_required
def update_expense_route(id):
    """Update an existing expense."""
    data = request.get_json()
    try:
        expense = update_expense(id, data)
        return jsonify(expense.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@accounting_bp.route('/expenses/<int:id>', methods=['DELETE'])
@login_required
def delete_expense_route(id):
    """Delete an expense."""
    delete_expense(id)
    return jsonify({'message': 'Dépense supprimée'}), 200


# ============================================
# CATEGORIES
# ============================================

@accounting_bp.route('/categories', methods=['GET'])
@login_required
def get_categories():
    """Get list of available expense categories."""
    labels = {
        'ingredients': 'Ingrédients',
        'salaires': 'Salaires',
        'loyer': 'Loyer',
        'equipement': 'Équipement',
        'marketing': 'Marketing',
        'livraison': 'Livraison',
        'autre': 'Autre'
    }
    return jsonify([{'id': c, 'label': labels.get(c, c)} for c in EXPENSE_CATEGORIES])


# ============================================
# CSV EXPORT
# ============================================

@accounting_bp.route('/export', methods=['GET'])
@login_required
def export_csv():
    """Export financial data as CSV."""
    start = request.args.get('start')
    end = request.args.get('end')

    today = date.today()
    start_date = datetime.strptime(start, '%Y-%m-%d').date() if start else today.replace(day=1)
    end_date = datetime.strptime(end, '%Y-%m-%d').date() if end else today

    rows = get_export_data(start_date, end_date)

    # Build CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['type', 'date', 'description', 'category', 'amount'])
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=comptabilite_{start_date}_{end_date}.csv'
    return response

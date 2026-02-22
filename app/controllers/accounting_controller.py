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
    get_export_data
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
def add_expense():
    """Create a new expense."""
    data = request.get_json()

    if not data.get('title') or not data.get('amount') or not data.get('category'):
        return jsonify({'error': 'Titre, montant et catégorie sont requis'}), 400

    if data['category'] not in EXPENSE_CATEGORIES:
        return jsonify({'error': f'Catégorie invalide. Choix: {", ".join(EXPENSE_CATEGORIES)}'}), 400

    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Le montant doit être positif'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Montant invalide'}), 400

    expense_date = date.today()
    if data.get('date'):
        try:
            expense_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Format de date invalide (YYYY-MM-DD)'}), 400

    expense = Expense(
        title=data['title'].strip(),
        category=data['category'],
        amount=amount,
        date=expense_date,
        notes=data.get('notes', '').strip() or None
    )

    db.session.add(expense)
    db.session.commit()

    return jsonify(expense.to_dict()), 201


@accounting_bp.route('/expenses/<int:id>', methods=['PUT'])
@login_required
def update_expense(id):
    """Update an existing expense."""
    expense = Expense.query.get_or_404(id)
    data = request.get_json()

    if data.get('title'):
        expense.title = data['title'].strip()

    if data.get('category'):
        if data['category'] not in EXPENSE_CATEGORIES:
            return jsonify({'error': 'Catégorie invalide'}), 400
        expense.category = data['category']

    if data.get('amount') is not None:
        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({'error': 'Le montant doit être positif'}), 400
            expense.amount = amount
        except (ValueError, TypeError):
            return jsonify({'error': 'Montant invalide'}), 400

    if data.get('date'):
        try:
            expense.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Format de date invalide'}), 400

    if 'notes' in data:
        expense.notes = data['notes'].strip() or None

    db.session.commit()
    return jsonify(expense.to_dict())


@accounting_bp.route('/expenses/<int:id>', methods=['DELETE'])
@login_required
def delete_expense(id):
    """Delete an expense."""
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return jsonify({'message': 'Dépense supprimée'})


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
